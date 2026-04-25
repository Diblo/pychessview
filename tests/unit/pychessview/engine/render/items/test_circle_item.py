# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for circle render items."""

from copy import copy

import pytest

from pychessview.engine.layout.primitives import Rect
from pychessview.engine.render.items.circle_item import CircleItem

pytestmark = pytest.mark.unit


def test_circle_item_stores_stroke_and_independent_rect_copy() -> None:
    """Carry circle stroke and geometry from annotation layout to renderer.

    Copying the item should also copy the rectangle value so later layout
    mutations cannot accidentally share object state with recorded render data.
    """
    rect = Rect(1, 2, 3, 4)
    item = CircleItem(5, rect)
    copied = copy(item)

    assert item.stroke_width == 5
    assert item.rect == rect
    assert copied is not item
    assert copied.rect == rect
    assert copied.rect is not rect
