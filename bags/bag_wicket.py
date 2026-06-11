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
from core.primitives import Geometry, CUT, SAFE, INFO

TICK = 3.5            # dimension tick ("засечка") length, mm
_AVG_CH = 1.7         # rough character width for centring labels, mm


def _dim_v(g, x, y0, y1, label):
    """Vertical dimension line with end ticks + label to the right."""
    g.line(x, y0, x, y1, INFO)
    g.line(x - TICK / 2, y0, x + TICK / 2, y0, INFO)
    g.line(x - TICK / 2, y1, x + TICK / 2, y1, INFO)
    g.text(x + TICK, (y0 + y1) / 2.0 - 1.5, label, size=7.0)


def _dim_h(g, y, x0, x1, label):
    """Horizontal dimension line with end ticks + centred label below."""
    g.line(x0, y, x1, y, INFO)
    g.line(x0, y - TICK / 2, x0, y + TICK / 2, INFO)
    g.line(x1, y - TICK / 2, x1, y + TICK / 2, INFO)
    g.text((x0 + x1) / 2.0 - len(label) * _AVG_CH, y - 6.0, label, size=7.0)


def wicket(width=240.0, body=420.0, wicket=60.0, tab=40.0,
           inset_side=10.0, inset_top=20.0, inset_bottom=20.0,
           dims=False) -> Geometry:
    """Flat wicket-bag blank. Returns a Geometry (mm, y-up).

    Sections bottom->top: tab, body, wicket, wicket, body. Total height =
    tab + body + 2*wicket + body. The SAFE frame covers the body+wicket block
    only (above the tab), inset by inset_side / inset_top / inset_bottom.
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
    sy = y_tab + inset_bottom                # bottom sits above the tab joint
    sh = (H - inset_top) - sy                # top sits below the top edge
    g.rect(sx, sy, sw, sh, SAFE)

    # --- optional dimensions (INFO) --------------------------------------
    if dims:
        rx = width + 12.0                    # per-section dims column
        ox = width + 34.0                    # overall-height column
        _dim_v(g, rx, 0.0, y_tab, f"Tab {tab:g} mm")
        _dim_v(g, rx, y_tab, y_b1, f"Body {body:g} mm")
        _dim_v(g, rx, y_b1, y_w1, f"Wicket {wicket:g} mm")
        _dim_v(g, ox, 0.0, H, f"Height {H:g} mm")
        _dim_h(g, -12.0, 0.0, width, f"Width {width:g} mm")

    return g


if __name__ == "__main__":
    for (w, b, wk, tb) in [(240, 420, 60, 40), (300, 500, 80, 50)]:
        g = wicket(w, b, wk, tb)
        bb = tuple(round(v, 1) for v in g.bbox())
        print(f"{w}/{b}/{wk}/{tb}: bbox {bb} "
              f"size {round(bb[2]-bb[0],1)}x{round(bb[3]-bb[1],1)} "
              f"cutSeg {len(g.segs)}")
