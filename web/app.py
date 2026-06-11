"""FastAPI web panel for the dieline generator (English UI).

Two-screen flow: `/` is a type chooser, `/box` and `/bag` are the constructors.
Each constructor drives a live SVG preview and layered PDF / DXF downloads.
Endpoints are generic: the type id selects the build function and parameters
from bags.registry, so adding a type needs no endpoint changes. Served under
/die/ via nginx.
"""
import os, datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.render_svg import render_svg
from core.render_pdf_fitz import render_pdf          # PDF with OCG layers CUT/CREASE/INFO/SAFE
from core.render_dxf import render_dxf               # DXF with real layers (for Illustrator/CAM)
from core.titleblock import title_block
from core.primitives import Geometry
from bags.registry import REGISTRY, coerce

app = FastAPI(title="Dieline Studio", root_path=os.environ.get("ROOT_PATH", ""))

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates")


def _page(name):
    with open(os.path.join(TPL, name), encoding="utf-8") as f:
        return f.read()


def _resolve_type(query) -> str:
    """Accept `type` (new) or `box` (legacy) and fall back to pizza_led."""
    t = query.get("type") or query.get("box") or "pizza_led"
    return t if t in REGISTRY else "pizza_led"


def _slug(type_id, params) -> str:
    if type_id == "pizza_led":
        return f"pizza_led_{int(params['W'])}x{int(params['D'])}x{int(params['H'])}"
    if type_id == "wicket":
        return f"wicket_{int(params['width'])}x{int(params['body'])}"
    return type_id


def build(type_id, params, query=None) -> Geometry:
    g = REGISTRY[type_id]["build"](params)
    # Legend / title block stays an opt-in box feature (off by default).
    if query is not None and str(query.get("legend", "")).lower() in ("1", "true", "on", "yes"):
        b = g.bbox()
        if type_id == "pizza_led":
            meta = {"W": int(params["W"]), "D": int(params["D"]), "H": int(params["H"]),
                    "sku": query.get("sku", ""), "color": query.get("color", ""),
                    "tol": float(query.get("tol", 5.0) or 5.0),
                    "date": datetime.date.today().strftime("%d.%m.%y")}
            g.extend(title_block(meta, b[0], b[1] - 42))
    return g


def _build_from_request(request: Request):
    q = request.query_params
    type_id = _resolve_type(q)
    params = coerce(type_id, q)
    return type_id, params, build(type_id, params, q)


@app.get("/preview.svg")
def preview(request: Request):
    _, _, g = _build_from_request(request)
    return Response(render_svg(g, mode="preview"), media_type="image/svg+xml")


@app.get("/download.pdf")
def download_pdf(request: Request):
    type_id, params, g = _build_from_request(request)
    slug = _slug(type_id, params)
    pdf = render_pdf(g, title=slug)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{slug}.pdf"'})


@app.get("/download.dxf")
def download_dxf(request: Request):
    type_id, params, g = _build_from_request(request)
    slug = _slug(type_id, params)
    dxf = render_dxf(g, title=slug)
    return Response(dxf, media_type="application/dxf",
                    headers={"Content-Disposition": f'attachment; filename="{slug}.dxf"'})


@app.get("/", response_class=HTMLResponse)
def index():
    return _page("landing.html")


@app.get("/box", response_class=HTMLResponse)
def box_constructor():
    return _page("index.html")


@app.get("/bag", response_class=HTMLResponse)
def bag_constructor():
    return _page("wicket.html")
