# CLAUDE.md

Parametric dieline generator. **Two categories:**
- **Boxes** (`boxes/`) — regenerated from a reference DXF by a parametric remap
  (thickness model, double-crease, rigid feature windows). One type: **14747**
  (book-style tray + folding lid).
- **Bags** (`bags/`) — thin-material bags (film / paper) built **by formula from
  scratch**: no thickness, no remap, no reference DXF, no double-crease. One type:
  **wicket**.

Live: https://idealabs.co/die/  ·  Output: **PDF** (OCG layers) + **DXF** (real
layers). Stack: Python · FastAPI · PyMuPDF (PDF) · ezdxf (DXF).

Layers: **CUT / CREASE / INFO / SAFE** (SAFE = blue dashed print-area boundary,
never a physical fold).

## Categories live by DIFFERENT rules — don't mix them
- **Boxes** are subtle and reference-driven. **Before touching box geometry,
  cut/crease classification, or the thickness model, read
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — it has the full architecture,
  the rules, and the failed approaches already ruled out (so you don't repeat them).
  Always verify by overlaying on the reference and rendering regions
  (`tools/verify_template.py`, `tools/region*.py`, `tools/hires.py`).
- **Bags** are pure parametric (`bags/bag_wicket.py`). **Do NOT apply the pizza_led
  machinery (remap / windows / double-crease / slot_shift) to bags** — different
  world: geometry is built from a formula, there is no thickness and no reference.

## Types & web
`bags/registry.py` maps `id -> {label, category, build, filename, params}`; the web
layer reads the build function, download filename and parameter schema from there,
so adding a type doesn't touch the endpoints. Two-screen flow: `/` = type chooser,
`/box` = box constructor, `/bag` = wicket constructor.

## Non-negotiables
- **Boxes:** CREASE = colour **230**; the outer perimeter is **always CUT**, never
  crease. Double-crease gap = **2 × board thickness** (180° folds only). The
  reference `samples/14747_d-layers.dxf` is **gitignored** (client file) but the
  generator loads it at runtime — it must be present on the machine/server.
- **All:** UI and title block are **English only**; the box legend/title block is
  OFF by default (clean dieline for production).

## Deploy
systemd `die.service` (uvicorn :8011, `ROOT_PATH=/die`) + nginx `location /die/`.
After editing code on the server: `systemctl restart die`.
