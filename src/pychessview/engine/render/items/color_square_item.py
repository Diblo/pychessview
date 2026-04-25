# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Color square item render item definitions for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from .base import Item

if TYPE_CHECKING:
    from ...layout.primitives import Color, Rect


class ColorSquareItem(Item):
    """Renderable item describing a solid-color square.

    Attributes:
        color: Color value associated with the object.
        rect: Rectangle occupied by the render item.
    """

    __slots__ = "color", "rect"

    color: Color
    rect: Rect

    def __init__(self, color: Color, rect: Rect) -> None:
        """Initialize the color square item with its initial configuration.

        Args:
            color: Color value associated with the object or operation.
            rect: Rectangle used to define geometry or clipping bounds.
        """
        self.color = color
        self.rect = rect

    def __copy__(self) -> ColorSquareItem:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(copy(self.color), copy(self.rect))
