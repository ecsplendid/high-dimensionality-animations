import math
import sys
from manim import *
import numpy as np
from scipy.spatial import ConvexHull
from matplotlib.path import Path

def spiral(radius, step, resolution=.1, angle=0.0, start=0.0):
    n=10 #number of spirals
    d=0.1 #distance between 2 spirals
    r=0  #radius
    x,y = 0, 0

    coords = []

    cur_r = r
    for i in range(n):
        for a in range(1,360, 4):
            r = cur_r + d*a/360.0
            a *= math.pi/180.0
            y = r*math.sin(a)
            x = r*math.cos(a)
            coords.append((x,y))
        cur_r += d

    return coords


class Spiral(Scene):
    def construct(self):

        self.ax = Axes(x_range=[-1, 1, 0.1], y_range=[-1, 1, 0.1], tips=False,
                    axis_config={"include_numbers": True,"font_size": 24},
                    x_axis_config={"numbers_to_include": np.linspace(-1,1,7)[[0,1,2,4,5,6]]},
                    y_axis_config={"numbers_to_include": np.linspace(-1,1,7)})

        self.add(self.ax)


        coords = spiral(0.3, 0.01, resolution=.1, angle=350.0, start=0.0)

        for c in enumerate(coords):

            line = Line((c[c[0]-1][0],c[c[0]-1][1]), (c[c[0]-1][0], c[c[0]-1][1],)).set_color(WHITE)
            self.add(line)
            

            self.add(
                Dot(self.ax.coords_to_point(c[1][0],c[1][1]),color=GREEN,radius=0.05)
            )