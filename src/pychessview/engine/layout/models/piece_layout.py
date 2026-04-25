# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Piece layout model for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from ...core.primitives import SQUARES
from ...render.items.image_square_item import ImageSquareItem
from .._helpers import fit_piece_asset_rect
from ..primitives import NULL_RECT
from .base import Layout

if TYPE_CHECKING:
    from ...core.primitives import Piece, Square
    from ..primitives import Coord, Rect
    from .base import CacheKey


class PieceLayout(Layout):
    """Computed layout data for piece rendering."""

    __slots__ = "_piece_rects", "_drag_rects"

    _piece_rects: list[Rect]
    _drag_rects: list[Rect]

    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        self._piece_rects = [NULL_RECT] * 64
        self._drag_rects = [NULL_RECT] * 64

    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        piece_theme = self.theme.piece
        piece_factor = piece_theme.factor
        piece_drag_factor = piece_theme.drag_factor

        for square in SQUARES:
            piece_rect = self.square_rects[square.index].scale(piece_factor)
            self._piece_rects[square.index] = piece_rect
            self._drag_rects[square.index] = piece_rect.scale(piece_drag_factor)

    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs.

        Returns:
            The cache key for the current inputs.
        """
        piece_theme = self.theme.piece
        return piece_theme.factor, piece_theme.drag_factor

    def piece_item(self, piece: Piece, square: Square) -> ImageSquareItem:
        """Return the render item used to draw a piece.

        Args:
            piece: Piece whose asset should be rendered.
            square: Square where the piece should be drawn.

        Returns:
            The render item used to draw the piece.
        """
        if not self.view_state.white_at_bottom:
            square = square.rotated()

        piece_asset = self.theme.piece.assets[piece]
        rect = self._piece_rects[square.index]
        return ImageSquareItem(copy(piece_asset), fit_piece_asset_rect(piece_asset, rect))

    def drag_item(self, piece: Piece, square: Square, coord: Coord) -> ImageSquareItem:
        """Return the render item used for the dragged piece preview.

        Args:
            piece: Piece whose asset should be rendered for the drag preview.
            square: Square the dragged piece originated from.
            coord: Pointer position in viewport coordinates.

        Returns:
            The render item used to draw the dragged piece preview.
        """
        geometry = self.geometry

        if not self.view_state.white_at_bottom:
            square = square.rotated()

        piece_asset = self.theme.piece.assets[piece]
        rect = fit_piece_asset_rect(piece_asset, self._drag_rects[square.index])

        x = coord.x - rect.width // 2
        y = coord.y - rect.height // 2

        min_x = geometry.vertical_edges[0]
        min_y = geometry.horizontal_edges[0]
        max_x = geometry.vertical_edges[-1] - rect.width
        max_y = geometry.horizontal_edges[-1] - rect.height

        clamped_x = min(max(x, min_x), max_x)
        clamped_y = min(max(y, min_y), max_y)

        return ImageSquareItem(copy(piece_asset), rect.with_xy(clamped_x, clamped_y))
