# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Annotation layout model for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from ...core.annotation_types import ArrowType, CircleType, HintArrowType
from ...core.primitives import SQUARES
from ...render.items.arrow_item import ArrowItem
from ...render.items.circle_item import CircleItem
from ..primitives import NULL_RECT, Coord
from .base import Layout

if TYPE_CHECKING:
    from ...core.primitives import Square
    from ..primitives import Color
    from .base import CacheKey


class AnnotationLayout(Layout):
    """Computed layout data for annotation rendering."""

    __slots__ = "_circle_items", "_arrow_item"

    _circle_items: list[CircleItem]
    _arrow_item: ArrowItem

    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        self._circle_items = [CircleItem(1, NULL_RECT) for _ in SQUARES]
        self._arrow_item = ArrowItem(1, 1, 1)

    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        theme = self.theme
        circle_theme = theme.circle
        arrow_theme = theme.arrow
        file_sizes = self.geometry.file_sizes
        rank_sizes = self.geometry.rank_sizes

        a1_mean_dim = (file_sizes[SQUARES[0].file] + rank_sizes[SQUARES[0].rank]) / 2
        stroke_width = max(1, int(a1_mean_dim * circle_theme.stroke_factor))

        for square in SQUARES:
            item = self._circle_items[square.index]
            item.rect = self.square_rects[square.index].scale(circle_theme.scale_factor)
            item.stroke_width = stroke_width

        self._arrow_item.shaft_width = max(1, int(a1_mean_dim * arrow_theme.shaft_factor))
        self._arrow_item.head_length = max(1, int(a1_mean_dim * arrow_theme.head_length_factor))
        self._arrow_item.head_width = max(1, int(a1_mean_dim * arrow_theme.head_width_factor))

    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs.

        Returns:
            The cache key for the current inputs.
        """
        circle_theme = self.theme.circle
        arrow_theme = self.theme.arrow
        return (
            circle_theme.scale_factor,
            circle_theme.stroke_factor,
            arrow_theme.shaft_factor,
            arrow_theme.head_length_factor,
            arrow_theme.head_width_factor,
        )

    def circle(self, circle_type: CircleType, square: Square) -> tuple[CircleItem, Color]:
        """Return the layout item used to render a circle annotation.

        Args:
            circle_type: Circle annotation type to use.
            square: Square where the circle annotation should be rendered.

        Returns:
            The layout item used to render a circle annotation.
        """
        if not self.view_state.white_at_bottom:
            square = square.rotated()

        item = self._circle_items[square.index].copy()
        if circle_type == CircleType.PRIMARY:
            return item, copy(self.theme.circle.primary_fill)
        if circle_type == CircleType.SECONDARY:
            return item, copy(self.theme.circle.secondary_fill)
        return item, copy(self.theme.circle.alternative_fill)

    def arrow(
        self, arrow_type: ArrowType | HintArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> tuple[ArrowItem, Color, tuple[Coord, Coord] | tuple[Coord, Coord, Coord]]:
        """Return the layout item used to render an arrow annotation.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the arrow.
            to_square: End square of the arrow.
            has_corner: Whether the arrow should include a corner.

        Returns:
            The layout item used to render an arrow annotation.
        """
        if from_square == to_square:
            raise ValueError("from_square and to_square cannot be the same for an arrow")

        if not self.view_state.white_at_bottom:
            from_square = from_square.rotated()
            to_square = to_square.rotated()

        arrow_theme = self.theme.arrow
        if arrow_type == ArrowType.PRIMARY:
            color = arrow_theme.primary_fill
        elif arrow_type == ArrowType.SECONDARY:
            color = arrow_theme.secondary_fill
        elif arrow_type == ArrowType.ALTERNATIVE:
            color = arrow_theme.alternative_fill
        elif arrow_type == HintArrowType.PRIMARY:
            color = arrow_theme.hint_primary_fill
        elif arrow_type == HintArrowType.SECONDARY:
            color = arrow_theme.hint_secondary_fill
        else:
            color = arrow_theme.hint_alternative_fill

        from_rect = self.square_rects[from_square.index]
        to_rect = self.square_rects[to_square.index]
        if not has_corner:
            return self._arrow_item.copy(), copy(color), (from_rect.center, to_rect.center)

        delta_x = to_rect.center.x - from_rect.center.x
        delta_y = to_rect.center.y - from_rect.center.y
        if abs(delta_y) >= abs(delta_x):
            bend = Coord(from_rect.center.x, to_rect.center.y)
        else:
            bend = Coord(to_rect.center.x, from_rect.center.y)

        return self._arrow_item.copy(), copy(color), (from_rect.center, bend, to_rect.center)
