# CLAUDE.md — working notes for AI agents / contributors

Guidance for safely extending this dieline generator. Read before changing geometry.

## Architecture

- **One box type = one assembler** in `boxes/<type>.py`, returning a `Geometry`
  (lists of `Seg`/`Arc`/`Text`, each tagged `CUT` / `CREASE` / `INFO`).
- `core/` is shared and must stay box-agnostic: `primitives.py` (geometry + bbox),
  `render_pdf.py` (reportlab, true arcs), `render_svg.py` (preview), `titleblock.py`.
- `web/app.py` builds geometry + title block and serves preview/PDF. Adding a box
  type should not require touching `core/` or `web/`.
- Units are **mm, y-up**. Angles **degrees, CCW, 0° = +x**. PDF/preview handle the
  y-flip; assemblers never deal with screen space.

## How real dielines are built (apply everywhere)

- **Thickness lives in the geometry**, not just outer size:
  - 180° fold-backs get a **double crease** *only when caliper ≥ ~0.6 mm* (24 pt);
    gap ≈ one board thickness. Thinner board → single crease. (`DOUBLE_T`, `DCG`.)
  - Wrapping panels are inset by `t` (score-to-score).
- **Locks are functional**: a tab is cut on 3 sides + creased on the fold and drops
  into a matching **slot**; tab/slot must align across the fold (offset by `t`).
- **Corners are softened / relieved** (radii, small clearances) so panels fold
  without tearing or colliding.
- Keep every per-board allowance a **named constant at the top of the assembler**
  (brief §11) so it can be recalibrated with a single number after a sample cut.
- **Do not add anything not in the reference** (no vent holes, print-direction
  marks, etc. unless the spec calls for it).

## The 14747 box (`boxes/pizza_led.py`)

Book-style tray + folding lid, **side-by-side blank** (base left, spine/hinge,
lid right). NOT a mailer and NOT a food box — earlier attempts at those were wrong.
Confirmed mechanics: end-wall flap **tabs → oval slots in the bottom**; lid right
edge (with grab notches) **tucks behind the base left wall**. Rounded lid corners.

## Reference & verification (do this for every geometry change)

- The trustworthy reference is the **layered** production file
  `samples/ref_14747_layers.pdf`: **CREASE = magenta (CMYK 0,1,0,0); CUT = the
  other spot colour.** (The earlier single-layer file had cut+crease merged — do
  not rely on it for classification.)
- `tools/extract_paths.py` / `tools/repro.py` — pull exact geometry from a PDF.
- `tools/compare_layers.py` — overlay the generated dieline on the reference and
  render a PNG. **Confirm cut/crease, slots, tabs and folds line up 1:1** before
  considering a change done. Render → look → adjust constants → repeat.

## Deploy

- systemd `die.service` runs uvicorn on `127.0.0.1:8011` (`ROOT_PATH=/die`).
- nginx `location /die/` proxies it on https://idealabs.co/die/.
- After editing code on the server: \`systemctl restart die\`.
- The web template uses **relative URLs** (preview.svg, download.pdf) so it works
  under the /die/ sub-path. Output is **PDF only** (no DXF/SVG download) and the
  UI/title block are **English only**.

## Pitfalls that already bit us

1. Guessing the box type — verify against the layered reference, don't assume.
2. Treating tabs as decorative — they must lock into a real slot.
3. Forgetting double crease on 180° folds (and its caliper threshold).
4. Letting `t` not affect geometry at all.
5. Approximating arcs as polylines in output (use true `Arc`).
