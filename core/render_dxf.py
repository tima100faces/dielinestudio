"""Render Geometry to DXF with real LAYERS (CUT / CREASE / INFO) and TRUE arcs.
Illustrator imports DXF layers as Illustrator layers (PDF OCG it does not).
CUT = ACI 1 (red), CREASE = ACI 3 (green) dashed, INFO = ACI 8. Units: mm."""
import io
import ezdxf
from core.primitives import CUT, CREASE, INFO

LAYER = {CUT: "CUT", CREASE: "CREASE", INFO: "INFO"}


def render_dxf(geom, title="dieline") -> bytes:
    doc = ezdxf.new(setup=True)            # setup=True loads standard linetypes (DASHED)
    doc.units = 4                          # millimetres
    doc.layers.add("CUT", color=1)
    doc.layers.add("CREASE", color=3, linetype="DASHED")
    doc.layers.add("INFO", color=8)
    msp = doc.modelspace()

    for s in geom.segs:
        msp.add_line((s.x1, s.y1), (s.x2, s.y2),
                     dxfattribs={"layer": LAYER[s.layer]})
    for a in geom.arcs:
        msp.add_arc((a.cx, a.cy), a.r, min(a.a0, a.a1), max(a.a0, a.a1),
                    dxfattribs={"layer": LAYER[a.layer]})
    for t in geom.texts:
        msp.add_text(t.s, height=t.size,
                     dxfattribs={"layer": "INFO"}).set_placement((t.x, t.y))

    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue().encode("utf-8")
