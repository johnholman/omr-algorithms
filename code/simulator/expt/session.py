from importlib import import_module


class Session(object):
    def __init__(self, **cfg):
        self.environment = self.create_component('environment.classname', **cfg)
        body = self.create_component('body.classname', **cfg)
        bout_generator = self.create_component('boutgenerator.classname', **cfg)
        controller = self.create_component('controller.classname', bout_generator=bout_generator, **cfg)
        self.agent = self.create_component('agent.classname', body=body, controller=controller, **cfg)
        self.dt = cfg['dt']
        self.t = 0
        self.stepnum = 0

    def configure(self, cfg):
        self.environment.configure(**cfg)
        self.agent.configure(**cfg)

    def update(self):
        self.t = self.dt * self.stepnum
        stimulus = self.environment.stimulate()
        action = self.agent.update(stimulus)
        self.environment.update(action)
        self.stepnum += 1

    @staticmethod
    def finished():
        return False

    def record(self, rec):
        rec['time'] = self.t
        rec['dt'] = self.dt
        self.environment.record(rec)
        self.agent.record(rec)

    @staticmethod
    def create_component(class_key, **cfg):
        """
        Return component with given configuration and random
        generator.
        
        The component classname is given as the value of key 'class_key' in cfg and
        the constructor signature is <component_class>(**cfg)
        """
        classname = cfg[class_key]
        module_name, classname = classname.rsplit(".", 1)
        module = import_module(module_name)
        cls = getattr(module, classname)
        return cls(**cfg)

    def __str__(self):
        return f'Session: dt {self.dt :.3f}\n{self.environment}\n{self.agent}'
