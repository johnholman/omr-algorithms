""" environment class simulating the natural environment
"""


class NaturalEnvironment(object):

    def __init__(self, dt, **_cfg):
        self.dt = dt
        self.x = 0.0  # position of fish x
        self.xv = 0.0  # speed of fish over ground
        self.swim_speed = 0.0  # speed of fish through water
        self.swim_speed_req = 0.0  # required swim speed to match stream
        self.flow = 0.0
        self.water_speed = None
        self.h = None
        self.Ke = None

    #         self.xv = 0.0   # speed of fish over ground
    #         self.flow = - self.env.water_speed/self.h  # initial optic flow with fish not swimming

    def configure(self, Vs, height, Ke, **_cfg):
        self.water_speed = Vs  # water speed in mm/s
        self.h = height
        self.Ke = Ke

    def stimulate(self):
        """ Return stimulus corresponding to the actual ventral optic flow in rad/s
        """
        self.flow = -(self.swim_speed + self.water_speed) / self.h
        return {'optic_flow': self.flow}

    def update(self, action):
        """Calculate new environment state resulting from this action performed at beginning of timestep
           and continued for duration dt
        """
        # speed through the water resulting from action holds throughout the timestep
        self.swim_speed = action * self.Ke
        # agent speed over the ground is speed through water (swim_speed) plus speed of stream (Vs)
        self.xv = self.swim_speed + self.water_speed
        self.x += self.xv * self.dt  # resulting new position at end of timestep
        self.swim_speed_req = -self.water_speed

    def record(self, rec):
        rec['optic_flow'] = self.flow
        rec['swim_speed'] = self.swim_speed
        rec['swim_speed_req'] = self.swim_speed_req
        rec['position'] = self.x
        rec['ground_speed'] = self.xv
        rec['Vs'] = self.water_speed
        rec['Ke'] = self.Ke
        rec['height'] = self.h

    def __str__(self):
        return f'{type(self).__name__}: water speed (Vs) {self.water_speed :.2f}, ' \
               f'Ke {self.Ke :.2f}, height {self.h :.2f} '
