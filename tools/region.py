import sys; sys.path.insert(0,'.')
import cairosvg
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
g=pizza_led(430,260,30,1.5)
def render(box,out,w=1200):
    x0,y0,x1,y1=box
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{x1-x0}mm\" height=\"{y1-y0}mm\" viewBox=\"{x0} {y0} {x1-x0} {y1-y0}\">',f'<rect x=\"{x0}\" y=\"{y0}\" width=\"{x1-x0}\" height=\"{y1-y0}\" fill=\"white\"/>']
    for seg in g.segs:
        # flip y handled by negating in viewBox? draw in y-up then transform
        col='#e51a24' if seg.layer==CUT else '#0a8a0a';dash='' if seg.layer==CUT else 'stroke-dasharray=\"1.5 1.5\"'
        s.append(f'<line x1=\"{seg.x1:.2f}\" y1=\"{-seg.y1:.2f}\" x2=\"{seg.x2:.2f}\" y2=\"{-seg.y2:.2f}\" stroke=\"{col}\" stroke-width=\"0.8\" {dash}/>')
    s.append('</svg>')
    # viewBox uses negated y; adjust
    open('/tmp/r.svg','w')
    cairosvg.svg2png(bytestring=('\n'.join(s)).replace(f'viewBox=\"{x0} {y0}',f'viewBox=\"{x0} {-y1}').encode(),write_to=out,output_width=w,background_color='white')
render((520,360,610,475),'samples/r_topright.png')
render((230,400,310,470),'samples/r_spine.png')
render((-65,400,5,475),'samples/r_lefttab.png')
print('ok')
