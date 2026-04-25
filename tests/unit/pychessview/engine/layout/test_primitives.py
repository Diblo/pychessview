# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for layout primitive value objects."""

import pytest

from pychessview.engine.layout.primitives import (
    NULL_RECT,
    Arrow,
    Color,
    Coord,
    HorizontalAlign,
    Rect,
    VerticalAlign,
    Viewport,
)

pytestmark = pytest.mark.unit


def test_alignment_string_contracts_match_theme_and_label_usage() -> None:
    """Expose stable human-readable alignment names.

    Label layout and renderer code use enum members directly, but stable string
    representations make debugging and generated command output predictable.
    """
    assert str(HorizontalAlign.LEFT) == "left"
    assert repr(HorizontalAlign.RIGHT) == "HorizontalAlign(RIGHT=2)"
    assert str(VerticalAlign.TOP) == "top"
    assert repr(VerticalAlign.BOTTOM) == "VerticalAlign(BOTTOM=2)"


def test_color_mapping_defaults_alpha_and_preserves_value_semantics() -> None:
    """Create RGBA colors from theme mappings with an opaque default alpha.

    Theme YAML may omit alpha for ordinary opaque colors. The value object must
    fill that default while still comparing by channel values.
    """
    assert Color.from_mapping({"r": 1, "g": 2, "b": 3}) == Color(1, 2, 3, 255)
    assert Color.from_mapping({"r": 1, "g": 2, "b": 3, "a": 4}) == Color(1, 2, 3, 4)
    assert repr(Color(1, 2, 3)) == "Color(r=1, g=2, b=3, a=255)"


def test_coord_rect_and_viewport_expose_derived_geometry() -> None:
    """Keep geometry primitives deterministic for layout and renderer consumers.

    Board layout computes many rectangles and centers once, then layers and
    renderers consume those derived values directly.
    """
    rect = Rect(10, 20, 30, 40)

    assert str(Coord(4, 5)) == "4,5"
    assert rect.left == 10
    assert rect.right == 40
    assert rect.bottom == 60
    assert rect.center == Coord(25, 40)
    assert rect.scale(0.5) == Rect(17, 30, 15, 20)
    assert rect.with_xy(1, 2) == Rect(1, 2, 30, 40)
    assert NULL_RECT == Rect(0, 0, 0, 0)
    assert Viewport(1, 2, 3, 4).as_rect() == Rect(1, 2, 3, 4)


def test_rect_rejects_negative_dimensions_and_scale_factors() -> None:
    """Reject impossible geometry before it enters layout caches.

    Negative dimensions would make edge and center calculations ambiguous, so
    the primitive protects downstream layout code by failing immediately.
    """
    with pytest.raises(ValueError, match="Width must be non-negative"):
        Rect(0, 0, -1, 1)
    with pytest.raises(ValueError, match="Height must be non-negative"):
        Rect(0, 0, 1, -1)
    with pytest.raises(ValueError, match="Scale factor must be non-negative"):
        Rect(0, 0, 1, 1).scale(-0.5)


def test_arrow_value_object_compares_by_geometry_fields() -> None:
    """Compare arrow geometry by dimensions rather than object identity.

    Theme and renderer tests can construct equivalent arrow values independently
    and still compare them as the same geometry contract.
    """
    assert Arrow(1.0, 2.0, 3.0) == Arrow(1.0, 2.0, 3.0)
    assert str(Arrow(1.0, 2.0, 3.0)) == "Arrow(shaft_width=1.0, head_length=2.0, head_width=3.0)"
