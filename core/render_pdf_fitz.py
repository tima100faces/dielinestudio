"""Render Geometry to a PDF with real OCG LAYERS (CUT / CREASE / INFO) via PyMuPDF.
CUT = red solid, CREASE = green dashed, INFO = title block (own layer).
Units mm; y-up geometry is flipped to PDF space. Returns PDF bytes."""
import fitz
from core.primitives import CUT, CREASE, INFO

MM = 72.0 / 25.4
COL = {CUT: (0.92, 0.10, 0.14), CREASE: (0.10, 0.62, 0.30), INFO: (0.12, 0.12, 0.12)}
LW = {CUT: 0.30, CREASE: 0.30, INFO: 0.20}


def render_pdf(geom, margin=15.0, title="dieline") -> bytes:
    minx, miny, maxx, maxy = geom.bbox()
    W = (maxx - minx) + 2 * margin
    H = (maxy - miny) + 2 * margin
    doc = fitz.open()
    page = doc.new_page(width=W * MM, height=H * MM)
    doc.set_metadata({"title": title})

    def X(x): return (x - minx + margin) * MM
    def Y(y): return (maxy - y + margin) * MM   # flip: fitz is y-down

    ocg = {lay: doc.add_ocg(name, on=True)
           for lay, name in ((CUT, "CUT"), (CREASE, "CREASE"), (INFO, "INFO"))}

    for lay in (INFO, CREASE, CUT):              # INFO under, CUT on top
        shp = page.new_shape()
        n = 0
        for s in geom.segs:
            if s.layer == lay:
                shp.draw_line((X(s.x1), Y(s.y1)), (X(s.x2), Y(s.y2))); n += 1
        for a in geom.arcs:
            if a.layer == lay:
                shp.draw_polyline([(X(px), Y(py)) for px, py in a.sample(2.0)]); n += 1
        if n:
            shp.finish(color=COL[lay], width=LW[lay] * MM,
                       dashes="[3 2] 0" if lay == CREASE else None,
                       closePath=False, oc=ocg[lay])
            shp.commit()

    for t in geom.texts:
        page.insert_text((X(t.x), Y(t.y)), t.s, fontsize=t.size,
                         color=COL[INFO], oc=ocg[INFO])
    return doc.tobytes()
