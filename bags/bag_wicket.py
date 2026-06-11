"""Wicket bag — built FROM A FORMULA, not from a reference DXF.

Thin-material bag (film / paper): there is no board thickness, no remap, no
reference geometry. The flat blank is a stack of full-width rectangles laid out
bottom -> top along Y:

    tab  ->  body  ->  wicket  ->  wicket  ->  body

Each section is its own closed CUT rectangle. Over the body+wicket block (NOT
the tab) sits a single SAFE-layer print/safe-area frame, inset from the edges.
Optional INFO dimension lines (dims=True). Units: mm, y-up, English-only.

This module deliberately shares NOTHING with boxes/pizza_led.py (no remap, no
windows, no double-crease, no slot_shift) — it is pure parametric construction.
"""
from core.primitives import Geometry, CUT, SAFE

TICK = 3.5            # dimension tick ("засечка") length, mm
_LAB = 5.0           # dimension label height, mm (~reference 240x420_60_40.dxf)
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


def wicket(width=240.0, body=420.0, wicket=60.0, tab=40.0,
           inset_side=10.0, inset_height=20.0, dims=False) -> Geometry:
    """Flat wicket-bag blank. Returns a Geometry (mm, y-up).

    Sections bottom->top: tab, body, wicket, wicket, body. Total height =
    tab + body + 2*wicket + body. The SAFE frame covers the body+wicket block
    only (above the tab), inset by inset_side at the sides and inset_height at
    both top and bottom.
    """
    g = Geometry()

    # --- section boundaries along Y (cumulative, bottom -> top) ----------
    y_tab = tab                          # tab / body joint
    y_b1 = y_tab + body                  # body / wicket joint
    y_w1 = y_b1 + wicket                 # wicket / wicket joint
    y_w2 = y_w1 + wicket                 # wicket / body joint
    H = y_w2 + body                      # top edge = total height

    # --- each section is its own closed CUT rectangle --------------------
    g.rect(0.0, 0.0, width, tab, CUT)        # tab
    g.rect(0.0, y_tab, width, body, CUT)     # body (lower)
    g.rect(0.0, y_b1, width, wicket, CUT)    # wicket (lower)
    g.rect(0.0, y_w1, width, wicket, CUT)    # wicket (upper)
    g.rect(0.0, y_w2, width, body, CUT)      # body (upper)

    # --- SAFE / print-area frame over the body+wicket block (not the tab) -
    sx = inset_side
    sw = width - 2 * inset_side
    sy = y_tab + inset_height                # bottom sits above the tab joint
    sh = (H - inset_height) - sy             # top sits below the top edge
    g.rect(sx, sy, sw, sh, SAFE)

    # --- optional dimensions (INFO), number-only labels ------------------
    if dims:
        near = -12.0                         # per-section column (left of bag)
        far = -34.0                          # overall-height column (further left)
        # near column: one dim per section, bottom -> top
        for y0, y1 in ((0.0, y_tab), (y_tab, y_b1), (y_b1, y_w1),
                       (y_w1, y_w2), (y_w2, H)):
            _dim_v(g, near, y0, y1, f"{y1 - y0:g} mm")
        # far column: overall height
        _dim_v(g, far, 0.0, H, f"{H:g} mm")
        # horizontal: width across the top
        _dim_h(g, H + 12.0, 0.0, width, f"{width:g} mm")

    return g


if __name__ == "__main__":
    for (w, b, wk, tb) in [(240, 420, 60, 40), (300, 500, 80, 50)]:
        g = wicket(w, b, wk, tb)
        bb = tuple(round(v, 1) for v in g.bbox())
        print(f"{w}/{b}/{wk}/{tb}: bbox {bb} "
              f"size {round(bb[2]-bb[0],1)}x{round(bb[3]-bb[1],1)} "
              f"cutSeg {len(g.segs)}")
