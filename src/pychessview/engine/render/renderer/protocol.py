# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Renderer protocol definitions for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...layout.primitives import Color, Coord, Viewport
    from ..items.arrow_item import ArrowItem
    from ..items.circle_item import CircleItem
    from ..items.color_square_item import ColorSquareItem
    from ..items.image_square_item import ImageSquareItem
    from ..items.label_item import LabelItem


class RendererProtocol(Protocol):
    """Protocol for renderers that draw pychessview items."""

    def begin_frame(self, viewport: Viewport) -> None:
        """Begin drawing a frame.

        Args:
            viewport: Viewport to render.
        """
        ...

    def draw_square_color(self, item: ColorSquareItem) -> None:
        """Draw a solid-color square item.

        Args:
            item: Render item to process.
        """
        ...

    def draw_square_image(self, item: ImageSquareItem) -> None:
        """Draw an image-backed square item.

        Args:
            item: Render item to process.
        """
        ...

    def draw_text_ink(self, item: LabelItem) -> None:
        """Draw a text label item.

        Args:
            item: Render item to process.
        """
        ...

    def draw_circle(self, item: CircleItem, color: Color) -> None:
        """Draw a circle item.

        Args:
            item: Render item to process.
            color: Stroke color to use for the circle.
        """
        ...

    def draw_arrow(
        self, item: ArrowItem, color: Color, points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]
    ) -> None:
        """Draw an arrow item.

        Args:
            item: Render item to process.
            color: Fill color to use for the arrow geometry.
            points: Arrow geometry points to draw.
        """
        ...

    def end_frame(self) -> None:
        """Finish drawing a frame."""
        ...
