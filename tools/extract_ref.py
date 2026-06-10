#!/usr/bin/env python3
"""Extract dieline geometry from a reference PDF.
Walks vector paths via pdfminer, classifies CUT vs CREASE by dash pattern,
converts to millimetres (origin bottom-left, y-up), and summarises structure.
"""
import sys, math
from collections import Counter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTCurve, LTLine, LTRect, LTFigure

PT2MM = 25.4 / 72.0

def walk(obj):
    for el in obj:
        if isinstance(el, (LTCurve, LTLine, LTRect)):
            yield el
        if isinstance(el, LTFigure):
            yield from walk(el)

def main(path):
    cuts, creases, other = [], [], []
    colors = Counter()
    xs, ys = [], []
    for page in extract_pages(path):
        for el in walk(page):
            stroke = getattr(el, "stroking_color", None)
            if stroke is None:           # unstroked fill (text/marks) -> skip
                continue
            dash = getattr(el, "dashing_style", None)  # (array, phase) or None
            pts = getattr(el, "pts", None) or [(el.x0, el.y0), (el.x1, el.y1)]
            pts_mm = [(round(x*PT2MM, 2), round(y*PT2MM, 2)) for x, y in pts]
            for x, y in pts_mm:
                xs.append(x); ys.append(y)
            colors[tuple(round(c,2) for c in stroke) if isinstance(stroke,(list,tuple)) else stroke] += 1
            dashed = bool(dash and dash[0])
            rec = {"pts": pts_mm, "stroke": stroke, "dash": dash, "n": len(pts_mm)}
            (creases if dashed else cuts).append(rec)
    print(f"FILE: {path}")
    print(f"BBox mm: x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}]  "
          f"=> {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} mm")
    print(f"Stroked subpaths: total={len(cuts)+len(creases)}  CUT(solid)={len(cuts)}  CREASE(dashed)={len(creases)}")
    print("Stroke colors (count):")
    for c, n in colors.most_common(8):
        print(f"   {c}: {n}")
    # segment-length histogram for creases (helps spot double-crease gaps)
    print("\nSample CREASE subpaths (first 12, as mm point lists):")
    for r in creases[:12]:
        print("  ", r["pts"], "dash=", r["dash"])
    return cuts, creases

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "samples/ref_14747.pdf")
