# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Circle item render item definitions for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from .base import Item

if TYPE_CHECKING:
    from ...layout.primitives import Rect


class CircleItem(Item):
    """Renderable item describing a circle annotation.

    Attributes:
        stroke_width: Stroke width in pixels.
        rect: Rectangle occupied by the render item.
    """

    __slots__ = "stroke_width", "rect"

    stroke_width: int
    rect: Rect

    def __init__(self, stroke_width: int, rect: Rect) -> None:
        """Initialize the circle item with its initial configuration.

        Args:
            stroke_width: Value used to initialize ``stroke_width``.
            rect: Rectangle used to define geometry or clipping bounds.
        """
        self.stroke_width = stroke_width
        self.rect = rect

    def __copy__(self) -> CircleItem:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(self.stroke_width, copy(self.rect))
