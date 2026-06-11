import sys; sys.path.insert(0,'.')
import cairosvg
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
g=pizza_led(430,260,30,1.5)
xs=[s.x1 for s in g.segs]+[s.x2 for s in g.segs];ys=[s.y1 for s in g.segs]+[s.y2 for s in g.segs]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys);P=10
W=maxx-minx+2*P;H=maxy-miny+2*P;sx=lambda x:x-minx+P;sy=lambda y:maxy-y+P
s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
for seg in g.segs:
    col='#e51a24' if seg.layer==CUT else '#0a8a0a';dash='' if seg.layer==CUT else 'stroke-dasharray=\"2 2\"'
    s.append(f'<line x1=\"{sx(seg.x1):.2f}\" y1=\"{sy(seg.y1):.2f}\" x2=\"{sx(seg.x2):.2f}\" y2=\"{sy(seg.y2):.2f}\" stroke=\"{col}\" stroke-width=\"1.1\" {dash}/>')
s.append('</svg>')
cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to='samples/hi.png',output_width=1500,background_color='white')
print('ok',round(W),round(H))
