# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Promotion layout model for the pychessview package.

Type Variables:
    T: Generic slot type used when building cached promotion rows.
"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, TypeVar

from ...core.exceptions import LayoutError
from ...core.primitives import File, Rank, Square
from ...render.items.color_square_item import ColorSquareItem
from ...render.items.image_square_item import ImageSquareItem
from .._helpers import fit_piece_asset_rect
from ..primitives import NULL_RECT, Color
from .base import Layout

if TYPE_CHECKING:
    from collections.abc import Callable

    from ...core.primitives import Piece
    from ..primitives import Rect
    from .base import CacheKey


class _RectSlot:
    """Stores a rectangle in a mutable slot.

    Attributes:
        rect: Rectangle value stored in the slot.
    """

    __slots__ = "rect"

    rect: Rect

    def __init__(self, rect: Rect) -> None:
        """Initialize the _ rect slot with its initial configuration.

        Args:
            rect: Rectangle used to define geometry or clipping bounds.
        """
        self.rect = rect


T = TypeVar("T")
"""Generic type variable used by helper factories in this module."""


def _build_file_rows(factory: Callable[[], T]) -> tuple[tuple[tuple[T, ...], ...], tuple[tuple[T, ...], ...]]:
    """Build per-file row caches and their reversed variants.

    Args:
        factory: Value supplied for ``factory``.

    Returns:
        Per-file row caches and their reversed variants.
    """
    rows: list[tuple[T, ...]] = []
    rows_reversed: list[tuple[T, ...]] = []

    for _ in File:
        row = tuple(factory() for _ in Rank)
        rows.append(row)
        rows_reversed.append(tuple(reversed(row)))

    return tuple(rows), tuple(rows_reversed)


class PromotionLayout(Layout):
    """Computed layout data for promotion rendering."""

    __slots__ = (
        "_fill_items",
        "_highlight_items",
        "_piece_rects",
        "_fill_items_reversed",
        "_highlight_items_reversed",
        "_piece_rects_reversed",
    )

    _fill_items: tuple[tuple[ColorSquareItem, ...], ...]
    _highlight_items: tuple[tuple[ColorSquareItem, ...], ...]
    _piece_rects: tuple[tuple[_RectSlot, ...], ...]

    _fill_items_reversed: tuple[tuple[ColorSquareItem, ...], ...]
    _highlight_items_reversed: tuple[tuple[ColorSquareItem, ...], ...]
    _piece_rects_reversed: tuple[tuple[_RectSlot, ...], ...]

    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        self._fill_items, self._fill_items_reversed = _build_file_rows(
            lambda: ColorSquareItem(Color(0, 0, 0), NULL_RECT)
        )
        self._highlight_items, self._highlight_items_reversed = _build_file_rows(
            lambda: ColorSquareItem(Color(0, 0, 0), NULL_RECT)
        )
        self._piece_rects, self._piece_rects_reversed = _build_file_rows(lambda: _RectSlot(NULL_RECT))

    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        promotion_theme = self.theme.promotion

        for file in File:
            file_fill_items = self._fill_items[file]
            file_highlight_items = self._highlight_items[file]
            file_piece_rects = self._piece_rects[file]

            for rank in Rank:
                rect = self.square_rects[Square(file, rank).index]

                file_fill_items[rank].color = promotion_theme.fill
                file_fill_items[rank].rect = rect

                file_highlight_items[rank].color = promotion_theme.highlight_fill
                file_highlight_items[rank].rect = rect

                file_piece_rects[rank].rect = rect.scale(promotion_theme.piece_factor)

    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs.

        Returns:
            The cache key for the current inputs.
        """
        promotion_theme = self.theme.promotion
        return promotion_theme.piece_factor, promotion_theme.fill, promotion_theme.highlight_fill

    def fill_item(self, promotion_square: Square, index: int) -> ColorSquareItem:
        """Return the fill item for the promotion chooser.

        Args:
            promotion_square: Promotion square to inspect.
            index: Zero-based promotion option row to render.

        Returns:
            The fill item for the promotion chooser background.
        """
        if promotion_square.rank not in (Rank.ONE, Rank.EIGHT):
            raise LayoutError(f"invalid promotion square: {promotion_square}, rank must be 1 or 8")

        if not 0 <= index <= 7:
            raise LayoutError(f"invalid index: {index}, index must be in [0, 7]")

        if not self.view_state.white_at_bottom:
            promotion_square = promotion_square.rotated()

        if promotion_square.rank == Rank.EIGHT:
            fill_items = self._fill_items_reversed[promotion_square.file]
        else:
            fill_items = self._fill_items[promotion_square.file]
        return fill_items[index].copy()

    def highlight_fill_item(self, promotion_square: Square, index: int) -> ColorSquareItem:
        """Return the fill item for the highlighted promotion choice.

        Args:
            promotion_square: Promotion square to inspect.
            index: Zero-based promotion option row whose highlight fill should be returned.

        Returns:
            The fill item for the highlighted promotion choice.
        """
        if promotion_square.rank not in (Rank.ONE, Rank.EIGHT):
            raise LayoutError(f"invalid promotion square: {promotion_square}, rank must be 1 or 8")

        if not 0 <= index <= 7:
            raise LayoutError(f"invalid index: {index}, index must be in [0, 7]")

        if not self.view_state.white_at_bottom:
            promotion_square = promotion_square.rotated()

        if promotion_square.rank == Rank.EIGHT:
            return self._highlight_items_reversed[promotion_square.file][index].copy()
        return self._highlight_items[promotion_square.file][index].copy()

    def piece_item(self, promotion_square: Square, index: int, piece: Piece) -> ImageSquareItem:
        """Return the render item used to draw a piece.

        Args:
            promotion_square: Promotion square to inspect.
            index: Zero-based promotion option row where the piece should be rendered.
            piece: Promotion piece whose asset should be rendered.

        Returns:
            The render item used to draw the piece.
        """
        if promotion_square.rank not in (Rank.ONE, Rank.EIGHT):
            raise LayoutError(f"invalid promotion square: {promotion_square}, rank must be 1 or 8")

        if not 0 <= index <= 7:
            raise LayoutError(f"invalid index: {index}, index must be in [0, 7]")

        if not self.view_state.white_at_bottom:
            promotion_square = promotion_square.rotated()

        if promotion_square.rank == Rank.EIGHT:
            rect = self._piece_rects_reversed[promotion_square.file][index].rect
        else:
            rect = self._piece_rects[promotion_square.file][index].rect

        piece_asset = copy(self.theme.piece.assets[piece])
        return ImageSquareItem(piece_asset, fit_piece_asset_rect(piece_asset, rect))
