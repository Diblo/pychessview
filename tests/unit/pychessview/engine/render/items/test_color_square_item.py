# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for solid-color square render items."""

from copy import copy

import pytest

from pychessview.engine.layout.primitives import Color, Rect
from pychessview.engine.render.items.color_square_item import ColorSquareItem

pytestmark = pytest.mark.unit


def test_color_square_item_stores_color_and_independent_rect_copy() -> None:
    """Carry square color and geometry as value data for render commands.

    The null renderer records copied items by value, so item copies must not
    share mutable-looking primitive instances with the original item.
    """
    color = Color(10, 20, 30, 40)
    rect = Rect(1, 2, 3, 4)
    item = ColorSquareItem(color, rect)
    copied = copy(item)

    assert item.color == color
    assert item.rect == rect
    assert copied.color == color
    assert copied.color is not color
    assert copied.rect == rect
    assert copied.rect is not rect
