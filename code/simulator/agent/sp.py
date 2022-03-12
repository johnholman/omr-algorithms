# sp.py - signal processing support for agent


class DelayElement(object):
    """Signal processing element that delays a signal by a fixed number of timesteps
    """

    def __init__(self, delay=10):
        self.delay = delay
        self.bufsiz = delay + 1
        self.buf = [0] * self.bufsiz
        self.xi = 0
        self.yi = -delay

    def process(self, x):
        self.buf[self.xi] = x
        self.xi += 1
        if self.xi >= self.bufsiz:
            self.xi -= self.bufsiz
        y = self.buf[self.yi]
        self.yi += 1
        if self.yi >= self.bufsiz:
            self.yi -= self.bufsiz
        return y
