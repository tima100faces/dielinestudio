import math, ezdxf, cairosvg
from collections import Counter
def walk(e, out):
    if e.dxftype()=='INSERT':
        for v in e.virtual_entities(): walk(v, out)
    else: out.append(e)
def bulge_arc(p0,p1,b,n=10):
    if abs(b)<1e-9: return [p0]
    import math as m
    x0,y0=p0; x1,y1=p1; dx,dy=x1-x0,y1-y0; chord=m.hypot(dx,dy)
    if chord<1e-9: return [p0]
    sag=b*chord/2; r=((chord/2)**2+sag**2)/(2*abs(sag))
    mx,my=(x0+x1)/2,(y0+y1)/2; nx,ny=-dy/chord,dx/chord
    h=r-abs(sag); s=1 if b>0 else -1
    cx,cy=mx - s*nx*h*0,my  # compute center properly
    # center: distance from midpoint along normal
    d=math.sqrt(max(r*r-(chord/2)**2,0))*(1 if abs(b)<1 else -1)*s
    cx,cy=mx+nx*d, my+ny*d
    a0=math.atan2(y0-cy,x0-cx); a1=math.atan2(y1-cy,x1-cx)
    if b>0 and a1<a0: a1+=2*math.pi
    if b<0 and a1>a0: a1-=2*math.pi
    return [(cx+r*math.cos(a0+(a1-a0)*i/n), cy+r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
def entity_pts(e):
    t=e.dxftype()
    if t=='LINE': return [[(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]]
    if t=='LWPOLYLINE':
        pts=list(e.get_points('xyb')); closed=e.closed; out=[]; poly=[]
        for i in range(len(pts)):
            x,y,b=pts[i]
            nx,ny,_=pts[(i+1)%len(pts)]
            if i==len(pts)-1 and not closed: poly.append((x,y)); break
            poly+=bulge_arc((x,y),(nx,ny),b)
        if closed: poly.append(poly[0])
        return [poly]
    if t in ('ARC','CIRCLE','SPLINE','ELLIPSE'):
        try: return [[(p.x,p.y) for p in e.flattening(0.2)]]
        except Exception: return []
    return []
def load(path,crease_test):
    d=ezdxf.readfile(path); ents=[]
    for e in d.modelspace(): walk(e,ents)
    items=[]
    for e in ents:
        if e.dxftype()=='MTEXT': continue
        for poly in entity_pts(e):
            if len(poly)>=2: items.append((crease_test(e),poly))
    return items,Counter(e.dxftype() for e in ents)
def render(items,out,w=1200):
    xs=[p[0] for _,pts in items for p in pts]; ys=[p[1] for _,pts in items for p in pts]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys);P=15
    W=maxx-minx+2*P;H=maxy-miny+2*P;sx=lambda x:x-minx+P;sy=lambda y:maxy-y+P
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
    for cre,pts in items:
        col='#19a04d' if cre else '#e51a24';dash='stroke-dasharray=\"4 2\"' if cre else ''
        s.append(f'<path d=\"M '+' L '.join(f'{sx(x):.2f} {sy(y):.2f}' for x,y in pts)+f'\" fill=\"none\" stroke=\"{col}\" stroke-width=\"0.9\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=w,background_color='white')
ref,types=load('samples/14747_d-layers.dxf', lambda e:(e.dxf.layer=='Layer 3') or e.dxf.color==230)
render(ref,'samples/ref_full2.png')
print('types',dict(types),'items',len(ref))
