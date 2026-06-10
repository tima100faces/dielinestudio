#!/usr/bin/env python3
"""Render extracted reference geometry to PNG via cairosvg, with the panel grid
(long fold lines) annotated, so panels can be labelled and the parametric
formula finalised. Output mm coords, y flipped to screen."""
from extract_paths import run
import cairosvg, math

cut, cre = run('samples/ref_14747.pdf')
recs = cut + cre
xs=[p[0] for r in recs for p in r['pts']]; ys=[p[1] for r in recs for p in r['pts']]
minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
W=maxx-minx; H=maxy-miny
PAD=20
def sx(x): return x-minx+PAD
def sy(y): return (maxy-y)+PAD       # flip y for screen
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W+2*PAD}mm" height="{H+2*PAD}mm" viewBox="0 0 {W+2*PAD} {H+2*PAD}">']
svg.append(f'<rect width="{W+2*PAD}" height="{H+2*PAD}" fill="white"/>')
# all geometry in thin black
for r in recs:
    p=r['pts']
    d='M '+' L '.join(f'{sx(x):.1f} {sy(y):.1f}' for x,y in p)
    svg.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="0.4"/>')
# long folds: vertical (x const, span>40) red, horizontal (y const, span>40) blue
def segs(axis):
    out=[]
    for r in recs:
        for a,b in zip(r['pts'],r['pts'][1:]):
            (x1,y1),(x2,y2)=a,b
            if axis=='v' and abs(x1-x2)<0.4 and abs(y1-y2)>40: out.append(((x1+x2)/2,min(y1,y2),max(y1,y2)))
            if axis=='h' and abs(y1-y2)<0.4 and abs(x1-x2)>40: out.append(((y1+y2)/2,min(x1,x2),max(x1,x2)))
    return out
def cl(vals,tol=1.5):
    if not vals: return []
    vals=sorted(vals);o=[];g=[vals[0]]
    for v in vals[1:]:
        if v-g[-1]<=tol:g.append(v)
        else:o.append(g);g=[v]
    o.append(g);return [sum(z)/len(z) for z in o]
V=segs('v'); Hh=segs('h')
for cx in cl([s[0] for s in V]):
    svg.append(f'<line x1="{sx(cx):.1f}" y1="0" x2="{sx(cx):.1f}" y2="{H+2*PAD}" stroke="red" stroke-width="0.8" stroke-dasharray="4 3"/>')
    svg.append(f'<text x="{sx(cx):.1f}" y="12" font-size="11" fill="red" text-anchor="middle">x{cx:.0f}</text>')
for cy in cl([s[0] for s in Hh]):
    svg.append(f'<line x1="0" y1="{sy(cy):.1f}" x2="{W+2*PAD}" y2="{sy(cy):.1f}" stroke="blue" stroke-width="0.8" stroke-dasharray="4 3"/>')
    svg.append(f'<text x="6" y="{sy(cy)-2:.1f}" font-size="11" fill="blue">y{cy:.0f}</text>')
svg.append("</svg>")
open("samples/overlay.svg","w").write("\n".join(svg))
cairosvg.svg2png(url="samples/overlay.svg", write_to="samples/overlay.png", output_width=1500)
print("wrote samples/overlay.png", f"({W:.0f}x{H:.0f} mm)")
