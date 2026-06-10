"""Smoke / sanity tests for the 14747 assembler and exporters."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boxes.pizza_led import pizza_led
from core.primitives import CUT, CREASE
from core.render_pdf import render_pdf
from core.render_svg import render_svg


def _counts(g):
    cre = sum(1 for s in g.segs if s.layer == CREASE)
    return cre, len(g.segs) - cre


def test_builds_with_cut_and_crease():
    g = pizza_led(430, 260, 30, 1.5)
    cre, cut = _counts(g)
    assert cre > 0 and cut > 0
    assert len(g.arcs) > 0                      # rounded corners / slots are real arcs


def test_blank_size_matches_reference():
    g = pizza_led(430, 260, 30, 1.5)
    minx, miny, maxx, maxy = g.bbox()
    w, h = maxx - minx, maxy - miny
    assert abs(w - 640) < 12                    # ref layered blank ~640 mm wide
    assert abs(h - 640) < 20


def test_double_crease_threshold():
    thick = _counts(pizza_led(430, 260, 30, 1.5))[0]   # caliper >= 0.6 -> double
    thin = _counts(pizza_led(430, 260, 30, 0.4))[0]    # caliper < 0.6  -> single
    assert thick > thin


def test_exports_produce_output():
    g = pizza_led(430, 260, 30, 1.5)
    assert render_pdf(g)[:4] == b"%PDF"
    assert "<svg" in render_svg(g)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok", name)
