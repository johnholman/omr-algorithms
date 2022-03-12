class Agent(object):
    """Base class for an agent acting on basis of sensed optical flow

        Agents are made up of a body and a controller
    """

    def __init__(self, body, controller, **_cfg):
        self.body = body
        self.controller = controller

    def configure(self, **cfg):
        self.body.configure(**cfg)
        self.controller.configure(**cfg)

    def update(self, stimulus):
        """Select and perform action for this time update based on optic flow
        """
        sensed_flow = self.body.sense(stimulus)
        action = self.controller.act(sensed_flow)
        return self.body.perform(action)

    def record(self, rec):
        self.body.record(rec)
        self.controller.record(rec)

    def __str__(self):
        return f'Agent\n{self.body}\n{self.controller}'
