"""LED display box 14747 — book-style tray + folding lid (side-by-side blank).
Reverse-engineered 1:1 from the layered production file (ref_14747_layers.pdf),
parametrised on W x D x H x t. Mechanics (confirmed):
  - base = bottom + left wall + back/spine wall (lid hinges off it) + 2 end walls;
    each end wall has a 180-deg fold-back flap (DOUBLE crease) carrying lock TABS
    that drop into the OVAL slots in the bottom near each end.
  - lid folds over; its right flap (with grab notches) tucks behind the base left
    wall and locks. Softened (rounded) lid corners.
Coords: mm, y-up, base-bottom lower-left = (0,0).  x: width(D)  y: length(W)
All allowances are constants up top (measured on 14747; calibrate per board).
"""
import math
from core.primitives import Geometry, CUT, CREASE


def pizza_led(W=430.0, D=260.0, H=30.0, t=1.5):
    # ---- calibration (measured on 14747) -------------------------------
    BW   = D + 2 * t          # base bottom width  (260 -> 263)
    BL   = W + 20.0           # base bottom length (430 -> 450)
    LW   = D + 4 * t          # lid width          (260 -> 266)
    LL   = W + 2.0            # lid length         (430 -> 432)
    LWALL = H + 6.6           # base left wall
    SPINE = H + 7.9           # back/spine wall (hinge)
    RWALL = H + 6.5           # lid right flap
    EWALL = H + 7.9           # end wall height
    EFLAP = 41.0              # end fold-back flap depth
    DOUBLE_T = 0.6            # caliper at/above which 180-deg folds get a double crease
    DCG  = 7.0                # double-crease gap
    LIDR = 30.0              # softened lid corner radius
    SLOT_L, SLOT_H = 48.0, 10.0      # oval lock slot
    SLOT_OFF = BW * 0.25      # slot centre offset from bottom centre (+/-)
    TAB_W, TAB_D = 44.0, 9.0  # lock tab on the end flap
    GRAB_R = 12.0             # lid grab-notch radius
    dbl = (t >= DOUBLE_T)

    g = Geometry()
    C = lambda *a: g.line(*a, CREASE)
    K = lambda *a: g.line(*a, CUT)

    # X grid
    x0 = 0.0; xBW = BW; xSP = BW + SPINE; xLF = xSP + LW; xLE = xLF + RWALL
    xLWo = -LWALL
    cxB = BW / 2.0
    # lid Y (centred in base length)
    ly0 = (BL - LL) / 2.0; ly1 = BL - ly0; cyL = BL / 2.0

    # ===================== CREASES =====================
    C(x0, 0, x0, BL)                  # left wall fold
    C(xBW, 0, xBW, BL)                # base->spine fold
    C(xSP, 0, xSP, BL)                # spine->lid hinge
    C(xLF, ly0, xLF, ly1)            # lid->right flap fold
    C(x0, 0, xBW, 0)                  # bottom end-wall fold
    C(x0, BL, xBW, BL)               # top end-wall fold
    C(xSP, ly0, xLF, ly0)            # lid bottom end-flap fold
    C(xSP, ly1, xLF, ly1)            # lid top end-flap fold

    def end_creases(sign, y0):
        yw = y0 + sign * EWALL                       # end wall outer / flap fold
        C(x0, yw, xBW, yw)
        if dbl:
            C(x0, yw + sign * DCG, xBW, yw + sign * DCG)   # double crease
    end_creases(-1, 0)
    end_creases(+1, BL)

    # ===================== CUTS =====================
    # --- left wall outer edge + glue corners ---
    K(xLWo, 0, xLWo, BL)
    K(xLWo, 0, x0, 0); K(xLWo, BL, x0, BL)

    # --- spine side edges ---
    K(xBW, 0, xSP, 0); K(xBW, BL, xSP, BL)

    # --- end assemblies (bottom & top) ---
    def end_assembly(sign, y0):
        yw  = y0 + sign * EWALL              # fold-back line
        yf  = yw + sign * (DCG + EFLAP)      # flap outer edge
        K(x0, y0, x0, yw); K(xBW, y0, xBW, yw)          # end-wall side edges
        K(x0, yw, x0, yf); K(xBW, yw, xBW, yf)          # flap side edges
        # flap outer edge with two lock tabs poking out
        c1, c2 = cxB - SLOT_OFF, cxB + SLOT_OFF
        pts = [(x0, yf)]
        for c in (c1, c2):
            pts += [(c - TAB_W/2, yf), (c - TAB_W/2, yf + sign*TAB_D),
                    (c + TAB_W/2, yf + sign*TAB_D), (c + TAB_W/2, yf)]
        pts.append((xBW, yf))
        g.polyline(pts, CUT)
        # oval lock slots in the bottom near this end
        for c in (c1, c2):
            g.stadium(c, y0 + sign * (SLOT_H/2 + 1), SLOT_L, SLOT_H, CUT)
    end_assembly(-1, 0)
    end_assembly(+1, BL)

    # --- lid: rounded outer corners + end-flap edges + right flap w/ grab notches ---
    # lid left side is the hinge (crease at xSP); cut the top/bottom end-flap outer edges
    # top & bottom lid end flaps fold along ly1/ly0; their outer edges are cut at panel ends
    # right flap with two grab notches and softened corners
    K(xSP, ly1, xLF - LIDR, ly1)
    g.arc(xLF - LIDR, ly1 - LIDR, LIDR, 90, 0, CUT)       # top-right round into flap
    K(xLF, ly1 - LIDR, xLF, ly0 + LIDR)                  # (flap base)
    K(xSP, ly0, xLF - LIDR, ly0)
    g.arc(xLF - LIDR, ly0 + LIDR, LIDR, 270, 360, CUT)   # bottom-right round
    # right flap outer edge with grab notches
    K(xLF, ly1 - LIDR, xLE, ly1 - LIDR)
    K(xLE, ly1 - LIDR, xLE, ly0 + LIDR)
    K(xLE, ly0 + LIDR, xLF, ly0 + LIDR)
    g.arc(xLE, cyL + LL*0.28, GRAB_R, 90, 270, CUT)       # grab notch upper
    g.arc(xLE, cyL - LL*0.28, GRAB_R, 90, 270, CUT)       # grab notch lower

    return g


if __name__ == "__main__":
    for (w, d, h, t) in [(430, 260, 30, 1.5), (300, 200, 40, 2.0)]:
        g = pizza_led(w, d, h, t)
        b = tuple(round(v, 1) for v in g.bbox())
        cre = sum(1 for s in g.segs if s.layer == CREASE)
        print(f"{w}x{d}x{h} t{t}: bbox {b} size {round(b[2]-b[0],1)}x{round(b[3]-b[1],1)} "
              f"creases {cre} cuts {len(g.segs)-cre} arcs {len(g.arcs)}")
