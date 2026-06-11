"""Extract the parametric grid (fold anchor lines) from the reference DXF.
CUT = color 114 / Layer 1; CREASE = Layer 3 / color 230. Origin shifted to the
base-bottom lower-left fold so grid lines can be expressed vs W/D/H/t."""
import ezdxf
from collections import defaultdict
def walk(e,out):
    if e.dxftype()=='INSERT':
        for v in e.virtual_entities(): walk(v,out)
    else: out.append(e)
d=ezdxf.readfile('samples/14747_d-layers.dxf'); ents=[]
for e in d.modelspace(): walk(e,ents)
cre=[]; 
for e in ents:
    is_cre=(e.dxf.layer=='Layer 3') or e.dxf.color==230
    if e.dxftype()=='LINE' and is_cre:
        cre.append(((e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)))
# vertical & horizontal crease lines
V=[]; H=[]
for (x1,y1),(x2,y2) in cre:
    if abs(x1-x2)<0.5 and abs(y1-y2)>2: V.append(round((x1+x2)/2,1))
    elif abs(y1-y2)<0.5 and abs(x1-x2)>2: H.append(round((y1+y2)/2,1))
def cl(v,t=1.5):
    v=sorted(v); o=[]; g=[v[0]]
    for a in v[1:]:
        if a-g[-1]<=t: g.append(a)
        else: o.append(sum(g)/len(g)); g=[a]
    o.append(sum(g)/len(g)); return [round(x,1) for x in o]
vx=cl(V); hy=cl(H)
print('VERTICAL fold anchors x:', vx)
print('  spacings:', [round(b-a,1) for a,b in zip(vx,vx[1:])])
print('HORIZONTAL fold anchors y:', hy)
print('  spacings:', [round(b-a,1) for a,b in zip(hy,hy[1:])])
# shift origin to (base-left-fold, base-bottom-fold) = (vx after wall, hy after end)
print('\nReference dims: W=430 D=260 H=30 t=1.5')
