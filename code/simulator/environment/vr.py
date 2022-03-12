""" environment class simulating the virtual reality situation where the fish is restrained and
ventral stimulus speed is determined by swimming effort.
"""


class VREnvironment(object):

    def __init__(self, dt, **cfg):
        self.dt = dt
        self.effort = 0.0  # swim effort of agent
        self.swim_speed = 0.0  # speed of fish through water
        self.swim_speedreq = 0.0  # required swim speed to match stream
        self.flow = 0.0
        self.h = 0.0
        self.s = 0.0
        self.b = None
        self.hvr = None
        self.Ke = None
        self.gain = None

    def configure(self, baseline_speed, height_vr, gain, Ke, **_cfg):
        self.b = baseline_speed  # speed of stimulus when fish is not swimming
        self.hvr = height_vr
        self.Ke = Ke
        self.gain = gain

    def stimulate(self):
        """ Return sense data containing the ventral optic flow in rad/s
        """
        #         self.s = self.b - self.gain*self.effort
        self.flow = (self.b - self.gain * self.effort) / self.hvr
        return {'optic_flow': self.flow}

    def update(self, action):
        """ Update environment in response to changes in agent activity or configuration
        """
        self.effort = action
        self.s = self.b - self.gain * self.effort
        self.swim_speed = (self.b - self.s) * self.Ke / self.gain
        self.swim_speedreq = self.b * self.Ke / self.gain
        self.h = self.hvr * self.Ke / self.gain

    def record(self, rec):
        # record state of environment as at the end of the timestep
        rec['optic_flow'] = self.flow
        rec['stimulus_speed'] = self.s
        rec['baseline_speed'] = self.b
        rec['height_vr'] = self.hvr
        rec['swim_speed'] = self.swim_speed
        rec['swim_speed_req'] = self.swim_speedreq
        rec['gain'] = self.gain
        rec['height'] = self.h
        rec['Ke'] = self.Ke

    def __str__(self):
        return f'{type(self).__name__}: baseline stimulus speed {self.b :.2f}, VR height {self.hvr :.2f} ' \
               f'gain {self.gain : .2f}, Ke {self.Ke : .2f}'


class VRReplayEnvironment(VREnvironment):

    def __init__(self, dt, **cfg):
        VREnvironment.__init__(self, dt, **cfg)
        self.stim_rec = []
        self.recorder = None
        self.recording = None
        self.stimulus_record = None
        self.replay = None
        self.phase_step = None

    def configure(self, recorder, **args):
        self.recorder = recorder
        self.replay = (recorder == 'replay')
        self.recording = (recorder == 'record')
        if self.recording:
            self.stimulus_record = []
        if self.replay and len(self.stim_rec) == 0:
            raise ValueError('No stimulus recording to replay')
        self.phase_step = 0
        VREnvironment.configure(self, **args)

    def stimulate(self):
        """ Return sense data containing the ventral optic flow in rad/s, or from the
        session recording if in replay mode
        """
        if not self.replay:
            return VREnvironment.stimulate(self)

        if self.phase_step >= len(self.stim_rec):
            raise ValueError('Stimulus recording too short')
        self.s = self.stim_rec[self.phase_step]
        self.flow = self.s / self.h
        return {'optic_flow': self.flow}

    def update(self, action):
        self.effort = action
        if self.recording:
            self.stim_rec.append(self.s)
        self.phase_step += 1

    def record(self, rec):
        rec['recorder'] = self.recorder
        VREnvironment.record(self, rec)

    def __str__(self):
        return f'{type(self).__name__}: recording status {self.recorder} \n  {super().__str__()}'
