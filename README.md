# Dieline Studio

Parametric packaging **dieline generator**. Enter box dimensions and board
thickness — get a print-ready vector **PDF** for die-cutting, with separate
**cut** and **crease** layers, in millimetres at 1:1.

**Live demo:** https://idealabs.co/die/

Commercial dieline services (Pacdora, diecuttemplates, …) are subscription based.
This is a small, self-hosted generator for the box types actually used in
production, built from real production files and FEFCO/ECMA principles rather than
guesswork.

## Features

- **Parametric** box geometry from `W × D × H × t` (width, depth, height, board thickness).
- **Production-correct mechanics**, not just an outline:
  - **Double crease** on 180° fold-backs, applied automatically when the board
    caliper is thick enough (≥ ~0.6 mm) — gap scales with thickness.
  - **Locking tabs ↔ slots**: end-wall flap tabs drop into the oval slots in the
    bottom; the lid edge tucks behind the base wall and locks.
  - **Score-to-score** thickness allowances; softened (rounded) corners.
- **Layers & colours** (production convention): `CUT` (red), `CREASE` (green,
  dashed), `INFO` (title block: SKU, inner size, colour, tolerance, date).
- **True circular arcs** in the PDF (reportlab bézier), not polyline approximation.
- **Live SVG preview** in the browser; one-click PDF download.

## Box types

| Type | Description | Status |
|------|-------------|--------|
| `pizza_led` (14747) | LED display box — book-style tray + folding lid, side-by-side blank, oval tab locks, rounded lid corners | reverse-engineered 1:1 from a layered production file |

Architecture is **one type = one assembler** (`boxes/<type>.py`). The shared
`core/` (primitives, layers, PDF/SVG export, title block) is reused, so adding a
type never touches export or the web layer.

## Stack

Python · **FastAPI** (web) · **reportlab** (vector PDF) · **CairoSVG** (preview
rendering) · **pdfminer.six** (reverse-engineering reference dielines).

## Repository layout

\`\`\`
core/      primitives (Line/Arc/Text + bbox), layers, render_pdf, render_svg, titleblock
boxes/     one assembler per box type (pizza_led.py = 14747)
web/       FastAPI app + HTML template (form -> live preview -> PDF)
tools/     reverse-engineering & verification (extract_paths, repro, compare_layers, overlay)
tests/     geometry / output checks
samples/   reference dielines & generated previews  (gitignored — not in the public repo)
\`\`\`

## Run locally

\`\`\`bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn web.app:app --reload --port 8011
# open http://127.0.0.1:8011/
\`\`\`

Generate a box from the CLI / inspect geometry:

\`\`\`bash
python -m boxes.pizza_led          # prints bbox / segment counts for a few sizes
\`\`\`

## Output conventions

- Units **millimetres**, scale **1:1**.
- `CUT` = ACI/red, `CREASE` = green dashed, `INFO` = title block.
- Tolerance in the shop is ~±5 mm; correct mechanics and readability matter more
  than absolute precision (FEFCO/ECMA practice).

## Deploy (production)

Served behind nginx as a systemd service (see `idealabs.co/die`):

\`\`\`
systemd:  die.service -> uvicorn web.app:app --host 127.0.0.1 --port 8011  (Environment=ROOT_PATH=/die)
nginx:    location /die/ { proxy_pass http://127.0.0.1:8011/; }
\`\`\`

After changing code: \`systemctl restart die\`.

## Verifying changes

Every geometry change is checked by overlaying the generated dieline on the real
reference (`tools/compare_layers.py` → PNG) and confirming cut/crease, slots, tabs
and folds line up 1:1. See `CLAUDE.md` for the workflow and pitfalls.
