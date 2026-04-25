# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Promotion session implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import ChessboardViewError, MoveError
from ..primitives import PlayerColor
from ._helpers import clear_all, update_highlight
from .protocols import PromotionSessionProtocol

if TYPE_CHECKING:
    from ...layout.primitives import Coord
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Piece
    from ..query.board_query import BoardQuery
    from ..state.annotation_state import AnnotationState
    from ..state.highlight_state import HighlightState
    from ..state.piece_ui_state import PieceUiState
    from ..state.promotion_state import PromotionState


class PromotionSession(PromotionSessionProtocol):
    """Coordinates promotion selection and completion."""

    __slots__ = (
        "_game_adapter",
        "_query",
        "_highlight_state",
        "_piece_ui_state",
        "_annotation_state",
        "_promotion_state",
    )

    _game_adapter: GameAdapterProtocol
    _query: BoardQuery
    _highlight_state: HighlightState
    _piece_ui_state: PieceUiState
    _annotation_state: AnnotationState
    _promotion_state: PromotionState

    def __init__(
        self,
        game_adapter: GameAdapterProtocol,
        query: BoardQuery,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> None:
        """Initialize the promotion session with its initial configuration.

        Args:
            game_adapter: Game adapter used to provide board state and rule queries.
            query: Query object used to read board state and derived view data.
            highlight_state: State object used to initialize or update the highlight state.
            piece_ui_state: State object used to initialize or update the piece ui state.
            annotation_state: State object used to initialize or update the annotation state.
            promotion_state: State object used to initialize or update the promotion state.
        """
        self._game_adapter = game_adapter
        self._query = query
        self._highlight_state = highlight_state
        self._piece_ui_state = piece_ui_state
        self._annotation_state = annotation_state
        self._promotion_state = promotion_state

    @classmethod
    def create(
        cls,
        game_adapter: GameAdapterProtocol,
        query: BoardQuery,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> PromotionSession:
        """Create an instance from the provided collaborators.

        Args:
            game_adapter: Game adapter to use.
            query: Board query helper to use.
            highlight_state: Highlight state to update.
            piece_ui_state: Piece UI state to update.
            annotation_state: Annotation state to update.
            promotion_state: Promotion state to update.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(game_adapter, query, highlight_state, piece_ui_state, annotation_state, promotion_state)

    def has_active_promotion(self) -> bool:
        """Return whether promotion selection is currently active.

        Returns:
            ``True`` when the promotion chooser is open and waiting for a piece selection.
        """
        return self._promotion_state.is_active()

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether ``move`` requires a promotion choice.

        Args:
            move: Move to inspect for promotion handling.

        Returns:
            ``True`` when the active game adapter treats ``move`` as a promotion move.
        """
        return self._game_adapter.is_promotion_move(move)

    def promote(self, move: Move) -> None:
        """Apply a promotion move using the selected piece.

        Args:
            move: Promotion move to apply.
        """
        if not self._game_adapter.is_promotion_move(move) or not self._game_adapter.is_legal_move(move):
            raise MoveError(f"move is not a legal promotion move: {move}")
        self._game_adapter.move(move)
        clear_all(self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state)
        update_highlight(self._game_adapter, self._highlight_state, move)

    def show_promotion(self, move: Move, color: PlayerColor, coord: Coord) -> None:
        """Open the promotion chooser for ``move`` and seed its initial highlight.

        Args:
            move: Promotion move awaiting a piece choice.
            color: Player color whose promotion options should be shown.
            coord: Pointer position used to initialize the highlighted promotion choice.
        """
        if self._promotion_state.is_active():
            raise ChessboardViewError("cannot show promotion while another promotion is active")

        if (color is PlayerColor.WHITE and not self._promotion_state.white_promotion_pieces) or (
            color is PlayerColor.BLACK and not self._promotion_state.black_promotion_pieces
        ):
            return

        self._promotion_state.show_promotion(move, color)
        self.update_promotion_highlight(coord)
        self._piece_ui_state.clear_dragged_piece()
        self._piece_ui_state.preview_move = move

    def set_white_promotion_pieces(self, white_promotion_pieces: tuple[Piece, ...]) -> None:
        """Set the white promotion piece options shown by the UI.

        Args:
            white_promotion_pieces: White promotion pieces to store.
        """
        if self._promotion_state.is_active():
            raise ChessboardViewError("cannot change white promotion pieces while promotion is active")
        self._promotion_state.white_promotion_pieces = white_promotion_pieces

    def set_black_promotion_pieces(self, black_promotion_pieces: tuple[Piece, ...]) -> None:
        """Set the black promotion piece options shown by the UI.

        Args:
            black_promotion_pieces: Black promotion pieces to store.
        """
        if self._promotion_state.is_active():
            raise ChessboardViewError("cannot change black promotion pieces while promotion is active")
        self._promotion_state.black_promotion_pieces = black_promotion_pieces

    def update_promotion_highlight(self, coord: Coord) -> None:
        """Update the promotion highlight.

        Args:
            coord: Pointer position used to determine which promotion option is highlighted.
        """
        if not self._promotion_state.is_active():
            return

        index = self._query.promotion_index_at(coord.x, coord.y)
        if index is None or not self._promotion_state.is_valid_index(index):
            self._promotion_state.clear_highlight()
            return
        self._promotion_state.set_highlight(index)

    def clear_promotion_highlight(self) -> None:
        """Clear the currently highlighted promotion choice."""
        self._promotion_state.clear_highlight()

    def commit_promotion(self, coord: Coord) -> None:
        """Commit the currently pointed-at promotion option, if any.

        Args:
            coord: Pointer position used to resolve the selected promotion option.
        """
        if not self._promotion_state.is_active():
            raise ChessboardViewError("cannot commit promotion when no promotion is active")

        try:
            index = self._query.promotion_index_at(coord.x, coord.y)
            if index is not None and self._promotion_state.is_valid_index(index):
                move = self._promotion_state.move
                piece = self._promotion_state.get_piece(index)
                self.promote(move.with_promotion(piece.kind))
        finally:
            self._promotion_state.clear_all()
            self._piece_ui_state.preview_move = None

    def close_promotion(self) -> None:
        """Close the active promotion chooser without applying a promotion."""
        if not self._promotion_state.is_active():
            raise ChessboardViewError("cannot close promotion when no promotion is active")
        self._promotion_state.clear_all()
        self._piece_ui_state.preview_move = None
