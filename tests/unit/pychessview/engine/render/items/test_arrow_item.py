# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for arrow render items."""

from copy import copy

import pytest

from pychessview.engine.render.items.arrow_item import ArrowItem

pytestmark = pytest.mark.unit


def test_arrow_item_stores_renderer_geometry_values() -> None:
    """Carry arrow dimensions from layout to renderer without interpretation.

    Annotation layout decides the shaft and head dimensions. The item must
    preserve those values exactly so renderers can draw the intended geometry.
    """
    item = ArrowItem(12, 24, 18)
    copied = copy(item)

    assert (item.shaft_width, item.head_length, item.head_width) == (12, 24, 18)
    assert copied is not item
    assert (copied.shaft_width, copied.head_length, copied.head_width) == (12, 24, 18)
