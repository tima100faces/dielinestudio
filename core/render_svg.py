"""Render Geometry to an SVG string (web preview). Arcs are sampled to polylines
(fine enough for preview; the production PDF keeps true curves). y is flipped to
screen space. mode='preview' adds a dark background; mode='plain' is transparent.
"""
from xml.sax.saxutils import escape
from core.primitives import CUT, CREASE, INFO, SAFE

COL = {CUT: "#e51a24", CREASE: "#19a04d", INFO: "#9aa6b2", SAFE: "#19b6d6"}


def render_svg(geom, margin=15.0, mode="preview", bg="#0d1117") -> str:
    minx, miny, maxx, maxy = geom.bbox()
    w = (maxx - minx) + 2 * margin
    h = (maxy - miny) + 2 * margin

    def X(x): return round(x - minx + margin, 2)
    def Y(y): return round(maxy - y + margin, 2)   # flip y

    layers = {CUT: [], CREASE: [], INFO: [], SAFE: []}
    for s in geom.segs:
        layers[s.layer].append(
            f'<line x1="{X(s.x1)}" y1="{Y(s.y1)}" x2="{X(s.x2)}" y2="{Y(s.y2)}"/>')
    for a in geom.arcs:
        pts = a.sample(4.0)
        d = "M " + " L ".join(f"{X(px)} {Y(py)}" for px, py in pts)
        layers[a.layer].append(f'<path d="{d}" fill="none"/>')

    texts = "".join(
        f'<text x="{X(t.x)}" y="{Y(t.y)}" font-size="{t.size}" '
        f'font-family="Helvetica,Arial,sans-serif" fill="{COL[INFO]}">{escape(t.s)}</text>'
        for t in geom.texts)

    bgrect = f'<rect width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>' if mode == "preview" else ""
    size = ('preserveAspectRatio="xMidYMid meet"' if mode == "preview"
            else f'width="{w:.2f}mm" height="{h:.2f}mm"')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" {size} viewBox="0 0 {w:.2f} {h:.2f}">
{bgrect}
<g stroke="{COL[INFO]}" stroke-width="0.2" fill="none">{''.join(layers[INFO])}</g>
<g stroke="{COL[SAFE]}" stroke-width="0.5" stroke-dasharray="4,2.5" fill="none">{''.join(layers[SAFE])}</g>
<g stroke="{COL[CREASE]}" stroke-width="0.5" stroke-dasharray="2.5,1.8" fill="none">{''.join(layers[CREASE])}</g>
<g stroke="{COL[CUT]}" stroke-width="0.5" fill="none">{''.join(layers[CUT])}</g>
{texts}
</svg>'''
