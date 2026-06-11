# Dieline Studio

Parametric packaging **dieline generator**. Two categories: rigid **boxes** (from
board, with thickness) and thin-material **bags** (film / paper, no thickness).
Enter dimensions — get a print-ready vector **PDF** (and a layered **DXF**) for
die-cutting, with separate **cut**, **crease** and **safe-area** layers, in
millimetres at 1:1.

**Live demo:** https://idealabs.co/die/

Commercial dieline services (Pacdora, diecuttemplates, …) are subscription based.
This is a small, self-hosted generator for the packaging types actually used in
production, built from real production files and FEFCO/ECMA principles rather than
guesswork.

## Features

- **Two categories, different engines** (see `docs/ARCHITECTURE.md`):
  - **Boxes** — parametric geometry remapped from a real layered reference DXF
    (`W × D × H × t`: width, depth, height, board thickness).
  - **Bags** — geometry built **by formula from scratch**: no thickness, no remap,
    no reference. Pure parametric.
- **Production-correct box mechanics**, not just an outline:
  - **Double crease** on 180° fold-backs, applied automatically when the board
    caliper is thick enough (≥ ~0.6 mm) — gap scales with thickness.
  - **Locking tabs ↔ slots**: end-wall flap tabs drop into the oval slots in the
    bottom; the lid edge tucks behind the base wall and locks.
  - **Score-to-score** thickness allowances; softened (rounded) corners.
- **Layers & colours** (production convention): `CUT` (red), `CREASE` (green,
  dashed), `INFO` (title block / dimensions), `SAFE` (blue dashed — print/safe-area
  boundary, never a physical fold).
- **Type registry + two-screen web**: a landing page chooses a type, then the box
  or bag constructor opens; the registry drives the build function, download
  filename and parameter schema, so new types need no endpoint changes.
- **Live SVG preview** in the browser; one-click **PDF** and layered **DXF** download.

## Types

Architecture is **one type = one builder**. The shared `core/` (primitives, layers,
PDF/SVG/DXF export, title block) is reused, so adding a type never touches export
or the web layer.

### Boxes — `boxes/<type>.py`

| Type | Description | Status |
|------|-------------|--------|
| `pizza_led` (14747) | LED display box — book-style tray + folding lid, side-by-side blank, oval tab locks, rounded lid corners | reverse-engineered 1:1 from a layered production file |

### Bags — `bags/<type>.py`

| Type | Description | Status |
|------|-------------|--------|
| `wicket` | Wicket bag (film / paper) — sections lip → length → gusset → gusset → length, built from a formula; SAFE print-area frame; optional dimensions, panel labels and legend | parametric, no reference file |

## Stack

Python · **FastAPI** (web) · **PyMuPDF** (production PDF with OCG layers) · **ezdxf**
(DXF with real layers) · **reportlab** / **CairoSVG** (legacy & preview helpers) ·
**pdfminer.six** (reverse-engineering reference dielines).

## Repository layout

```
core/      primitives (Seg/Arc/Text + bbox + layers CUT/CREASE/INFO/SAFE),
           render_pdf_fitz (PDF/OCG), render_dxf (real layers), render_svg, titleblock
boxes/     one assembler per box type (pizza_led.py = 14747; reference-driven remap)
bags/      formula-built bags (bag_wicket.py) + registry.py (type registry, coerce)
web/       FastAPI app + templates (landing.html chooser, index.html box, wicket.html bag)
tools/     reverse-engineering & verification (extract_paths, repro, compare_layers, overlay)
tests/     geometry / output checks
samples/   reference dielines & generated previews  (gitignored — not in the public repo)
```

## Run locally

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn web.app:app --reload --port 8011
# open http://127.0.0.1:8011/
```

Generate geometry / inspect from the CLI:

```bash
python -m boxes.pizza_led          # box: prints bbox / segment counts for a few sizes
python -m bags.bag_wicket          # wicket: prints bbox (240×420+60+40 -> 240 × 1000 mm)
```

## Output conventions

- Units **millimetres**, scale **1:1**.
- `CUT` = red, `CREASE` = green dashed, `INFO` = title block / dimensions,
  `SAFE` = blue dashed (print-area boundary, not a cut or fold).
- Tolerance in the shop is ~±5 mm; correct mechanics and readability matter more
  than absolute precision (FEFCO/ECMA practice).

## Deploy (production)

Served behind nginx as a systemd service (see `idealabs.co/die`):

```
systemd:  die.service -> uvicorn web.app:app --host 127.0.0.1 --port 8011  (Environment=ROOT_PATH=/die)
nginx:    location /die/ { proxy_pass http://127.0.0.1:8011/; }
```

After changing code: `systemctl restart die`.

## Verifying changes

Every **box** geometry change is checked by overlaying the generated dieline on the
real reference (`tools/compare_layers.py` → PNG) and confirming cut/crease, slots,
tabs and folds line up 1:1. **Bags** have no reference: verify by rendering the PDF
(and checking `python -m bags.bag_wicket` reports the expected blank size). See
`CLAUDE.md` and `docs/ARCHITECTURE.md` for the workflow and pitfalls.
