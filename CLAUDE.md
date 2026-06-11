# CLAUDE.md

Parametric dieline generator. One box type: **14747** (book-style tray + folding
lid). Live: https://idealabs.co/die/  ·  Output: **PDF** (OCG layers) + **DXF**
(real CUT/CREASE/INFO layers). Stack: Python · FastAPI · PyMuPDF (PDF) · ezdxf (DXF).

## Read before changing geometry
The box is **regenerated from a reference DXF** via a parametric remap with rigid
feature windows. The details are subtle and several intuitive approaches fail.
**Before touching geometry, cut/crease classification, or the thickness model, read
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** — it has the full architecture, the
rules, and the failed approaches we already ruled out (so you don't repeat them).
Always verify a change by overlaying on the reference and rendering regions
(`tools/verify_template.py`, `tools/region*.py`, `tools/hires.py`).

## Non-negotiables (the rest is in docs/ARCHITECTURE.md)
- CREASE = colour **230**; the outer perimeter is **always CUT**, never crease.
- Double-crease gap = **2 × board thickness** (180-deg folds only).
- UI and title block are **English only**; the legend is OFF by default.
- The reference `samples/14747_d-layers.dxf` is **gitignored** (client file) but the
  generator loads it at runtime — it must be present on the machine/server.

## Deploy
systemd `die.service` (uvicorn :8011, `ROOT_PATH=/die`) + nginx `location /die/`.
After editing code on the server: `systemctl restart die`.
