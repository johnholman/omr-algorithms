from simulator.agent.sp import DelayElement


class Body(object):
    """Body of an agent operating on the basis of optical flow stimulation
    """

    def __init__(self, dt, rgen, **_cfg):
        self.rgen = rgen  # random number generator
        self.dt = dt  # timestep duration
        self.sensed_flow = 0
        self.sensory_noise = None
        self.sensory_delay = None
        self.delay_timesteps = None
        self.delayer = None

    def configure(self, sensory_noise=0.0, sensory_delay=0, **_cfg):
        self.sensory_noise = sensory_noise
        self.sensory_delay = sensory_delay
        self.delay_timesteps = round(self.sensory_delay / self.dt)
        self.delayer = DelayElement(delay=self.delay_timesteps)

    def sense(self, stimulus):
        """ Return sensory input about the flow given in the stimulus
        """
        w = stimulus['optic_flow']

        # add noise
        if self.sensory_noise > 0.0:
            w += self.rgen.normal(0, self.sensory_noise)
            # self.w += self.rgen.normal(0, self.sensory_noise)

        # impose delay
        if self.sensory_delay != 0:
            w = self.delayer.process(w)

        self.sensed_flow = w
        return self.sensed_flow

    @staticmethod
    def perform(action):
        """Return result of performing the given action

        For now just the identity as the environment is modelled as responding directly
        to the action
        """
        return action

    def record(self, rec):
        rec['sensed_flow'] = self.sensed_flow
        rec['sensory_noise'] = self.sensory_noise
        rec['sensory_delay'] = self.sensory_delay

    def __str__(self):
        return (f'{type(self).__name__}: sensory noise {self.sensory_noise}, '
                f'sensory delay {self.sensory_delay}s ({self.delay_timesteps} steps)')
