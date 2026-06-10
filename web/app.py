"""FastAPI web panel for the dieline generator (English UI).
Form -> live SVG preview -> PDF download. Served under /die/ via nginx proxy.
"""
import os, datetime
from fastapi import FastAPI, Response, Query
from fastapi.responses import HTMLResponse
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boxes.pizza_led import pizza_led
from core.render_svg import render_svg
from core.render_pdf import render_pdf
from core.titleblock import title_block
from core.primitives import Geometry

app = FastAPI(title="Dieline Studio", root_path=os.environ.get("ROOT_PATH", ""))

BOXES = {"pizza_led": pizza_led}


def build(W, D, H, t, sku="", color="", tol=5.0, box="pizza_led") -> Geometry:
    g = BOXES.get(box, pizza_led)(W=W, D=D, H=H, t=t)
    b = g.bbox()
    meta = {"W": int(W), "D": int(D), "H": int(H), "sku": sku, "color": color,
            "tol": tol, "date": datetime.date.today().strftime("%d.%m.%y")}
    g.extend(title_block(meta, b[0], b[1] - 42))
    return g


@app.get("/preview.svg")
def preview(W: float = 430, D: float = 260, H: float = 30, t: float = 1.5,
            sku: str = "", color: str = "", tol: float = 5.0, box: str = "pizza_led"):
    g = build(W, D, H, t, sku, color, tol, box)
    return Response(render_svg(g, mode="preview"), media_type="image/svg+xml")


@app.get("/download.pdf")
def download(W: float = 430, D: float = 260, H: float = 30, t: float = 1.5,
             sku: str = "", color: str = "", tol: float = 5.0, box: str = "pizza_led"):
    g = build(W, D, H, t, sku, color, tol, box)
    pdf = render_pdf(g, title=f"{box}_{int(W)}x{int(D)}x{int(H)}")
    fn = f"{box}_{int(W)}x{int(D)}x{int(H)}.pdf"
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{fn}"'})


@app.get("/", response_class=HTMLResponse)
def index():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "templates", "index.html"), encoding="utf-8") as f:
        return f.read()
