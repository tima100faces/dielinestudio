"""Wicket bag — built FROM A FORMULA, not from a reference DXF.

Thin-material bag (film / paper): there is no board thickness, no remap, no
reference geometry. The flat blank is a stack of full-width rectangles laid out
bottom -> top along Y:

    lip  ->  length  ->  gusset  ->  gusset  ->  length

Each section is its own closed CUT rectangle. Over the length+gusset block (NOT
the lip) sits a single SAFE-layer print/safe-area frame, inset from the edges.
Optional INFO dimension lines (dims=True). Units: mm, y-up, English-only.

This module deliberately shares NOTHING with boxes/pizza_led.py (no remap, no
windows, no double-crease, no slot_shift) — it is pure parametric construction.
"""
from core.primitives import Geometry, CUT, SAFE

TICK = 3.5            # dimension tick ("засечка") length, mm
_LAB = 5.0           # dimension label height, mm (~reference 240x420_60_40.dxf)
_PANEL = 10.0        # panel-label height, mm
_LEGEND = 4.5        # legend text height, mm
_CH = 0.55           # rough glyph-width factor (× size) for centring labels

# Dimensions are drawn on the CUT layer so they carry the technical red pen
# (same colour as the dieline geometry); they stay numeric, English-only.
_DIM = CUT


def _dim_v(g, x, y0, y1, label):
    """Vertical dimension: line at x from y0..y1, horizontal end ticks, and a
    VERTICAL (90deg) number-only label centred on the line, sitting to its left."""
    g.line(x, y0, x, y1, _DIM)
    g.line(x - TICK / 2, y0, x + TICK / 2, y0, _DIM)
    g.line(x - TICK / 2, y1, x + TICK / 2, y1, _DIM)
    tlen = len(label) * _LAB * _CH
    ymid = (y0 + y1) / 2.0
    # rotated 90deg CCW: glyphs read bottom->top, height extends left of anchor x
    g.text(x - 2.0, ymid - tlen / 2.0, label, size=_LAB, rotation=90.0, layer=_DIM)


def _dim_h(g, y, x0, x1, label):
    """Horizontal dimension: line at y from x0..x1, vertical end ticks, and a
    HORIZONTAL number-only label centred above the line."""
    g.line(x0, y, x1, y, _DIM)
    g.line(x0, y - TICK / 2, x0, y + TICK / 2, _DIM)
    g.line(x1, y - TICK / 2, x1, y + TICK / 2, _DIM)
    tlen = len(label) * _LAB * _CH
    g.text((x0 + x1) / 2.0 - tlen / 2.0, y + 2.0, label, size=_LAB, layer=_DIM)


def _panel(g, cx, cy, text, width, size=_PANEL, rot=0.0):
    """Centred panel label at section centre (cx, cy). rot=0 upright,
    rot=180 upside-down (anchor mirrored through itself so it stays centred).
    Auto-shrinks so the text never exceeds the panel width."""
    size = min(size, width * 0.9 / max(1, len(text) * _CH))
    w = len(text) * size * _CH
    cap = size * 0.7
    if rot == 180.0:
        ax, ay = cx + w / 2.0, cy + cap / 2.0
    else:
        ax, ay = cx - w / 2.0, cy - cap / 2.0
    g.text(ax, ay, text, size=size, rotation=rot, layer=_DIM)


def wicket(width=240.0, length=420.0, gusset=60.0, lip=40.0,
           safe_side=10.0, safe_height=20.0, dims=False) -> Geometry:
    """Flat wicket-bag blank. Returns a Geometry (mm, y-up).

    Sections bottom->top: lip, length, gusset, gusset, length. Total height =
    lip + length + 2*gusset + length. The SAFE frame covers the length+gusset
    block only (above the lip), inset by safe_side at the sides and safe_height
    at both top and bottom.
    """
    g = Geometry()

    # --- section boundaries along Y (cumulative, bottom -> top) ----------
    y_lip = lip                          # lip / length joint
    y_l1 = y_lip + length                # length / gusset joint
    y_g1 = y_l1 + gusset                 # gusset / gusset joint
    y_g2 = y_g1 + gusset                 # gusset / length joint
    H = y_g2 + length                    # top edge = total height

    # --- each section is its own closed CUT rectangle --------------------
    g.rect(0.0, 0.0, width, lip, CUT)        # lip
    g.rect(0.0, y_lip, width, length, CUT)   # length (lower)
    g.rect(0.0, y_l1, width, gusset, CUT)    # gusset (lower)
    g.rect(0.0, y_g1, width, gusset, CUT)    # gusset (upper)
    g.rect(0.0, y_g2, width, length, CUT)    # length (upper)

    # --- SAFE / print-area frame over the length+gusset block (not the lip) -
    sx = safe_side
    sw = width - 2 * safe_side
    sy = y_lip + safe_height                 # bottom sits above the lip joint
    sh = (H - safe_height) - sy              # top sits below the top edge
    g.rect(sx, sy, sw, sh, SAFE)

    # --- optional dimensions (INFO), number-only labels ------------------
    if dims:
        near = -12.0                         # per-section column (left of bag)
        far = -34.0                          # overall-height column (further left)
        # near column: one dim per section, bottom -> top
        for y0, y1 in ((0.0, y_lip), (y_lip, y_l1), (y_l1, y_g1),
                       (y_g1, y_g2), (y_g2, H)):
            _dim_v(g, near, y0, y1, f"{y1 - y0:g} mm")
        # far column: overall height
        _dim_v(g, far, 0.0, H, f"{H:g} mm")
        # horizontal: width across the top
        _dim_h(g, H + 12.0, 0.0, width, f"{width:g} mm")

        # --- panel labels (large, centred on their sections) ----------
        cx = width / 2.0
        _panel(g, cx, (y_g2 + H) / 2.0, "FRONT", width)                # length (upper)
        _panel(g, cx, (y_lip + y_l1) / 2.0, "BACK", width, rot=180.0)  # length (lower), flipped
        # bottom gusset: two stacked lines centred on the gusset block
        cyg = (y_l1 + y_g2) / 2.0
        ls = _PANEL * 1.15
        _panel(g, cx, cyg + ls / 2.0, "BOTTOM", width)
        _panel(g, cx, cyg - ls / 2.0, "GUSSET", width)

        # --- legend under the blank (below the lip) -------------------
        g.text(0.0, -10.0, "blue dashed = printable area, do not exceed",
               size=_LEGEND, layer=_DIM)

    return g


if __name__ == "__main__":
    for (w, length, gus, lip) in [(240, 420, 60, 40), (300, 500, 80, 50)]:
        g = wicket(w, length, gus, lip)
        bb = tuple(round(v, 1) for v in g.bbox())
        print(f"{w}/{length}/{gus}/{lip}: bbox {bb} "
              f"size {round(bb[2]-bb[0],1)}x{round(bb[3]-bb[1],1)} "
              f"cutSeg {len(g.segs)}")
