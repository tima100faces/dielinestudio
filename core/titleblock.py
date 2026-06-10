"""English INFO title block, drawn below the dieline (layer INFO)."""
from core.primitives import Geometry, INFO


def title_block(meta, x, y, w=190.0, h=30.0):
    """meta: dict(sku,color,tol,W,D,H,date). Anchored at lower-left (x,y)."""
    g = Geometry()
    g.rect(x, y, w, h, layer=INFO)
    g.line(x + w * 0.5, y, x + w * 0.5, y + h, layer=INFO)
    def L(tx, ty, s, sz=4.4): g.text(tx, ty, s, sz)
    col2 = x + w * 0.5 + 5
    L(x + 5, y + h - 9,  f"SKU: {meta.get('sku') or '-'}")
    L(x + 5, y + h - 18, f"INNER: {meta['W']}x{meta['D']}x{meta['H']} mm")
    L(x + 5, y + h - 27, f"COLOR: {meta.get('color') or '-'}")
    L(col2, y + h - 9,   f"TOL: +/- {meta.get('tol', 3)} mm")
    L(col2, y + h - 18,  f"DATE: {meta.get('date', '-')}")
    L(col2, y + h - 27,  "CUT = red   CREASE = green")
    return g
