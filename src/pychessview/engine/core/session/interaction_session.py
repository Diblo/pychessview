# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Interaction session implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import PieceNotFoundError
from ..highlight_types import HighlightPlayer
from ..primitives import SquareData
from ._helpers import clear_interaction_state, ensure_no_active_promotion, set_hints, set_pseudo_hints
from .protocols import InteractionSessionProtocol

if TYPE_CHECKING:
    from ...layout.primitives import Coord
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Square
    from ..state.annotation_state import AnnotationState
    from ..state.highlight_state import HighlightState
    from ..state.piece_ui_state import PieceUiState
    from ..state.promotion_state import PromotionState
    from ..state.view_state import ViewState


class InteractionSession(InteractionSessionProtocol):
    """Coordinates selection and drag interaction state."""

    __slots__ = (
        "_view_state",
        "_game_adapter",
        "_highlight_state",
        "_piece_ui_state",
        "_promotion_state",
        "_annotation_state",
    )

    _view_state: ViewState
    _game_adapter: GameAdapterProtocol
    _highlight_state: HighlightState
    _piece_ui_state: PieceUiState
    _promotion_state: PromotionState
    _annotation_state: AnnotationState

    def __init__(
        self,
        view_state: ViewState,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        promotion_state: PromotionState,
        annotation_state: AnnotationState,
    ) -> None:
        """Initialize the interaction session with its initial configuration.

        Args:
            view_state: View state used to control the rendered board presentation.
            game_adapter: Game adapter used to provide board state and rule queries.
            highlight_state: State object used to initialize or update the highlight state.
            piece_ui_state: State object used to initialize or update the piece ui state.
            promotion_state: State object used to initialize or update the promotion state.
            annotation_state: State object used to initialize or update the annotation state.
        """
        self._view_state = view_state
        self._game_adapter = game_adapter
        self._highlight_state = highlight_state
        self._piece_ui_state = piece_ui_state
        self._promotion_state = promotion_state
        self._annotation_state = annotation_state

    @classmethod
    def create(
        cls,
        view_state: ViewState,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        promotion_state: PromotionState,
        annotation_state: AnnotationState,
    ) -> InteractionSession:
        """Create an instance from the provided collaborators.

        Args:
            view_state: View state to use.
            game_adapter: Game adapter to use.
            highlight_state: Highlight state to update.
            piece_ui_state: Piece UI state to update.
            promotion_state: Promotion state to update.
            annotation_state: Annotation state to update.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(view_state, game_adapter, highlight_state, piece_ui_state, promotion_state, annotation_state)

    def has_active_selection(self) -> bool:
        """Return whether a square is currently selected.

        Returns:
            ``True`` when a selected square is stored and still contains a piece.
        """
        selected = self._highlight_state.get_selected()
        if selected is None:
            return False
        return self._game_adapter.piece_at(selected[1]) is not None

    def select_piece(self, square: Square) -> None:
        """Mark the piece on the given square as selected.

        Args:
            square: Square whose piece should become the active selection.
        """
        ensure_no_active_promotion(self._promotion_state, "select a piece")
        piece = self._game_adapter.piece_at(square)
        if piece is None:
            raise PieceNotFoundError(f"cannot select empty square {square}")

        self.clear_selection()
        player = self._view_state.player

        if piece.color == player:
            self._highlight_state.set_selected(HighlightPlayer.PLAYER, square)
            if not self._view_state.show_player_hints:
                return
        else:
            self._highlight_state.set_selected(HighlightPlayer.OPPONENT, square)
            if not self._view_state.show_opponent_hints:
                return

        if self._game_adapter.turn == piece.color:
            set_hints(self._view_state, self._game_adapter, self._highlight_state, square)
        else:
            set_pseudo_hints(self._view_state, self._game_adapter, self._highlight_state, square)

    def get_selected(self) -> SquareData | None:
        """Return the currently selected square or selection data, if any.

        Returns:
            The current selection state, or ``None`` when nothing is selected.
        """
        selected = self._highlight_state.get_selected()
        if selected is None:
            return None

        square = selected[1]

        piece = self._game_adapter.piece_at(square)
        if piece is None:
            return None
        return SquareData(square, piece)

    def clear_selection(self) -> None:
        """Clear the active piece selection."""
        self._highlight_state.clear_hints()
        self._highlight_state.clear_selected()

    def has_active_drag(self) -> bool:
        """Return whether a drag operation is currently active.

        Returns:
            ``True`` when a dragged square is stored and still contains a piece.
        """
        piece_ui_state = self._piece_ui_state
        dragged_square = piece_ui_state.dragged_square
        if dragged_square is None:
            return False
        return piece_ui_state.is_dragging() and self._game_adapter.piece_at(dragged_square) is not None

    def begin_drag(self, square: Square, coord: Coord) -> None:
        """Start dragging the piece on the given square from the given coordinate.

        Args:
            square: Square the dragged piece originates from.
            coord: Pointer position where the drag begins, expressed in viewport coordinates.
        """
        ensure_no_active_promotion(self._promotion_state, "begin dragging a piece")
        piece = self._game_adapter.piece_at(square)
        if piece is None:
            raise PieceNotFoundError(f"cannot drag piece from empty square {square}")
        self._piece_ui_state.set_dragged_piece(square, coord)

    def update_drag(self, coord: Coord) -> None:
        """Update the drag.

        Args:
            coord: Updated pointer position in viewport coordinates.
        """
        if not self._piece_ui_state.is_dragging():
            return
        self._piece_ui_state.set_dragged_position(coord)

    def clear_drag(self) -> None:
        """Clear any active drag state."""
        self._piece_ui_state.clear_dragged_piece()

    def set_last_move(self, move: Move) -> None:
        """Store the move that should be highlighted as the last move.

        Args:
            move: Move to highlight as the most recently played move.
        """
        ensure_no_active_promotion(self._promotion_state, "set the last move")
        self._highlight_state.set_last_move(move)

    def clear_last_move(self) -> None:
        """Clear the stored last-move highlight."""
        self._highlight_state.clear_last_move()

    def clear_interaction(self) -> None:
        """Clear all interaction-related highlight and selection state."""
        clear_interaction_state(
            self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state
        )
