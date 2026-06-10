"""Load the EXACT cut/crease geometry from the layered reference into our model
and render it, to confirm a 1:1 capture before building the parametric template."""
import sys; sys.path.insert(0,'.')
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.utils import apply_matrix_pt
from core.primitives import Geometry, CUT, CREASE
from core.render_svg import render_svg
import cairosvg
PT2MM=25.4/72.0
class Rec(PDFLayoutAnalyzer):
    def __init__(s,rm): super().__init__(rm); s.g=Geometry()
    def paint_path(s,gs,stroke,fill,eo,path):
        if not stroke: return
        c=gs.scolor
        crease = isinstance(c,(list,tuple)) and tuple(round(v,1) for v in c)==(0.0,1.0,0.0,0.0)
        layer = CREASE if crease else CUT
        pts=[]
        for seg in path:
            cc=seg[1:]
            for i in range(0,len(cc),2):
                x,y=apply_matrix_pt(s.ctm,(cc[i],cc[i+1])); pts.append((x*PT2MM,y*PT2MM))
        for a,b in zip(pts,pts[1:]): s.g.line(a[0],a[1],b[0],b[1],layer)
fp=open('samples/ref_14747_layers.pdf','rb')
doc=PDFDocument(PDFParser(fp)); rm=PDFResourceManager(); dev=Rec(rm); it=PDFPageInterpreter(rm,dev)
for pg in PDFPage.create_pages(doc): it.process_page(pg)
g=dev.g
svg=render_svg(g, mode='plain')
open('samples/repro.svg','w').write(svg)
cairosvg.svg2png(url='samples/repro.svg', write_to='samples/repro.png', output_width=1400, background_color='white')
cre=sum(1 for s in g.segs if s.layer==CREASE)
print('captured segs', len(g.segs), 'crease', cre, 'cut', len(g.segs)-cre, 'bbox', tuple(round(v,1) for v in g.bbox()))
