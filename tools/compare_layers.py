import sys; sys.path.insert(0,'.')
import cairosvg
from tools.repro import g as refg   # reuse extracted reference geometry
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
OFFX, OFFY = 47.6, 96.6
mine = pizza_led(430,260,30,1.5)
xs=[OFFX,OFFY]; ys=[]
allx=[s.x1 for s in refg.segs]+[s.x2 for s in refg.segs]+[s.x1+OFFX for s in mine.segs]+[s.x2+OFFX for s in mine.segs]
ally=[s.y1 for s in refg.segs]+[s.y2 for s in refg.segs]+[s.y1+OFFY for s in mine.segs]+[s.y2+OFFY for s in mine.segs]
for a in mine.arcs:
    for px,py in a.sample(6): allx.append(px+OFFX); ally.append(py+OFFY)
minx,maxx,miny,maxy=min(allx),max(allx),min(ally),max(ally)
P=15; Wd=maxx-minx+2*P; Hd=maxy-miny+2*P
sx=lambda x:x-minx+P; sy=lambda y:maxy-y+P
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}mm" height="{Hd}mm" viewBox="0 0 {Wd} {Hd}">',f'<rect width="{Wd}" height="{Hd}" fill="white"/>']
for seg in refg.segs:
    s.append(f'<line x1="{sx(seg.x1):.1f}" y1="{sy(seg.y1):.1f}" x2="{sx(seg.x2):.1f}" y2="{sy(seg.y2):.1f}" stroke="#bbbbbb" stroke-width="0.7"/>')
for seg in mine.segs:
    col='#e51a24' if seg.layer==CUT else '#19a04d'; dash='' if seg.layer==CUT else 'stroke-dasharray="3 2"'
    s.append(f'<line x1="{sx(seg.x1+OFFX):.1f}" y1="{sy(seg.y1+OFFY):.1f}" x2="{sx(seg.x2+OFFX):.1f}" y2="{sy(seg.y2+OFFY):.1f}" stroke="{col}" stroke-width="0.9" {dash}/>')
for a in mine.arcs:
    pts=a.sample(5); d='M '+' L '.join(f'{sx(px+OFFX):.1f} {sy(py+OFFY):.1f}' for px,py in pts)
    col='#e51a24' if a.layer==CUT else '#19a04d'
    s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="0.9"/>')
s.append('</svg>')
open('samples/cmpL.svg','w').write('\n'.join(s))
cairosvg.svg2png(url='samples/cmpL.svg', write_to='samples/cmpL.png', output_width=1500)
print('ok')
