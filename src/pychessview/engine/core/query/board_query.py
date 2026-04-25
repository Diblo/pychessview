# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board query helpers for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..primitives import Rank, Square

if TYPE_CHECKING:
    from ...layout.layout_engine import LayoutEngine
    from ..state.promotion_state import PromotionState
    from ..state.view_state import ViewState


def _edge_index(coord: int, edges: tuple[int, ...]) -> int | None:
    """Return the board edge index that contains the given coordinate.

    Args:
        coord: Board-space coordinate involved in the operation.
        edges: Value supplied for ``edges``.

    Returns:
        The board edge index that contains the given coordinate.
    """
    for index, (start, end) in enumerate(zip(edges, edges[1:], strict=False)):
        if start <= coord < end:
            return index
    return None


class BoardQuery:
    """Maps viewport coordinates to board and promotion queries."""

    __slots__ = "_view_state", "_promotion_state", "_layout_engine"

    _view_state: ViewState
    _promotion_state: PromotionState
    _layout_engine: LayoutEngine

    def __init__(self, view_state: ViewState, promotion_state: PromotionState, geometry: LayoutEngine) -> None:
        """Initialize the board query with its initial configuration.

        Args:
            view_state: View state used to control the rendered board presentation.
            promotion_state: State object used to initialize or update the promotion state.
            geometry: Value used to initialize ``geometry``.
        """
        self._view_state = view_state
        self._promotion_state = promotion_state
        self._layout_engine = geometry

    def square_at(self, x: int, y: int) -> Square | None:
        """Return the board square at the given viewport coordinate, if any.

        Args:
            x: Horizontal coordinate to use.
            y: Vertical coordinate to use.

        Returns:
            The board square under ``(x, y)``, or ``None`` when the coordinate falls outside the rendered board.
        """
        if not self._layout_engine.is_renderable:
            return None

        file_index = _edge_index(x, self._layout_engine.vertical_edges[1:-1])
        rank_index = _edge_index(y, self._layout_engine.horizontal_edges[1:-1])

        if file_index is None or rank_index is None:
            return None

        square = Square(file_index, Rank.EIGHT - rank_index)
        if self._view_state.white_at_bottom:
            return square

        return square.rotated()

    def promotion_index_at(self, x: int, y: int) -> int | None:
        """Return the promotion choice index at the given viewport coordinate, if any.

        Args:
            x: Horizontal coordinate to use.
            y: Vertical coordinate to use.

        Returns:
            The zero-based promotion option index under ``(x, y)``, or ``None`` when the coordinate does not map
            to a currently valid promotion choice.
        """
        if not self._promotion_state.is_active():
            return None

        target_square = self.square_at(x, y)
        promotion_square = self._promotion_state.move.to_square

        if target_square is None or target_square.file != promotion_square.file:
            return None

        if promotion_square.rank == Rank.EIGHT:
            index = Rank.EIGHT - target_square.rank
        else:
            index = target_square.rank - Rank.ONE

        if not self._promotion_state.is_valid_index(index):
            return None

        return index

    def is_inside(self, x: int, y: int) -> bool:
        """Return whether the given coordinate lies inside the current viewport.

        Args:
            x: Horizontal coordinate to use.
            y: Vertical coordinate to use.

        Returns:
            ``True`` when ``(x, y)`` falls within the viewport rectangle tracked by the layout engine.
        """
        return (
            self._layout_engine.viewport.left <= x < self._layout_engine.viewport.right
            and self._layout_engine.viewport.top <= y < self._layout_engine.viewport.bottom
        )
