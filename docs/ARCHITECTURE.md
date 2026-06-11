# Dieline Studio — architecture & hard-won lessons

Guidance for safely extending this dieline generator. Read **all** of it before
touching geometry — most of these lessons cost real iterations.

## What this is
Parametric dieline generator with **two categories**:
- **Boxes** (`boxes/`) — rigid board, regenerated 1:1 from a layered production DXF
  by a parametric remap. Current type **14747**: a book-style tray + folding lid
  (side-by-side blank).
- **Bags** (`bags/`) — thin-material bags (film / paper) built **by formula from
  scratch**. Current type **wicket**.

Output: vector **PDF** (PyMuPDF, OCG layers) + **DXF** (ezdxf, real layers), layers
CUT (red) / CREASE (green) / INFO / SAFE (blue dashed). Served at
https://idealabs.co/die/.

## Two categories — and why their rules differ
This is the single most important thing to internalise before editing geometry:

- **Box (`boxes/pizza_led.py`)** — complex **DXF-template remap**, rigid feature
  **windows**, a **thickness model**, **double-crease**, and it **loads a reference
  DXF** at runtime. **Everything in sections 1–6 below applies to the box category
  only.**
- **Bag (`bags/`, e.g. `bag_wicket.py`)** — geometry is built by a **formula from
  scratch**. **No thickness, no remap, no reference DXF, no double-crease.** Pure
  parametric construction (see section 8).

> ⚠️ **Do NOT apply the pizza_led machinery (remap / windows / double-crease /
> slot_shift) to bags.** They are different worlds. A bag is a stack of plain
> rectangles computed from its parameters; reaching for the box engine there is
> always wrong.

---

# BOX category (pizza_led) — sections 1–6

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

## 6. Verify EVERY box change
- Overlay output on the reference DXF at the design size (`tools/verify_template.py`,
  `tools/compare_layers.py`). At `430×260×30, t1.5` it must match 1:1.
- Render and LOOK at what you touched (`tools/region*.py`, `tools/hires.py`).
- Resize hard (e.g. `820×580`) and change thickness (`t=4`) — that is where
  stretching, connectivity and classification bugs surface.

---

# BAG category — section 7

## 7. Bag category: wicket (formula-built)
A wicket bag is **built from a formula**, not a reference. There is no thickness,
no remap, no windows, no double-crease — just rectangles computed from parameters.

- **Sections, bottom → top:** `lip → length → gusset → gusset → length`.
  - **Blank height = `lip + 2·length + 2·gusset`**; width = `width`.
  - Reference: `240 × 420 + 60 + 40` → **240 × 1000 mm**.
- Each section is a **closed rectangle on the CUT layer** (drawn as rectangles, not
  loose lines — it keeps the blank easy for a designer to align to).
- **SAFE frame**: one rectangle on the SAFE layer over the **length+gusset block
  (NOT the lip)**, inset by `safe_side` (sides) and `safe_height` (top/bottom).
- **Reference / annotation layer (`dims=True`, "Show dimensions")** — everything
  below is drawn on **CUT (technical red)** and is hidden when `dims=False` (clean
  drawing):
  - **Dimensions**: numbers only (no names). Vertical dims are rotated so they read
    bottom-to-top; a per-section column plus the overall blank height sit at the
    left, the width dimension across the top.
  - **Panel labels**: **FRONT** (upper length panel, upright), **BACK** (lower
    length panel, `rotation=180` so it reads right once the bag is folded), and
    **BOTTOM GUSSET** as two centred lines on the gusset block.
  - **Legend** below the blank: `"blue dashed = printable area, do not exceed"`.
- **Terminology** (UI label / code parameter): Width / `width`, Length / `length`,
  Gusset / `gusset`, Lip / `lip`, Safe area · sides / `safe_side`, Safe area ·
  top/bottom / `safe_height`, Show dimensions / `dims`. (Earlier names were
  tab→lip, body→length, inset→safe area.)
- Verify a bag by **rendering the PDF and looking** (and `python -m bags.bag_wicket`
  reports the blank size). No 1:1 overlay — there is no reference.

---

# Shared core & web — section 8

## 8. Core mechanisms shared by both categories
- **Four layers: CUT / CREASE / INFO / SAFE.** SAFE was added alongside the
  original three: a **blue dashed print/safe-area boundary** (never a physical cut
  or fold). Handled in every renderer (`render_svg`, `render_pdf_fitz`,
  `render_pdf`, `render_dxf`); in DXF it is a **real layer `SAFE`, ACI 5, dashed**.
- **`Text.rotation`** (degrees, CCW, y-up) — an **additive** field (default `0`, so
  all pre-existing text is unchanged). Used for vertical dimension labels and the
  upside-down BACK label. Sign in the y-flipping renderers differs by convention:
  **fitz uses `+rotation`, SVG uses `-rotation`** (PyMuPDF `prerotate` vs SVG
  `rotate`); reportlab and DXF are y-up native so the angle is direct.
- **Type registry `bags/registry.py`**: `id -> {label, category, build, filename,
  params}`. The web layer takes the **build function**, **download filename** and
  **parameter schema** from the registry, so adding a type does not touch the
  endpoints. `coerce()` turns query strings into typed params.
- **Two-screen web flow**: `/` = type chooser (`landing.html`), `/box` = box
  constructor (`index.html`), `/bag` = wicket constructor (`wicket.html`). `app.py`
  is generic over the `type` parameter (legacy `box=` is still accepted).
- **Download filenames** come from a per-type `filename` function in the registry:
  box → `pizza_led_430x260x30`; wicket → `wicket_240x420+60+40` (format
  `width x length + gusset + lip`, numbers as entered, gusset single).
- **Text size note:** `Text.size` is in **mm**; PDF renderers scale it to points
  (`* MM` / `* mm`). DXF height is in mm directly.

## 9. Known issues & roadmap
- **Wicket legend is drawn red (CUT)** even though it refers to the blue dashed
  line — cosmetic, worth revisiting.
- **Label / dimension centring is approximate** — it uses a rough glyph-width
  factor (`_CH`), not real font metrics.
- **Roadmap:** the next bag types (t-shirt bag, die-cut handle bag) go through the
  **same registry / pattern** — add a `bags/<type>.py` builder + a registry entry;
  no new endpoints.

---

# Deploy — section 10

## 10. Deploy
- systemd `die.service` → `uvicorn web.app:app --host 127.0.0.1 --port 8011`
  (`ROOT_PATH=/die`); nginx `location /die/`. After editing code: `systemctl restart die`.
- Output is **PDF** (PyMuPDF, `render_pdf_fitz`) with real OCG
  **layers CUT / CREASE / INFO / SAFE**; UI and title block are **English only**.
- The box title block / legend is a toggle in the sidebar, **OFF by default** (a
  clean dieline for production); `legend=true` adds it.
- **DXF download** (`render_dxf`, ezdxf) gives REAL layers CUT/CREASE/INFO/SAFE
  (ACI 1/3/8/5) + audit-clean. Use DXF for Illustrator/CAM layers — Illustrator does
  NOT promote PDF OCG to Layers-panel layers (only groups by them).
