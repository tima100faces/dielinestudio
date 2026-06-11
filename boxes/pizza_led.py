"""14747 LED box — PARAMETRIC TEMPLATE generator.

Instead of hand-coding details (which kept being wrong), this loads the exact
reference dieline from samples/14747_d-layers.dxf and regenerates it at any
W x D x H x t by piecewise-linear remapping of the fold-grid ZONES:
  X zones: [left wall][base bottom][spine][lid][lid flap]
  Y zones: [bottom end assembly][main panel][top end assembly]
Wall/spine/flap/end zones scale with H; base/lid widths with D; panel length
with W. Features (slots, tabs, corners, locks) ride along rigidly. Reference dims
are 430x260x30 t1.5 -> at those values the output equals the reference 1:1.

CUT = colour 114 / Layer 1 ; CREASE = Layer 3 / colour 230 in the DXF.
"""
import os, math, ezdxf
from core.primitives import Geometry, CUT, CREASE

_DXF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "samples", "14747_d-layers.dxf")

# reference anchors (origin = base-left fold x, bottom main fold y), measured
RX = [-36.6, 0.0, 263.3, 301.2, 567.3, 603.8]      # wall|base|spine|lid|flap
RY = [-95.0, 0.0, 432.1, 527.1]                     # flap|botFold|topFold|flap
REF = dict(W=430.0, D=260.0, H=30.0, t=1.5)
OX, OY = -24.4, -191.0                              # DXF->local origin shift


def _walk(e, out):
    if e.dxftype() == "INSERT":
        for v in e.virtual_entities():
            _walk(v, out)
    else:
        out.append(e)


def _bulge_pts(p0, p1, b, n=14):
    if abs(b) < 1e-9:
        return [p0]
    x0, y0 = p0; x1, y1 = p1
    chord = math.hypot(x1 - x0, y1 - y0)
    if chord < 1e-9:
        return [p0]
    ang = 4 * math.atan(b)                  # included angle
    r = chord / (2 * math.sin(abs(ang) / 2))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0) / chord, (x1 - x0) / chord
    d = r * math.cos(ang / 2) * (1 if b > 0 else -1)
    cx, cy = mx - nx * d, my - ny * d
    a0 = math.atan2(y0 - cy, x0 - cx)
    out = []
    for i in range(n + 1):
        a = a0 + ang * i / n
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def _load_template():
    d = ezdxf.readfile(_DXF)
    ents = []
    for e in d.modelspace():
        _walk(e, ents)
    polys = []      # (is_crease, [pts])  in local origin
    for e in ents:
        t = e.dxftype()
        if t == "MTEXT":
            continue
        cre = (e.dxf.color == 230)
        pts = []
        if t == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif t == "LWPOLYLINE":
            raw = list(e.get_points("xyb")); closed = e.closed
            for i in range(len(raw)):
                x, y, b = raw[i]
                nx, ny, _ = raw[(i + 1) % len(raw)]
                if i == len(raw) - 1 and not closed:
                    pts.append((x, y)); break
                pts += _bulge_pts((x, y), (nx, ny), b)
            if closed and pts:
                pts.append(pts[0])
        elif t in ("ARC", "CIRCLE", "SPLINE", "ELLIPSE"):
            try:
                pts = [(p.x, p.y) for p in e.flattening(0.2)]
            except Exception:
                pts = []
        if len(pts) >= 2:
            polys.append((cre, [(x - OX, y - OY) for x, y in pts]))
    return polys


_TEMPLATE = None
def _template():
    global _TEMPLATE
    if _TEMPLATE is None:
        _TEMPLATE = _load_template()
    return _TEMPLATE


def _piecewise(v, src, dst):
    if v <= src[0]:
        return dst[0] + (v - src[0])
    if v >= src[-1]:
        return dst[-1] + (v - src[-1])
    for i in range(len(src) - 1):
        if src[i] <= v <= src[i + 1]:
            f = (v - src[i]) / (src[i + 1] - src[i])
            return dst[i] + f * (dst[i + 1] - dst[i])
    return v


def _slot_boxes(polys, maxdim=70.0):
    """Stitch cut segments into loops; return bboxes of small CLOSED loops (the
    lock slots), which arrive split into caps (arcs) + straight sides."""
    import math
    segs = []
    for cre, pts in polys:
        if cre:
            continue
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) > 0.05:
                segs.append([a, b])
    used = [False] * len(segs)
    TOL = 0.8

    def find(pt, skip):
        for i, s in enumerate(segs):
            if used[i] or i == skip:
                continue
            if math.dist(s[0], pt) < TOL:
                return i, s[1]
            if math.dist(s[1], pt) < TOL:
                return i, s[0]
        return None, None

    boxes = []
    for start in range(len(segs)):
        if used[start]:
            continue
        used[start] = True
        chain = [segs[start][0], segs[start][1]]
        cur, prev, closed = segs[start][1], start, False
        while True:
            i, nxt = find(cur, prev)
            if i is None:
                break
            used[i] = True
            chain.append(nxt); cur = nxt; prev = i
            if math.dist(cur, chain[0]) < TOL:
                closed = True
                break
        xs = [p[0] for p in chain]; ys = [p[1] for p in chain]
        if closed and (max(xs) - min(xs)) < maxdim and (max(ys) - min(ys)) < maxdim:
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
    return boxes


def _build_windows(polys, axis, thresh=70.0):
    """Rigid windows = projection of feature polylines (>2 pts) narrow on `axis`,
    PLUS whole lock-slot loops (so a slot stays rigid end-to-end). Merged."""
    wins = []
    for cre, pts in polys:
        if len(pts) <= 2:
            continue
        vs = [p[axis] for p in pts]
        if max(vs) - min(vs) < thresh:
            wins.append([min(vs) - 1.0, max(vs) + 1.0])
    for x0, y0, x1, y1 in _slot_boxes(polys):
        lo, hi = (x0, x1) if axis == 0 else (y0, y1)
        wins.append([lo - 1.0, hi + 1.0])
    wins.sort()
    merged = []
    for lo, hi in wins:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], hi)
        else:
            merged.append([lo, hi])
    return merged


def _make_controls(zsrc, zdst, windows):
    """Control points for a piecewise-linear map that resizes each zone
    [zsrc -> zdst] while keeping `windows` rigid (slope 1); free gaps absorb the
    change. One continuous monotonic map -> shared endpoints stay shared."""
    src, dst = [], []
    for (s0, s1), (d0, d1) in zip(zip(zsrc, zsrc[1:]), zip(zdst, zdst[1:])):
        ws = sorted([max(a, s0), min(b, s1)] for a, b in windows if b > s0 and a < s1)
        ws = [w for w in ws if w[1] > w[0]]
        feat = sum(b - a for a, b in ws)
        free_src = (s1 - s0) - feat
        free_dst = (d1 - d0) - feat
        scale = free_dst / free_src if free_src > 1e-6 else 1.0
        cs, cd = s0, d0
        if not src or abs(src[-1] - cs) > 1e-9:
            src.append(cs); dst.append(cd)
        for a, b in ws:
            cd += (a - cs) * scale; cs = a
            src.append(cs); dst.append(cd)
            cd += (b - a); cs = b
            src.append(cs); dst.append(cd)
        cd += (s1 - cs) * scale
        src.append(s1); dst.append(cd)
    return src, dst


def _drop_cut_under_crease(g):
    """Where the source draws BOTH a cut and a crease on the same fold line (e.g. a
    tab base), the CREASE wins (it marks a real fold): drop the coincident CUT.
    Perimeter lines carry no crease, so they stay cut."""
    from core.primitives import CUT, CREASE
    rh = [(s.y1, min(s.x1, s.x2), max(s.x1, s.x2)) for s in g.segs
          if s.layer == CREASE and abs(s.y1 - s.y2) < 0.3]
    rv = [(s.x1, min(s.y1, s.y2), max(s.y1, s.y2)) for s in g.segs
          if s.layer == CREASE and abs(s.x1 - s.x2) < 0.3]

    def covered(a, b, lines, c):
        ivs = sorted((max(a, la), min(b, lb)) for cc, la, lb in lines
                     if abs(cc - c) < 0.9 and lb > a and la < b)
        tot, end = 0.0, a - 1.0
        for lo, hi in ivs:
            lo = max(lo, end)
            if hi > lo:
                tot += hi - lo; end = hi
        return tot / (b - a) if b > a else 0.0

    keep = []
    for s in g.segs:
        if s.layer == CUT:
            if abs(s.y1 - s.y2) < 0.3:
                a, b = min(s.x1, s.x2), max(s.x1, s.x2)
                if b > a and covered(a, b, rh, s.y1) >= 0.7:
                    continue
            elif abs(s.x1 - s.x2) < 0.3:
                a, b = min(s.y1, s.y2), max(s.y1, s.y2)
                if b > a and covered(a, b, rv, s.x1) >= 0.7:
                    continue
        keep.append(s)
    g.segs = keep
    return g


def pizza_led(W=430.0, D=260.0, H=30.0, t=1.5):
    polys = _template()
    # target zone anchors: panels grow with D/W; walls & end assembly with H (and t)
    tx = [-(H + 6.6), 0.0, D + 2 * t]
    tx.append(tx[-1] + (H + 7.9))            # spine
    tx.append(tx[-1] + (D + 4 * t))          # lid
    tx.append(tx[-1] + (H + 6.5))            # lid flap
    # 180-deg double crease, thickness reactive (below DOUBLE_T -> single).
    DOUBLE_T = 0.6
    DCG = 2.0 * t                            # double-crease gap = 2 x board thickness
    grow = max(0.0, DCG - 2.0 * 1.5)         # box grows vs reference t=1.5
    DBL = ((-54.1, -47.1, -1.0), (486.2, 478.9, 1.0))   # (outer, inner, sign) local y

    # end assembly (and thus the lock flap + tabs) moves out by `grow` -> box grows
    ty = [-(H + 65.0 + grow), 0.0, W + 2.0, (W + 2.0) + (H + 65.0 + grow)]

    # ONE continuous remap with rigid feature windows -> contour stays connected
    SX, DX = _make_controls(RX, tx, _build_windows(polys, 0))
    SY, DY = _make_controls(RY, ty, _build_windows(polys, 1))
    rx = lambda x: _piecewise(x, SX, DX)
    ry_ = lambda y: _piecewise(y, SY, DY)

    def slot_shift(pts):
        """A lock slot (small closed loop in the base bottom) tracks the flap:
        it shifts by `grow` toward its end so tab<->slot stay aligned (linked)."""
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if (len(pts) > 2 and (max(ys) - min(ys)) < 15 and 40 < (max(xs) - min(xs)) < 65):
            return -grow if (min(ys) + max(ys)) / 2.0 < 216 else grow
        return 0.0

    g = Geometry()
    for cre, pts in polys:
        layer = CREASE if cre else CUT
        ys = [p[1] for p in pts]; h = max(ys) - min(ys)
        yloc = (min(ys) + max(ys)) / 2.0
        if cre and h < 1.0 and any(abs(yloc - o) < 1.6 for o, _, _ in DBL):
            if t < DOUBLE_T:
                continue
            outer, inner, sgn = next(d for d in DBL if abs(yloc - d[0]) < 1.6)
            yy = ry_(inner) + sgn * DCG
            for a, b in zip(pts, pts[1:]):
                g.line(rx(a[0]), yy, rx(b[0]), yy, CREASE)
            continue
        sh = slot_shift(pts)
        rp = [(rx(x), ry_(y) + sh) for x, y in pts]
        for a, b in zip(rp, rp[1:]):
            g.line(a[0], a[1], b[0], b[1], layer)
    _drop_cut_under_crease(g)
    return g


if __name__ == "__main__":
    for (w, d, h, t) in [(430, 260, 30, 1.5), (580, 260, 30, 1.5)]:
        g = pizza_led(w, d, h, t)
        b = tuple(round(v, 1) for v in g.bbox())
        cre = sum(1 for s in g.segs if s.layer == CREASE)
        print(f"{w}x{d}x{h}: bbox {b} size {round(b[2]-b[0],1)}x{round(b[3]-b[1],1)} "
              f"creaseSeg {cre} cutSeg {len(g.segs)-cre}")
