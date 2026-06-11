"""Render Geometry to a PDF with real OCG LAYERS (CUT / CREASE / INFO) via PyMuPDF.
CUT = red solid, CREASE = green dashed, INFO = title block (own layer).
Units mm; y-up geometry is flipped to PDF space. Returns PDF bytes."""
import fitz
from core.primitives import CUT, CREASE, INFO, SAFE

MM = 72.0 / 25.4
COL = {CUT: (0.92, 0.10, 0.14), CREASE: (0.10, 0.62, 0.30),
       INFO: (0.12, 0.12, 0.12), SAFE: (0.10, 0.71, 0.84)}
LW = {CUT: 0.30, CREASE: 0.30, INFO: 0.20, SAFE: 0.30}


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
           for lay, name in ((CUT, "CUT"), (CREASE, "CREASE"),
                             (INFO, "INFO"), (SAFE, "SAFE"))}
    DASH = {CREASE: "[3 2] 0", SAFE: "[4 2.5] 0"}

    for lay in (INFO, SAFE, CREASE, CUT):        # INFO under, CUT on top
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
                       dashes=DASH.get(lay), closePath=False, oc=ocg[lay])
            shp.commit()

    for t in geom.texts:
        pivot = fitz.Point(X(t.x), Y(t.y))
        kw = dict(fontsize=t.size, color=COL[t.layer], oc=ocg[t.layer])
        if t.rotation:
            # geometry rotation is CCW y-up; page space is y-down. Empirically
            # +rotation reads bottom-to-top, upright (see docs/wicket_dims_preview).
            m = fitz.Matrix(1, 1); m.prerotate(t.rotation)
            kw["morph"] = (pivot, m)
        page.insert_text(pivot, t.s, **kw)
    return doc.tobytes()
