# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Image square item render item definitions for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from .base import Item

if TYPE_CHECKING:
    from ...layout.primitives import Rect
    from ..image_assets import ImageAsset


class ImageSquareItem(Item):
    """Renderable item describing an image-backed square.

    Attributes:
        image_asset: Image asset rendered by the item.
        rect: Rectangle occupied by the render item.
    """

    __slots__ = "image_asset", "rect"

    image_asset: ImageAsset
    rect: Rect

    def __init__(self, image_asset: ImageAsset, rect: Rect) -> None:
        """Initialize the image square item with its initial configuration.

        Args:
            image_asset: Image asset used for piece or square rendering.
            rect: Rectangle used to define geometry or clipping bounds.
        """
        self.image_asset = image_asset
        self.rect = rect

    def __copy__(self) -> ImageSquareItem:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(copy(self.image_asset), copy(self.rect))
