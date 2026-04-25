# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Game session implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import MoveError, PieceNotFoundError, SquareOccupiedError
from ._helpers import clear_all, clear_interaction_state, ensure_no_active_promotion, update_highlight
from .protocols import GameSessionProtocol

if TYPE_CHECKING:
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Piece, PlayerColor, Square
    from ..state.annotation_state import AnnotationState
    from ..state.highlight_state import HighlightState
    from ..state.piece_ui_state import PieceUiState
    from ..state.promotion_state import PromotionState


class GameSession(GameSessionProtocol):
    """Coordinates game-state operations against the active adapter."""

    __slots__ = "_game_adapter", "_highlight_state", "_piece_ui_state", "_annotation_state", "_promotion_state"

    _game_adapter: GameAdapterProtocol
    _highlight_state: HighlightState
    _piece_ui_state: PieceUiState
    _annotation_state: AnnotationState
    _promotion_state: PromotionState

    def __init__(
        self,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> None:
        """Initialize the game session with its initial configuration.

        Args:
            game_adapter: Game adapter used to provide board state and rule queries.
            highlight_state: State object used to initialize or update the highlight state.
            piece_ui_state: State object used to initialize or update the piece ui state.
            annotation_state: State object used to initialize or update the annotation state.
            promotion_state: State object used to initialize or update the promotion state.
        """
        self._game_adapter = game_adapter
        self._highlight_state = highlight_state
        self._piece_ui_state = piece_ui_state
        self._annotation_state = annotation_state
        self._promotion_state = promotion_state

    @classmethod
    def create(
        cls,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> GameSession:
        """Create an instance from the provided collaborators.

        Args:
            game_adapter: Game adapter to use.
            highlight_state: Highlight state to update.
            piece_ui_state: Piece UI state to update.
            annotation_state: Annotation state to update.
            promotion_state: Promotion state to update.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(game_adapter, highlight_state, piece_ui_state, annotation_state, promotion_state)

    @property
    def fen(self) -> str:
        """Current board position as a FEN string.

        Returns:
            Current board position as a FEN string.
        """
        return self._game_adapter.fen

    def load_fen(self, fen: str, last_move: Move | None = None) -> None:
        """Load the session from a FEN string and optional last move.

        Args:
            fen: FEN string describing the position that should become active.
            last_move: Last move to highlight after loading, or ``None`` to clear the highlight.
        """
        self._game_adapter.fen = fen
        clear_all(self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state)
        update_highlight(self._game_adapter, self._highlight_state, last_move)

    @property
    def turn(self) -> PlayerColor:
        """Player whose turn it is to move.

        Returns:
            Player whose turn it is to move.
        """
        return self._game_adapter.turn

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement as a mapping from occupied squares to pieces.

        Returns:
            Mapping of occupied squares to their pieces.
        """
        return self._game_adapter.pieces()

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently placed on the given square, if any.

        Args:
            square: Square to inspect.

        Returns:
            The piece on ``square``, or ``None`` when the square is empty.
        """
        return self._game_adapter.piece_at(square)

    def add_piece(self, square: Square, piece: Piece) -> None:
        """Add a piece to the given square.

        Args:
            square: Empty square that should receive the new piece.
            piece: Piece to place on ``square``.
        """
        ensure_no_active_promotion(self._promotion_state, "add a piece")
        if self._game_adapter.piece_at(square) is not None:
            raise SquareOccupiedError(f"cannot add piece to occupied square {square}")
        self._game_adapter.set_piece(square, piece)
        clear_interaction_state(
            self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state
        )
        update_highlight(self._game_adapter, self._highlight_state)

    def remove_piece(self, square: Square) -> None:
        """Remove any piece from the given square.

        Args:
            square: Square whose piece should be removed.
        """
        ensure_no_active_promotion(self._promotion_state, "remove a piece")
        if self._game_adapter.piece_at(square) is None:
            raise PieceNotFoundError(f"cannot remove piece from empty square {square}")
        self._game_adapter.set_piece(square, None)
        clear_interaction_state(
            self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state
        )
        update_highlight(self._game_adapter, self._highlight_state)

    def replace_piece(self, square: Square, piece: Piece) -> None:
        """Replace the piece on the given square.

        Args:
            square: Occupied square whose piece should be replaced.
            piece: Piece that should replace the current occupant of ``square``.
        """
        ensure_no_active_promotion(self._promotion_state, "replace a piece")
        if self._game_adapter.piece_at(square) is None:
            raise PieceNotFoundError(f"cannot replace piece from empty square {square}")
        self._game_adapter.set_piece(square, piece)
        clear_interaction_state(
            self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state
        )
        update_highlight(self._game_adapter, self._highlight_state)

    def king(self, color: PlayerColor) -> Square | None:
        """Return the square occupied by the specified color's king, if present.

        Args:
            color: Player color whose king square should be queried.

        Returns:
            The king square for ``color``, or ``None`` when no king is present.
        """
        return self._game_adapter.king(color)

    def reset(self, fen: str | None = None) -> None:
        """Reset the game state to the default or provided position.

        Args:
            fen: Optional FEN string to load instead of the adapter's configured default position.
        """
        next_fen = fen if fen is not None and fen.strip() else self._game_adapter.default_fen
        self._game_adapter.fen = next_fen
        clear_all(self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state)
        update_highlight(self._game_adapter, self._highlight_state)

    def is_legal_move(self, move: Move) -> bool:
        """Return whether ``move`` is legal in the current position.

        Args:
            move: Move to validate against the current position.

        Returns:
            ``True`` when the active adapter accepts ``move`` as legal.
        """
        return self._game_adapter.is_legal_move(move)

    def move(self, move: Move) -> None:
        """Apply a move to the current state.

        Args:
            move: Legal move to apply to the current position.
        """
        ensure_no_active_promotion(self._promotion_state, "move a piece")
        if self._game_adapter.is_promotion_move(move) or not self._game_adapter.is_legal_move(move):
            raise MoveError(f"move is not a legal move: {move}")
        self._game_adapter.move(move)
        clear_all(self._highlight_state, self._piece_ui_state, self._promotion_state, self._annotation_state)
        update_highlight(self._game_adapter, self._highlight_state, move)

    def is_check(self) -> bool:
        """Return whether the side to move is currently in check.

        Returns:
            ``True`` when the active adapter reports the side to move as in check.
        """
        return self._game_adapter.is_check()

    def is_checkmate(self) -> bool:
        """Return whether the current position is checkmate.

        Returns:
            ``True`` when the active adapter reports the current position as checkmate.
        """
        return self._game_adapter.is_checkmate()
