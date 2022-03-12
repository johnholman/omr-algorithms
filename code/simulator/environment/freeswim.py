""" environment class simulating the freeswimming experimental environment where a fish swims but stream is
simulated by moving grid at fixed speed
"""


class FreeSwimEnvironment(object):

    def __init__(self, dt, **_cfg):
        self.dt = dt
        self.x = 0.0  # position of fish x
        self.xv = 0.0  # speed of fish over ground
        self.prs = 0.0  # position of fish relative to stimulus
        self.flow = 0.0
        self.swim_speed_req = 0.0
        self.s = None
        self.h = None
        self.Ke = None

    def configure(self, stimulus_speed, height, Ke, **_cfg):
        self.s = stimulus_speed  # stimulus speed
        self.h = height
        self.Ke = Ke

    def stimulate(self):
        """ Return sense data containing the ventral optic flow in rad/s
        """
        self.flow = (self.s - self.xv) / self.h
        return {'optic_flow': self.flow}

    def update(self, action):
        """Calculate new environment state resulting from this action performed at beginning of timestep
           and continued for duration dt
        """
        # speed through the water resulting from action holds throughout the timestep
        self.xv = action * self.Ke

        self.x += self.xv * self.dt  # resulting new position at end of timestep

        self.swim_speed_req = self.s

    def record(self, rec):
        rec['optic_flow'] = self.flow
        rec['swim_speed'] = self.xv
        rec['swim_speed_req'] = self.swim_speed_req
        rec['position'] = self.x
        rec['stimulus_speed'] = self.s
        rec['Ke'] = self.Ke
        rec['height'] = self.h

    def __str__(self):
        return f'{type(self).__name__}: stimulus speed {self.s :.2f}, Ke {self.Ke :.2f}, height {self.h :.2f} '
