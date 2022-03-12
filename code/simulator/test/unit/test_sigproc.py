from unittest import TestCase
from simulator.agent.sp import DelayElement


class TestDelayElement(TestCase):
    def test_delay(self):
        d = DelayElement(delay=3)
        self.assertEqual(d.bufsiz, 4)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [0] * len(x)
        for i in range(len(x)):
            y[i] = d.process(x[i])
        self.assertEqual(y, [0, 0, 0, 1, 2, 3, 4, 5, 6])

    def test_zero_delay(self):
        d = DelayElement(delay=0)
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [0] * len(x)
        for i in range(len(x)):
            y[i] = d.process(x[i])
        self.assertEqual(x, y)
