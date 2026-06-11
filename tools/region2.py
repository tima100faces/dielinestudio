import sys; sys.path.insert(0,'.')
import cairosvg
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
W,D,H,t=820,580,30,1.5
g=pizza_led(W,D,H,t)
# report slot feature sizes (closed-ish small loops in base bottom)
print('=== small closed features (slots/tabs) sizes ===')
# group segs is hard; instead measure: list cut segs that are short horizontals near y in [-100,30]
def render(box,out,w=1400):
    x0,y0,x1,y1=box
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{x1-x0}mm\" height=\"{y1-y0}mm\" viewBox=\"{x0} {-y1} {x1-x0} {y1-y0}\">',f'<rect x=\"{x0}\" y=\"{-y1}\" width=\"{x1-x0}\" height=\"{y1-y0}\" fill=\"white\"/>']
    for seg in g.segs:
        col='#e51a24' if seg.layer==CUT else '#0a8a0a';dash='' if seg.layer==CUT else 'stroke-dasharray=\"2 2\"'
        s.append(f'<line x1=\"{seg.x1:.2f}\" y1=\"{-seg.y1:.2f}\" x2=\"{seg.x2:.2f}\" y2=\"{-seg.y2:.2f}\" stroke=\"{col}\" stroke-width=\"1.0\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=w,background_color='white')
render((-50,-100,620,40),'samples/rb_bottom.png')   # bottom band: slots+tabs+left wall corner
print('bbox',tuple(round(v,1) for v in g.bbox()))
