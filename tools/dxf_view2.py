import ezdxf, cairosvg
def explode(e, out):
    if e.dxftype()=='INSERT':
        for v in e.virtual_entities(): explode(v, out)
    else: out.append(e)
def load(path, crease_test):
    d=ezdxf.readfile(path); ents=[]
    for e in d.modelspace(): explode(e, ents)
    items=[]
    for e in ents:
        t=e.dxftype()
        if t=='MTEXT': continue
        try:
            if t=='LINE': pts=[(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]
            else: pts=[(p.x,p.y) for p in e.flattening(0.2)]
        except Exception: continue
        if len(pts)>=2: items.append((crease_test(e),pts,t))
    return items
def render(items,out,w=1200):
    xs=[p[0] for _,pts,_ in items for p in pts]; ys=[p[1] for _,pts,_ in items for p in pts]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); P=15
    W=maxx-minx+2*P; H=maxy-miny+2*P
    sx=lambda x:x-minx+P; sy=lambda y:maxy-y+P
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
    for cre,pts,t in items:
        col='#19a04d' if cre else '#e51a24'; dash='stroke-dasharray=\"4 2\"' if cre else ''
        d='M '+' L '.join(f'{sx(x):.2f} {sy(y):.2f}' for x,y in pts)
        s.append(f'<path d=\"{d}\" fill=\"none\" stroke=\"{col}\" stroke-width=\"0.9\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(),write_to=out,output_width=w,background_color='white')
    from collections import Counter
    return len(items), Counter(t for _,_,t in items)
ref=load('samples/14747_d-layers.dxf', lambda e:(e.dxf.layer=='Layer 3') or e.dxf.color==230)
n,types=render(ref,'samples/ref_full.png')
print('ref items',n,'types',dict(types))
