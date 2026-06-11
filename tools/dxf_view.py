import sys, ezdxf, cairosvg
def load(path, crease_test):
    d=ezdxf.readfile(path); msp=d.modelspace(); items=[]
    def emit(e):
        t=e.dxftype()
        if t=='MTEXT': return
        try:
            if t=='LINE': pts=[(e.dxf.start.x,e.dxf.start.y),(e.dxf.end.x,e.dxf.end.y)]
            else: pts=[(p.x,p.y) for p in e.flattening(0.3)]
        except Exception: return
        if len(pts)<2: return
        items.append((crease_test(e), pts))
    for e in msp:
        if e.dxftype()=='INSERT':
            for v in e.virtual_entities(): emit(v)
        else: emit(e)
    return items
def render(items, out):
    xs=[p[0] for _,pts in items for p in pts]; ys=[p[1] for _,pts in items for p in pts]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys); P=15
    W=maxx-minx+2*P; H=maxy-miny+2*P
    sx=lambda x:x-minx+P; sy=lambda y:maxy-y+P
    s=[f'<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{W}mm\" height=\"{H}mm\" viewBox=\"0 0 {W} {H}\">',f'<rect width=\"{W}\" height=\"{H}\" fill=\"white\"/>']
    for cre,pts in items:
        col='#19a04d' if cre else '#e51a24'; dash='stroke-dasharray=\"4 2\"' if cre else ''
        d='M '+' L '.join(f'{sx(x):.2f} {sy(y):.2f}' for x,y in pts)
        s.append(f'<path d=\"{d}\" fill=\"none\" stroke=\"{col}\" stroke-width=\"0.8\" {dash}/>')
    s.append('</svg>')
    cairosvg.svg2png(bytestring='\n'.join(s).encode(), write_to=out, output_width=1100, background_color='white')
    return len(items)

ref=load('samples/14747_d-layers.dxf', lambda e: (e.dxf.layer=='Layer 3') or e.dxf.color==230)
mine=load('samples/pizza_led_580x260x30.dxf', lambda e: e.dxf.color==114)
print('ref items',render(ref,'samples/ref_dxf.png'),' mine items',render(mine,'samples/mine_dxf.png'))
