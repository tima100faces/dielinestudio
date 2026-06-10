"""Overlay my generated dieline over the reference for 1:1 visual check.
Reference in light grey; my CUT red, CREASE green dashed. Aligned so my base
bottom-left (0,0) maps onto the reference base corner (x=118.4, y=158)."""
import sys, cairosvg
sys.path.insert(0, '.')
from extract_paths import run
from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE

OFFX, OFFY = 118.4, 158.0     # ref base-corner in ref mm

ref_cut, ref_cre = run('samples/ref_14747.pdf')
ref = ref_cut + ref_cre
g = pizza_led()

xs = [OFFX]; ys = [OFFY]
for r in ref:
    for p in r['pts']: xs.append(p[0]); ys.append(p[1])
b = g.bbox(); xs += [b[0]+OFFX, b[2]+OFFX]; ys += [b[1]+OFFY, b[3]+OFFY]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
PAD = 15; Wd = maxx-minx+2*PAD; Hd = maxy-miny+2*PAD
def sx(x): return x-minx+PAD
def sy(y): return maxy-y+PAD

s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}mm" height="{Hd}mm" viewBox="0 0 {Wd} {Hd}">',
     f'<rect width="{Wd}" height="{Hd}" fill="white"/>']
# reference grey
for r in ref:
    d = 'M ' + ' L '.join(f'{sx(x):.1f} {sy(y):.1f}' for x, y in r['pts'])
    s.append(f'<path d="{d}" fill="none" stroke="#c8c8c8" stroke-width="0.6"/>')
# mine
def seg_svg(seg, col, dash):
    return (f'<line x1="{sx(seg.x1+OFFX):.1f}" y1="{sy(seg.y1+OFFY):.1f}" '
            f'x2="{sx(seg.x2+OFFX):.1f}" y2="{sy(seg.y2+OFFY):.1f}" '
            f'stroke="{col}" stroke-width="0.9" {dash}/>')
for seg in g.segs:
    if seg.layer == CUT:  s.append(seg_svg(seg, '#e51a24', ''))
    else: s.append(seg_svg(seg, '#19a04d', 'stroke-dasharray="3 2"'))
for a in g.arcs:
    pts = a.sample(4)
    d = 'M ' + ' L '.join(f'{sx(px+OFFX):.1f} {sy(py+OFFY):.1f}' for px, py in pts)
    col = '#e51a24' if a.layer == CUT else '#19a04d'
    s.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="0.9"/>')
s.append('</svg>')
open('samples/compare.svg', 'w').write('\n'.join(s))
cairosvg.svg2png(url='samples/compare.svg', write_to='samples/compare.png', output_width=1500)
print('wrote samples/compare.png')
