#!/usr/bin/env python3
"""Dieline extractor (pdfminer.six 2026): device subclass captures CTM-applied
points + dash state; interpreter.do_gs resolves ExtGState /D so creases (dashed)
are split from cuts (solid). Output in mm, y-up (PDF native)."""
import sys
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt
from pdfminer.pdftypes import resolve1, list_value

PT2MM = 25.4/72.0

class Rec(PDFLayoutAnalyzer):
    def __init__(self, rm):
        super().__init__(rm)
        self.recs = []
    def paint_path(self, gs, stroke, fill, evenodd, path):
        if not stroke:
            return
        dash = getattr(gs, 'dash', None)
        dashed = bool(dash and dash[0])
        pts = []
        for seg in path:
            c = seg[1:]
            for i in range(0, len(c), 2):
                x, y = apply_matrix_pt(self.ctm, (c[i], c[i+1]))
                pts.append((round(x*PT2MM, 2), round(y*PT2MM, 2)))
        if pts:
            self.recs.append({'dashed': dashed, 'sc': gs.scolor,
                              'ops': ''.join(s[0] for s in path), 'pts': pts})

class Interp(PDFPageInterpreter):
    def do_gs(self, name):
        try:
            eg = resolve1(self.resources.get('ExtGState'))
            d = resolve1(eg[name.name])
            if 'D' in d:
                arr, ph = list_value(d['D'])
                self.graphicstate.dash = (list_value(arr), ph)
        except Exception:
            pass

def run(path):
    fp = open(path, 'rb')
    doc = PDFDocument(PDFParser(fp))
    rm = PDFResourceManager()
    dev = Rec(rm)
    it = Interp(rm, dev)
    for pg in PDFPage.create_pages(doc):
        it.process_page(pg)
    R = dev.recs
    cut = [r for r in R if not r['dashed']]
    cre = [r for r in R if r['dashed']]
    xs = [p[0] for r in R for p in r['pts']]; ys = [p[1] for r in R for p in r['pts']]
    print(f"BBox mm x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}] "
          f"=> {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f}")
    print(f"Stroked: {len(R)}  CUT={len(cut)}  CREASE={len(cre)}")
    fp.close()
    return cut, cre

if __name__ == '__main__':
    cut, cre = run(sys.argv[1] if len(sys.argv) > 1 else 'samples/ref_14747.pdf')
    print("\n--- CREASE folds (dashed), mm ---")
    for r in cre:
        xs=[p[0] for p in r['pts']]; ys=[p[1] for p in r['pts']]
        print(f"  ops={r['ops'][:10]:10} pts={len(r['pts']):2} x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}]")
