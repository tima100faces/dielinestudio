"""Type registry: maps a type id to its label, category, build function and the
parameter schema the web UI drives. The web layer picks the build function and
parameters from here instead of a hard-coded dictionary.

Each build function takes a params dict (already coerced to the right types) and
returns a core.primitives.Geometry. Unknown extra keys are ignored, so callers
can pass a superset safely.
"""
from boxes.pizza_led import pizza_led
from bags.bag_wicket import wicket


def _build_pizza(p):
    return pizza_led(W=p["W"], D=p["D"], H=p["H"], t=p["t"])


def _build_wicket(p):
    return wicket(width=p["width"], body=p["body"], gusset=p["gusset"],
                  tab=p["tab"], inset_side=p["inset_side"],
                  inset_height=p["inset_height"], dims=p["dims"])


def _name_pizza(p):
    return f"pizza_led_{int(p['W'])}x{int(p['D'])}x{int(p['H'])}"


def _name_wicket(p):
    # width x body + gusset + tab, numbers as entered (gusset single, not doubled)
    return f"wicket_{p['width']:g}x{p['body']:g}+{p['gusset']:g}+{p['tab']:g}"


# param: name, label, min, max, step, default. type defaults to float;
# "bool" params (default True/False) become checkboxes.
REGISTRY = {
    "pizza_led": {
        "label": "Box (pizza / LED)",
        "category": "box",
        "build": _build_pizza,
        "filename": _name_pizza,
        "params": [
            {"name": "W", "label": "Width · W", "min": 120, "max": 650, "step": 1, "default": 430},
            {"name": "D", "label": "Depth · D", "min": 120, "max": 650, "step": 1, "default": 260},
            {"name": "H", "label": "Wall height · H", "min": 15, "max": 120, "step": 1, "default": 30},
            {"name": "t", "label": "Board thickness · t", "min": 0.3, "max": 7, "step": 0.1, "default": 1.5},
        ],
    },
    "wicket": {
        "label": "Wicket bag",
        "category": "bag",
        "build": _build_wicket,
        "filename": _name_wicket,
        "params": [
            {"name": "width", "label": "Width", "min": 80, "max": 600, "step": 1, "default": 240},
            {"name": "body", "label": "Body", "min": 100, "max": 900, "step": 1, "default": 420},
            {"name": "gusset", "label": "Gusset", "min": 20, "max": 200, "step": 1, "default": 60},
            {"name": "tab", "label": "Tab", "min": 10, "max": 150, "step": 1, "default": 40},
            {"name": "inset_side", "label": "Inset · sides", "min": 0, "max": 60, "step": 1, "default": 10},
            {"name": "inset_height", "label": "Inset · top/bottom", "min": 0, "max": 80, "step": 1, "default": 20},
            {"name": "dims", "label": "Show dimensions", "type": "bool", "default": False},
        ],
    },
}


def coerce(type_id, query):
    """Build a params dict for `type_id` from a (string-valued) query mapping,
    filling defaults and coercing each value to float or bool per the schema."""
    spec = REGISTRY[type_id]
    out = {}
    for p in spec["params"]:
        raw = query.get(p["name"])
        if p.get("type") == "bool":
            out[p["name"]] = (str(raw).lower() in ("1", "true", "on", "yes")
                              if raw is not None else bool(p["default"]))
        else:
            try:
                out[p["name"]] = float(raw) if raw is not None else float(p["default"])
            except (TypeError, ValueError):
                out[p["name"]] = float(p["default"])
    return out
