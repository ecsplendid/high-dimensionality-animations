from manim import *
import numpy as np

class CSV(GraphScene):
    def construct(self):
        self.setup_axes()
        for i in range(100):
            dot = Dot(np.randn(3))
            self.add(dot)
            self.play(FadeIn(dot))
