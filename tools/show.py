import sys, cairosvg
sys.path.insert(0,'.')
from boxes.pizza_led import pizza_led
from core.render_svg import render_svg
W=float(sys.argv[1]); D=float(sys.argv[2]); H=float(sys.argv[3]); t=float(sys.argv[4]) if len(sys.argv)>4 else 1.5
g=pizza_led(W,D,H,t)
svg=render_svg(g, mode='plain')
open('samples/show.svg','w').write(svg)
cairosvg.svg2png(url='samples/show.svg', write_to='samples/show.png', output_width=900, background_color='white')
print('bbox', tuple(round(v,1) for v in g.bbox()))
