"""Render Geometry to a vector PDF via reportlab.

CUT = red solid, CREASE = green dashed, INFO = black text + thin lines.
Arcs are emitted as true PDF curves (reportlab arcTo -> bezier), never polylines.
Units mm, 1:1, y-up (native PDF). Returns PDF bytes.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from core.primitives import CUT, CREASE, INFO

CUT_RGB = (0.92, 0.10, 0.14)      # red
CREASE_RGB = (0.10, 0.62, 0.30)   # green
INFO_RGB = (0.10, 0.10, 0.10)     # near-black
LW_CUT = 0.30
LW_CREASE = 0.30
LW_INFO = 0.20


def render_pdf(geom, margin=15.0, title="dieline") -> bytes:
    minx, miny, maxx, maxy = geom.bbox()
    w = (maxx - minx) + 2 * margin
    h = (maxy - miny) + 2 * margin
    ox, oy = margin - minx, margin - miny     # translate geometry into page

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w * mm, h * mm))
    c.setTitle(title)

    def X(x): return (x + ox) * mm
    def Y(y): return (y + oy) * mm

    def stroke_segs(layer, rgb, lw, dash):
        c.setStrokeColorRGB(*rgb); c.setLineWidth(lw * mm)
        c.setDash(dash if dash else [], 0)
        items = [s for s in geom.segs if s.layer == layer]
        if not items:
            return
        for s in items:
            c.line(X(s.x1), Y(s.y1), X(s.x2), Y(s.y2))

    def stroke_arcs(layer, rgb, lw, dash):
        items = [a for a in geom.arcs if a.layer == layer]
        if not items:
            return
        c.setStrokeColorRGB(*rgb); c.setLineWidth(lw * mm)
        c.setDash(dash if dash else [], 0)
        for a in items:
            p = c.beginPath()
            sx, sy = a.start()
            p.moveTo(X(sx), Y(sy))
            # bounding box of the full circle, in device units
            p.arcTo(X(a.cx - a.r), Y(a.cy - a.r), X(a.cx + a.r), Y(a.cy + a.r),
                    startAng=a.a0, extent=(a.a1 - a.a0))
            c.drawPath(p, stroke=1, fill=0)

    # INFO first (under), then CREASE, then CUT on top
    stroke_segs(INFO, INFO_RGB, LW_INFO, None)
    stroke_arcs(INFO, INFO_RGB, LW_INFO, None)
    stroke_segs(CREASE, CREASE_RGB, LW_CREASE, [2, 1.5])
    stroke_arcs(CREASE, CREASE_RGB, LW_CREASE, [2, 1.5])
    stroke_segs(CUT, CUT_RGB, LW_CUT, None)
    stroke_arcs(CUT, CUT_RGB, LW_CUT, None)

    # INFO texts
    c.setDash([], 0); c.setFillColorRGB(*INFO_RGB)
    for t in geom.texts:
        c.setFont("Helvetica", t.size)
        c.drawString(X(t.x), Y(t.y), t.s)

    c.showPage(); c.save()
    return buf.getvalue()
