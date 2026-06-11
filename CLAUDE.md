# CLAUDE.md — working notes & hard-won lessons

Guidance for safely extending this dieline generator. Read **all** of it before
touching geometry — most of these lessons cost real iterations.

## What this is
Parametric dieline generator. Current production type **14747**: a book-style
tray + folding lid (side-by-side blank), reverse-engineered 1:1 from a layered
production DXF and regenerated at any `W × D × H × t`. Output: vector PDF, layers
CUT (red) / CREASE (green) / INFO. Served at https://idealabs.co/die/.

## 1. Get the box TYPE right
14747 is a **side-by-side book box**: base (left) + spine/hinge + lid (right).
It is **NOT** a mailer (FEFCO 0427) and **NOT** a food box (ECMA / becf-12007) —
both were wrong guesses that wasted a lot of time. Confirmed mechanics: the
end-wall flap tabs drop into the **oval slots in the bottom**; the lid's right
flap **tucks behind the base's left wall**.

## 2. Golden rule: build FROM the reference, don't hand-code details
Every attempt to hand-draw geometry "from the box definition" produced wrong
details (corners, tapers, locks, lid shape). What works: load the EXACT geometry
from the layered reference DXF and regenerate it parametrically.

- Reference: `samples/14747_d-layers.dxf` — **gitignored** (client production
  file, server only). The generator loads it at runtime, so it must be present.
- **Classify CREASE vs CUT by COLOUR, not layer.** CREASE = colour **230**
  (magenta); CUT = everything else. The file has cut-coloured (114) lines sitting
  on the crease layer (Layer 3) — classifying by layer mislabels them.

## 3. Parametric engine: ONE continuous remap + rigid feature windows
The core insight after several failures:
- **A single continuous remap applied to ALL points preserves connectivity** —
  shared endpoints map to the same point, so the contour never tears. Translating
  features by a *separate* rule BREAKS the outer contour at large sizes. Don't.
- Keep features rigid with **windows**: ranges the remap maps with slope 1; only
  the empty gaps between features stretch. (`_build_windows`, `_make_controls`,
  `_piecewise`.)
- A lock slot arrives **split** into arc caps (polylines) + straight sides
  (2-pt lines). Windowing only the caps lets the middle stretch. Fix: stitch cut
  segments into closed loops and window the **whole** slot (`_slot_boxes`).

### Failed approaches — do NOT repeat
- Pure remap, no windows → stretches embedded features (slots, grab notches).
- Rigid feature *translation* + stretch the rest → tears the outer contour.
- Hand-coded edge walk / guessing the outline → wrong details every time.
- boxes.py (florianfesti) is the right architectural reference (edge system,
  thickness-aware) but it's laser-cut finger-joint, not folding carton — borrow
  ideas, don't fork.

## 4. Cut / crease rules (the outer contour is sacred)
- **The outer perimeter is ALWAYS cut** and never interrupted by a crease.
- Where the source draws BOTH a cut and a crease on the same line (tab bases),
  **the CREASE wins** — a marked crease is an intentional fold. `_drop_cut_under_crease`
  removes the redundant cut. (We first did the opposite and turned a fold red —
  wrong. The earlier `_drop_perimeter_creases` is gone.)
- Perimeter lines carry no coincident crease, so they stay cut. The spine
  top/bottom and the left-wall tabs are colour-114 cut lines on Layer 3 — cut,
  correctly.

## 5. Thickness model
- **Double-crease gap = 2 × board thickness** (`DCG = 2*t`), only on the 180°
  fold-back, and only when `t >= 0.6 mm` (below → single crease).
- The box **grows** with thickness (`grow = max(0, DCG - 3)`; the end assembly
  extends) and the **lock slot is linked to the flap/tab** (`slot_shift`) so they
  stay aligned. Never just "shift the bigs" without growing the box — the tab
  stops reaching the slot.
- Panels carry score-to-score: base width `D + 2t`, lid width `D + 4t`.

## 6. Verify EVERY change
- Overlay output on the reference DXF at the design size (`tools/verify_template.py`,
  `tools/compare_layers.py`). At `430×260×30, t1.5` it must match 1:1.
- Render and LOOK at what you touched (`tools/region*.py`, `tools/hires.py`).
- Resize hard (e.g. `820×580`) and change thickness (`t=4`) — that is where
  stretching, connectivity and classification bugs surface.

## 7. Deploy
- systemd `die.service` → `uvicorn web.app:app --host 127.0.0.1 --port 8011`
  (`ROOT_PATH=/die`); nginx `location /die/`. After editing code: `systemctl restart die`.
- Output is **PDF only** (PyMuPDF, ) with real OCG
  **layers CUT / CREASE / INFO**; UI and title block are **English only**.
- The title block / legend is a toggle in the sidebar, **OFF by default** (a clean
  dieline for production);  adds it.
- **DXF download** (, ezdxf) gives REAL layers CUT/CREASE/INFO
  (ACI 1/3/8) + audit-clean. Use DXF for Illustrator/CAM layers — Illustrator does
  NOT promote PDF OCG to Layers-panel layers (only groups by them).
