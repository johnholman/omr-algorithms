from abc import ABC, abstractmethod


class Controller(ABC):

    def __init__(self, dt, rgen, bout_generator, **_cfg):
        self.dt = dt
        self.rgen = rgen  # random number generator
        self.bg = bout_generator
        self.m = 0.0
        self.is_swimming = False  # whether swimming

    def configure(self, **cfg):
        self.bg.configure(**cfg)

    def act(self, sensed_flow):
        self.m = self.calc_motor_drive(sensed_flow)
        motor_command = self.bg.select_action(self.m)

        return motor_command

    @abstractmethod
    def calc_motor_drive(self, sensed_flow):
        pass

    def record(self, rec):
        # save variables for recording
        self.bg.record(rec)


class PIController(Controller):
    """ Basic PI controller
    """

    def __init__(self, ierr_init=0, **cfg):
        super().__init__(**cfg)
        self.ierr_init = ierr_init
        self.ierr = self.ierr_init  # accumulated integral of optic flow error
        self.u = None  # flow processing output
        self.Ki = None
        self.Kp = None
        self.tau = None

    def configure(self, Ki, Kp, tau=None, ierr_init=None, **cfg):
        super().configure(**cfg)
        self.Ki = Ki  # integral gain
        self.Kp = Kp  # proportional gain
        self.tau = tau  # integral leak time constant
        if ierr_init is not None:
            self.ierr = ierr_init  # fix integral error at start of phase

    def calc_motor_drive(self, sensed_flow):
        if self.tau is None or self.tau < 0:
            # non-leaky integration required
            self.ierr += sensed_flow * self.dt
        elif self.tau > self.dt:
            # leaky integration with time constant zero
            self.ierr += self.dt * (sensed_flow - self.ierr / self.tau)
        else:
            # pass-through - equivalent to "proportional control" with Ki as the gain
            self.ierr = sensed_flow

        self.u = self.Ki * self.ierr + self.Kp * sensed_flow

        return self.u

    def record(self, rec):
        super().record(rec)
        rec['motor_drive'] = self.u
        rec['integrated_flow'] = self.u
        rec['integral_error'] = self.ierr
        rec['Ki'] = self.Ki
        rec['Kp'] = self.Kp
        rec['tau'] = self.tau

    def __str__(self):
        s = (f'  {type(self).__name__}: '
             f'Ki {self.Ki:.2f} '
             f'Kp {self.Kp:.2f} ')
        if self.tau is not None:
            s += f'tau {self.tau:.2f} '
        s += f'\n  {self.bg}'

        return s


class DualControllerSpecifiedIntensity(PIController):
    def __init__(self, **cfg):
        super().__init__(**cfg)
        self.ibs = None
        self.u_intensity = None
        self.u_rate = None

    def configure(self, ibs, ibs_to_scale, **cfg):
        super().configure(**cfg)
        self.ibs = ibs  # required initial bout speed
        self.u_intensity = ibs_to_scale * ibs

    def calc_motor_drive(self, sensed_flow):
        self.u_rate = super().calc_motor_drive(sensed_flow)
        return self.u_rate, self.u_intensity

    def record(self, rec):
        super().record(rec)
        rec['u_rate'] = self.u_rate
        rec['u_intensity'] = self.u_intensity

    def __str__(self):
        s = (f'  {type(self).__name__}: '
             f'Ki {self.Ki:.2f} '
             f'Kp {self.Kp:.2f} '
             f'initial bout speed {self.ibs}')
        if self.tau is not None:
            s += f'tau {self.tau:.2f} '
        # s +=   f'max drive {self.m_max:.1f}\n{self.bg}'
        s += f'\n  {self.bg}'

        return s


class DualFactorController(Controller):
    """ Dual output controller, with immediate forward flow for rate output, leaky integration
    of a mixture of forward and backward flow for intensity output.
    """

    def __init__(self, **cfg):
        super().__init__(**cfg)
        self.u_rate = 0  # flow processing rate output
        self.u_intensity = 0  # flow processing intensity output
        self.intensity_flow = 0  # weighted mixture of forward and backward flow for intensity output
        self.kfi = None
        self.kbi = None
        self.tau_intensity = None

    def configure(self, kf_intensity, kb_intensity, tau_intensity, **cfg):
        super().configure(**cfg)
        self.kfi = kf_intensity  # gain for forward component of intensity output
        self.kbi = kb_intensity  # gain for backward component of intensity output
        self.tau_intensity = tau_intensity  # integrator leak time constant for intensity output

    def calc_motor_drive(self, sensed_flow):

        # rate output is the unfiltered forward flow
        self.u_rate = max(sensed_flow, 0)

        # intensity output depends on leaky integration of flow with differential gains for forward and backward
        # flow
        self.intensity_flow = self.kfi * sensed_flow if sensed_flow > 0 else self.kbi * sensed_flow

        if self.tau_intensity <= self.dt:
            # no integration required
            self.u_intensity = self.intensity_flow
        else:
            self.u_intensity += self.dt * (self.intensity_flow - self.u_intensity / self.tau_intensity)

        return self.u_rate, self.u_intensity

    def record(self, rec):
        super().record(rec)
        rec['u_rate'] = self.u_rate
        rec['u_intensity'] = self.u_intensity
        rec['intensity_flow'] = self.intensity_flow
        rec['kf_intensity'] = self.kfi
        rec['kb_intensity'] = self.kbi
        rec['tau_intensity'] = self.tau_intensity

    def __str__(self):
        s = (f'  {type(self).__name__}: '
             f'Kf intensity {self.kfi:.2f} Kb intensity {self.kbi:.2f} '
             f'tau intensity {self.tau_intensity:.2f} '
             f'\n  {self.bg}'
             )

        return s
