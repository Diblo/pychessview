# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for image-backed square render items."""

from copy import copy

import pytest

from pychessview.engine.layout.primitives import Rect
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.render.items.image_square_item import ImageSquareItem

pytestmark = pytest.mark.unit


def test_image_square_item_stores_asset_and_independent_rect_copy() -> None:
    """Carry image asset and target rectangle from layout to renderer.

    Renderers need the asset metadata and the rectangle as separate value data;
    copying preserves both while avoiding shared primitive instances.
    """
    asset = ImageAsset("pieces/queen.svg", 45, 55)
    rect = Rect(1, 2, 3, 4)
    item = ImageSquareItem(asset, rect)
    copied = copy(item)

    assert item.image_asset == asset
    assert item.rect == rect
    assert copied.image_asset == asset
    assert copied.image_asset is not asset
    assert copied.rect == rect
    assert copied.rect is not rect
