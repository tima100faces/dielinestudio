"""Turtle-style pen that builds a Geometry by walking a contour.
Straight runs carry parametric length; corners are TRUE arcs; feature sub-paths
draw a fixed shape regardless of panel size. Units mm, y-up, heading deg (0=+x)."""
import math
from core.primitives import Geometry, CUT, CREASE


class Pen:
    def __init__(self, x=0.0, y=0.0, heading=0.0, g=None):
        self.g = g or Geometry()
        self.x, self.y, self.h = x, y, heading

    def jump(self, x, y, heading=None):
        self.x, self.y = x, y
        if heading is not None:
            self.h = heading
        return self

    def turn(self, deg):
        self.h += deg; return self

    def seth(self, deg):
        self.h = deg; return self

    def fwd(self, dist, layer=CUT):
        a = math.radians(self.h)
        nx, ny = self.x + dist * math.cos(a), self.y + dist * math.sin(a)
        if dist != 0:
            self.g.line(self.x, self.y, nx, ny, layer)
        self.x, self.y = nx, ny
        return self

    def arc(self, radius, deg, layer=CUT):
        """Sweep an arc turning by `deg` (+left/CCW), radius `radius`. True ARC."""
        r = abs(radius)
        if r < 1e-9 or deg == 0:
            return self
        side = 1 if deg > 0 else -1
        cx = self.x + r * math.cos(math.radians(self.h + 90 * side))
        cy = self.y + r * math.sin(math.radians(self.h + 90 * side))
        a0 = math.degrees(math.atan2(self.y - cy, self.x - cx))
        a1 = a0 + deg
        self.g.arc(cx, cy, r, a0, a1, layer)
        ar = math.radians(a1)
        self.x, self.y = cx + r * math.cos(ar), cy + r * math.sin(ar)
        self.h += deg
        return self
