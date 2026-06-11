import sys; sys.path.insert(0,'.')
import cairosvg
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
def render(W,D,H,t,box,out,w=900):
    g=pizza_led(W,D,H,t); x0,y0,x1,y1=box
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{x1-x0}mm\" height=\"{y1-y0}mm\" viewBox=\"{x0} {-y1} {x1-x0} {y1-y0}\">',f'<rect x=\"{x0}\" y=\"{-y1}\" width=\"{x1-x0}\" height=\"{y1-y0}\" fill=\"white\"/>']
    for seg in g.segs:
        col='#e51a24' if seg.layer==CUT else '#0a8a0a';dash='' if seg.layer==CUT else 'stroke-dasharray=\"2 2\"'
        s.append(f'<line x1=\"{seg.x1:.2f}\" y1=\"{-seg.y1:.2f}\" x2=\"{seg.x2:.2f}\" y2=\"{-seg.y2:.2f}\" stroke=\"{col}\" stroke-width=\"0.9\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=w,background_color='white')
# left wall top corner at 430 and at 820x580 (same local box; left wall x in [-(H+6.6),0])
render(430,260,30,1.5,(-45,400,10,530),'samples/lw_430.png')
render(820,580,30,1.5,(-45,400,10,530),'samples/lw_820.png')
