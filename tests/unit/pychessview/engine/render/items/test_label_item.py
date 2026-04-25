# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for label render items."""

from copy import copy
from pathlib import Path

import pytest

from pychessview.engine.layout.primitives import Color, HorizontalAlign, Rect, VerticalAlign
from pychessview.engine.render.items.label_item import LabelItem

pytestmark = pytest.mark.unit


def test_label_item_stores_text_style_and_alignment_values() -> None:
    """Carry label text styling from board layout to text renderers.

    Labels combine geometry, text, color, font, size, and alignment. The item
    should preserve every value so renderers can stay backend-specific only.
    """
    font = Path("fonts/labels.ttf")
    rect = Rect(1, 2, 3, 4)
    color = Color(9, 8, 7)
    item = LabelItem(
        rect,
        "A",
        color,
        18,
        font=font,
        v_align=VerticalAlign.BOTTOM,
        h_align=HorizontalAlign.RIGHT,
    )
    copied = copy(item)

    assert item.rect == rect
    assert item.text == "A"
    assert item.color == color
    assert item.size == 18
    assert item.font == font
    assert item.v_align is VerticalAlign.BOTTOM
    assert item.h_align is HorizontalAlign.RIGHT
    assert copied is not item
    assert copied.rect == rect
    assert copied.rect is not rect
    assert copied.color == color
    assert copied.color is not color
    assert copied.font == font
