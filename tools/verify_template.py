import sys; sys.path.insert(0,'.')
import cairosvg, ezdxf, math
from boxes.pizza_led import pizza_led, _load_template
from core.primitives import CUT, CREASE
# reference template polylines (already origin-shifted to local frame)
ref=_load_template()
def svg_overlay(out):
    mine=pizza_led(430,260,30,1.5)
    allx=[p[0] for _,pts in ref for p in pts]+[s.x1 for s in mine.segs]+[s.x2 for s in mine.segs]
    ally=[p[1] for _,pts in ref for p in pts]+[s.y1 for s in mine.segs]+[s.y2 for s in mine.segs]
    minx,maxx,miny,maxy=min(allx),max(allx),min(ally),max(ally);P=15
    W=maxx-minx+2*P;H=maxy-miny+2*P;sx=lambda x:x-minx+P;sy=lambda y:maxy-y+P
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
    for cre,pts in ref:
        s.append('<path d=\"M '+' L '.join(f'{sx(x):.2f} {sy(y):.2f}' for x,y in pts)+'\" fill=\"none\" stroke=\"#bbb\" stroke-width=\"1.4\"/>')
    for seg in mine.segs:
        col='#e51a24' if seg.layer==CUT else '#19a04d';dash='' if seg.layer==CUT else 'stroke-dasharray=\"3 2\"'
        s.append(f'<line x1=\"{sx(seg.x1):.2f}\" y1=\"{sy(seg.y1):.2f}\" x2=\"{sx(seg.x2):.2f}\" y2=\"{sy(seg.y2):.2f}\" stroke=\"{col}\" stroke-width=\"0.7\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=1300,background_color='white')
def svg_plain(g,out):
    xs=[s.x1 for s in g.segs]+[s.x2 for s in g.segs];ys=[s.y1 for s in g.segs]+[s.y2 for s in g.segs]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys);P=15
    W=maxx-minx+2*P;H=maxy-miny+2*P;sx=lambda x:x-minx+P;sy=lambda y:maxy-y+P
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
    for seg in g.segs:
        col='#e51a24' if seg.layer==CUT else '#19a04d';dash='' if seg.layer==CUT else 'stroke-dasharray=\"3 2\"'
        s.append(f'<line x1=\"{sx(seg.x1):.2f}\" y1=\"{sy(seg.y1):.2f}\" x2=\"{sx(seg.x2):.2f}\" y2=\"{sy(seg.y2):.2f}\" stroke=\"{col}\" stroke-width=\"0.8\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=1000,background_color='white')
svg_overlay('samples/tmpl_overlay430.png')
svg_plain(pizza_led(580,260,30,1.5),'samples/tmpl_580.png')
print('ok')
