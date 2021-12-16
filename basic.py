from manim import *
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.path import Path

class CoordSysExample(Scene):
    def construct(self):
        # the location of the ticks depends on the x_range and y_range.

        self.ax = Axes(x_range=[-1, 1, 0.1], y_range=[-1, 1, 0.1], tips=False,
                    axis_config={"include_numbers": True,"font_size": 24},
                    x_axis_config={"numbers_to_include": np.linspace(-1,1,7)[[0,1,2,4,5,6]]},
                    y_axis_config={"numbers_to_include": np.linspace(-1,1,7)})
        # plane = NumberPlane()
        self.add(self.ax)

        self.samples = []
        self.training_dots = []
        self.test_samples = []
        self.testing_dots = []

        self.add_training_data(10)
        vertices = self.compute_hull()
        self.add_convex_hull(vertices)
        self.wait(1)
        ratio = self.add_test_data(vertices)
        

        group = VGroup(self.label_training,self.ax,self.convex_hull,self.testing_dots,self.label_ratio, *self.training_dots)
        self.play(group.animate.scale(0.65).to_corner(UL))


        self.ax2 = Axes(x_range=[0, 100, 10], y_range=[0, 100, 10],tips=False,
                    axis_config={"include_numbers": True,"font_size": 50},
                    x_axis_config={"numbers_to_include": np.arange(0,100, 10)},
                    y_axis_config={"numbers_to_include": np.arange(0,100, 10)}).scale(0.33).to_corner(DR)
        y_label = self.ax2.get_y_axis_label(Tex("\% inside").scale(0.5), edge=LEFT, direction=LEFT, buff=0.4)
        x_label = self.ax2.get_y_axis_label(Tex("training set size").scale(0.5), edge=DOWN, direction=DOWN, buff=0.4)
        self.play(Create(VGroup(self.ax2,x_label,y_label)))
        self.add_ratio(ratio)

        for i in range(3):
            self.play(FadeOut(self.testing_dots), FadeOut(self.convex_hull),FadeOut(self.label_ratio))
            self.add_training_data(10)
            vertices = self.compute_hull()
            self.add_convex_hull(vertices)
            ratio = self.add_test_data(vertices)
            self.label_ratio[0].set_value(ratio)
            self.add_ratio(ratio)

    def add_training_data(self,numbers):
        """
        add training samples to existing list, and update the associated label
        """
        if len(self.samples)==0:

            number, text = self.label_training = VGroup(
                Integer(number=0, font_size=48, edge_to_fix=RIGHT),
                Tex(" training samples", font_size=48), 
            )

            number.align_to(text, UP)
            number.next_to(text, RIGHT)

            def update(m):
                m.set_value(len(self.samples))

            number.add_updater(update)
            self.label_training.align_on_border(LEFT+UP)
            scale = 1
        else:
            scale=0.65


        for i in range(3):
            self.samples.append(np.random.rand(2) * 2 - 1)
            self.training_dots.append(
                Dot(self.ax.coords_to_point(self.samples[-1][0], self.samples[-1][1])).scale(scale)
            )
            self.add(self.training_dots[-1])
            fadein = FadeIn(self.training_dots[-1])
            fadein.set_run_time(0.2)
            if len(self.samples)==1:
                self.play(fadein,FadeIn(self.label_training))
            else:
                self.play(fadein)


    def add_test_data(self,vertices):
        if len(self.test_samples) == 0:
            for i in range(400):
                self.test_samples.append(np.random.rand(2) * 2 - 1)
                self.testing_dots.append(
                    Dot(self.ax.coords_to_point(self.test_samples[-1][0], self.test_samples[-1][1]),color=GREEN,radius=0.05)
                )
            self.testing_dots = VGroup(*self.testing_dots)

        hull_path = Path([self.samples[u] for u in vertices])
        inside = 0.
        for i in range(len(self.test_samples)):
            inside += int(hull_path.contains_point(self.test_samples[i]))
        inside /= len(self.test_samples)
        inside *= 100

        if not hasattr(self, 'label_ratio'):
            number, text = self.label_ratio = VGroup(
                DecimalNumber(inside),
                Text("% of test samples lie within the hull"),
            )
            self.label_ratio.set_color(GREEN)
            text.next_to(number,RIGHT)
            self.label_ratio.align_on_border(RIGHT+DOWN)
        else:
            self.label_ratio[0].set_value(inside)

        self.play(FadeIn(self.testing_dots))
        self.play(FadeIn(self.label_ratio))
        return inside


    def compute_hull(self):
        hull = ConvexHull(np.array(self.samples))
        return hull.vertices


    def add_convex_hull(self,vertices):


        # create the circles that are the vertices of the hull
        circles = []
        vertices = np.concatenate([vertices, [vertices[0]]])
        for v in vertices:
            circle = Circle(radius=0.2, color=RED)
            circle.move_to(self.training_dots[v])
            circles.append(circle)

        # path joining the vertives i.e. the convex hull boundary
        path = VMobject()
        path.set_points_as_corners(
            [self.ax.coords_to_point(*self.samples[u]) for u in vertices]
        )
        path.set_color(RED)
        self.convex_hull = VGroup(path, *circles)
        self.play(FadeIn(self.convex_hull))


    def add_ratio(self,ratio):
        dot = Dot(self.ax2.c2p(len(self.samples), ratio))
        # h_line = self.ax2.get_horizontal_line(dot, line_func=Line)
        self.play(FadeIn(dot))
