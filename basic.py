from manim import *
import numpy as np
from scipy.spatial import ConvexHull


class CoordSysExample(Scene):
    def construct(self):
        # the location of the ticks depends on the x_range and y_range.

        self.ax = Axes(x_range=[-1, 1, 0.1], y_range=[-1, 1, 0.1], tips=False)
        plane = NumberPlane()
        self.add(self.ax, plane)

        self.samples = []

        self.add_text()
        self.add_training_data()
        self.wait(1)
        self.add_convex_hull()

        # Labels for the x-axis and y-axis.
        # y_label = grid.get_y_axis_label("y", edge=LEFT, direction=LEFT, buff=0.4)
        # x_label = grid.get_x_axis_label("x")
        # grid_labels = VGroup(x_label, y_label)

        # graphs = VGroup()
        # for n in np.arange(1, 20 + 0.5, 0.5):
        #     graphs += grid.plot(lambda x: x ** n, color=WHITE)
        #     graphs += grid.plot(
        #         lambda x: x ** (1 / n), color=WHITE, use_smoothing=False
        #     )

        # Extra lines and labels for point (1,1)
        # title = Title(
        #     # spaces between braces to prevent SyntaxError
        #     r"Graphs of $y=x^1$ and $y=x^n (n=1,2,3,...,20)$",
        #     include_underline=False,
        #     font_size=40,
        # )

    def add_training_data(self):
        self.dots = []
        for i in range(20):
            self.samples.append(np.random.rand(2) * 2 - 1)
            self.dots.append(
                Dot(self.ax.coords_to_point(self.samples[-1][0], self.samples[-1][1]))
            )
            self.add(self.dots[-1])
            fadein = FadeIn(self.dots[-1])
            fadein.set_run_time(0.2)
            self.play(fadein)
        self.samples = np.array(self.samples)

    def add_convex_hull(self):
        hull = ConvexHull(self.samples)
        circles = []
        vertices = np.concatenate([hull.vertices, [hull.vertices[0]]])
        for v in vertices:
            circle = Circle(radius=0.2, color=RED)
            circle.move_to(self.dots[v])
            circles.append(circle)
        path = VMobject()
        path.set_points_as_corners(
            [self.ax.coords_to_point(x, y) for (x, y) in self.samples[vertices]]
        )
        path.set_color(RED)
        self.play(FadeIn(VGroup(path, *circles)))

    def add_text(self):
        Integer(number=0)
        Text(" training samples")
        # number, text = label = VGroup(
        #     Integer(number=0),
        #     Text(" training samples"),
        # )
        # number.add_updater(lambda m: m.set_value(len(self.samples)))
        # self.add(text)
        # f_always(number.set_value, lambda: len(self.samples))
