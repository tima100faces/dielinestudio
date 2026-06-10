#!/usr/bin/env python3
"""Derive the panel grid from the reference: collect axis-aligned segments,
cluster their constant coordinate, report vertical (X) and horizontal (Y) fold
lines and their spacings -> basis for the parametric formula. mm, y-up."""
from extract_paths import run
import sys
cut, cre = run('samples/ref_14747.pdf')
recs = cut + cre

H_segs=[]; V_segs=[]   # (const_coord, span_min, span_max, length)
for r in recs:
    p=r['pts']
    for a,b in zip(p, p[1:]):
        (x1,y1),(x2,y2)=a,b
        if abs(y1-y2)<0.4 and abs(x1-x2)>2:      # horizontal
            H_segs.append((round((y1+y2)/2,1), min(x1,x2), max(x1,x2), abs(x1-x2)))
        elif abs(x1-x2)<0.4 and abs(y1-y2)>2:    # vertical
            V_segs.append((round((x1+x2)/2,1), min(y1,y2), max(y1,y2), abs(y1-y2)))

def cluster(vals, tol=1.2):
    vals=sorted(vals); out=[]; grp=[vals[0]]
    for v in vals[1:]:
        if v-grp[-1]<=tol: grp.append(v)
        else: out.append(grp); grp=[v]
    out.append(grp); return [round(sum(g)/len(g),1) for g in out]

def report(name, segs, axis):
    print(f"\n=== {name}: {len(segs)} segments ===")
    coords=cluster([s[0] for s in segs])
    print(f"{axis} fold/edge lines ({len(coords)}):", coords)
    print(f"spacings: {[round(b-a,1) for a,b in zip(coords,coords[1:])]}")
    # longest segments at each coord (the real panel folds)
    for c in coords:
        grp=[s for s in segs if abs(s[0]-c)<1.2]
        ln=max(grp,key=lambda s:s[3])
        print(f"  {axis}={c:7.1f}  longest span {ln[1]:.1f}->{ln[2]:.1f} (len {ln[3]:.1f}), {len(grp)} segs")

report("VERTICAL lines (x=const)", V_segs, "x")
report("HORIZONTAL lines (y=const)", H_segs, "y")
