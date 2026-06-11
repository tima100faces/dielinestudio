"""Renderer-agnostic geometry model for dielines.

Geometry holds line segments, true circular arcs and INFO texts, each tagged
with a layer (CUT / CREASE / INFO). Renderers (PDF/SVG) consume this model.
Units: millimetres, y-up. Angles: degrees, CCW, 0 deg = +x axis.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field

CUT = "cut"
CREASE = "crease"
INFO = "info"
SAFE = "safe"        # safe / print area boundary (dashed); never a physical edge


@dataclass
class Seg:
    x1: float; y1: float; x2: float; y2: float
    layer: str = CUT


@dataclass
class Arc:
    cx: float; cy: float; r: float
    a0: float; a1: float          # degrees, CCW; sweep goes a0 -> a1
    layer: str = CUT

    def point(self, a_deg: float):
        a = math.radians(a_deg)
        return (self.cx + self.r * math.cos(a), self.cy + self.r * math.sin(a))

    def start(self): return self.point(self.a0)
    def end(self):   return self.point(self.a1)

    def sample(self, step_deg: float = 6.0):
        n = max(2, int(math.ceil(abs(self.a1 - self.a0) / step_deg)) + 1)
        return [self.point(self.a0 + (self.a1 - self.a0) * i / (n - 1)) for i in range(n)]


@dataclass
class Text:
    x: float; y: float; s: str
    size: float = 8.0
    layer: str = INFO
    rotation: float = 0.0         # degrees, CCW, y-up (math convention); 0 = horizontal


@dataclass
class Geometry:
    segs: list = field(default_factory=list)
    arcs: list = field(default_factory=list)
    texts: list = field(default_factory=list)

    # --- builders -------------------------------------------------------
    def line(self, x1, y1, x2, y2, layer=CUT):
        self.segs.append(Seg(x1, y1, x2, y2, layer)); return self

    def arc(self, cx, cy, r, a0, a1, layer=CUT):
        self.arcs.append(Arc(cx, cy, r, a0, a1, layer)); return self

    def text(self, x, y, s, size=8.0, rotation=0.0, layer=INFO):
        self.texts.append(Text(x, y, s, size, layer, rotation=rotation)); return self

    def polyline(self, pts, layer=CUT, close=False):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], layer)
        if close and len(pts) > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], layer)
        return self

    def rect(self, x, y, w, h, layer=CUT):
        return self.polyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                             layer=layer, close=True)

    def stadium(self, cx, cy, length, height, layer=CUT):
        """Horizontal stadium (rounded-end slot): total `length` x `height`."""
        r = height / 2.0
        xl, xr = cx - length / 2.0 + r, cx + length / 2.0 - r
        self.line(xl, cy - r, xr, cy - r, layer)
        self.line(xl, cy + r, xr, cy + r, layer)
        self.arc(xr, cy, r, -90, 90, layer)
        self.arc(xl, cy, r, 90, 270, layer)
        return self

    def extend(self, other: "Geometry"):
        self.segs += other.segs; self.arcs += other.arcs; self.texts += other.texts
        return self

    # --- analysis -------------------------------------------------------
    def bbox(self):
        xs, ys = [], []
        for s in self.segs:
            xs += [s.x1, s.x2]; ys += [s.y1, s.y2]
        for a in self.arcs:
            for px, py in a.sample():
                xs.append(px); ys.append(py)
        for t in self.texts:
            xs.append(t.x); ys.append(t.y)
        if not xs:
            return (0, 0, 0, 0)
        return (min(xs), min(ys), max(xs), max(ys))
