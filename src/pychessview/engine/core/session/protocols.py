# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Session protocols for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...layout.primitives import Coord
    from ..annotation_types import ArrowType, CircleType, HintArrowType
    from ..domain.adapters.protocol import GameAdapterProtocol
    from ..primitives import Move, Piece, PlayerColor, Square, SquareData
    from ..query.board_query import BoardQuery
    from ..state.annotation_state import AnnotationState
    from ..state.highlight_state import HighlightState
    from ..state.piece_ui_state import PieceUiState
    from ..state.promotion_state import PromotionState
    from ..state.view_state import ViewState


class GameSessionProtocol(Protocol):
    """Protocol for game session implementations."""

    @classmethod
    def create(
        cls,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> GameSessionProtocol:
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
        ...

    @property
    def fen(self) -> str:
        """Current board position as a FEN string."""
        ...

    def load_fen(self, fen: str, last_move: Move | None = None) -> None:
        """Load the session from a FEN string and optional last move.

        Args:
            fen: FEN string describing the position that should become active.
            last_move: Last move to highlight after loading, or ``None`` to clear the highlight.
        """
        ...

    @property
    def turn(self) -> PlayerColor:
        """Player whose turn it is to move."""
        ...

    def pieces(self) -> dict[Square, Piece]:
        """Return the current piece placement as a mapping from occupied squares to pieces.

        Returns:
            Mapping of occupied squares to their pieces.
        """
        ...

    def piece_at(self, square: Square) -> Piece | None:
        """Return the piece currently placed on the given square, if any.

        Args:
            square: Square to inspect.

        Returns:
            The piece on ``square``, or ``None`` when the square is empty.
        """
        ...

    def add_piece(self, square: Square, piece: Piece) -> None:
        """Add a piece to the given square.

        Args:
            square: Empty square that should receive the new piece.
            piece: Piece to place on ``square``.
        """
        ...

    def remove_piece(self, square: Square) -> None:
        """Remove any piece from the given square.

        Args:
            square: Square whose piece should be removed.
        """
        ...

    def replace_piece(self, square: Square, piece: Piece) -> None:
        """Replace the piece on the given square.

        Args:
            square: Occupied square whose piece should be replaced.
            piece: Piece that should replace the current occupant of ``square``.
        """
        ...

    def king(self, color: PlayerColor) -> Square | None:
        """Return the square occupied by the specified color's king, if present.

        Args:
            color: Player color whose king square should be queried.

        Returns:
            The king square for ``color``, or ``None`` when no king is present.
        """
        ...

    def reset(self, fen: str | None = None) -> None:
        """Reset the game state to the default or provided position.

        Args:
            fen: Optional FEN string to load instead of the adapter's configured default position.
        """
        ...

    def is_legal_move(self, move: Move) -> bool:
        """Return whether ``move`` is legal in the current position.

        Args:
            move: Move to validate against the current position.

        Returns:
            ``True`` when the active adapter accepts ``move`` as legal.
        """
        ...

    def move(self, move: Move) -> None:
        """Apply a move to the current state.

        Args:
            move: Legal move to apply to the current position.
        """
        ...

    def is_check(self) -> bool:
        """Return whether the side to move is currently in check.

        Returns:
            ``True`` when the side to move is currently in check.
        """
        ...

    def is_checkmate(self) -> bool:
        """Return whether the current position is checkmate.

        Returns:
            ``True`` when the active position is checkmate.
        """
        ...


class InteractionSessionProtocol(Protocol):
    """Protocol for interaction session implementations."""

    @classmethod
    def create(
        cls,
        view_state: ViewState,
        game_adapter: GameAdapterProtocol,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        promotion_state: PromotionState,
        annotation_state: AnnotationState,
    ) -> InteractionSessionProtocol:
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
        ...

    # Selection
    def has_active_selection(self) -> bool:
        """Return whether a square is currently selected.

        Returns:
            ``True`` when the interaction session currently stores a selected square.
        """
        ...

    def select_piece(self, square: Square) -> None:
        """Mark the piece on the given square as selected.

        Args:
            square: Square whose piece should become the active selection.
        """
        ...

    def get_selected(self) -> SquareData | None:
        """Return the currently selected square or selection data, if any.

        Returns:
            The current selection state, or ``None`` when nothing is selected.
        """
        ...

    def clear_selection(self) -> None:
        """Clear the active piece selection."""
        ...

    # Drag
    def has_active_drag(self) -> bool:
        """Return whether a drag operation is currently active.

        Returns:
            ``True`` when the interaction session is currently tracking a dragged piece.
        """
        ...

    def begin_drag(self, square: Square, coord: Coord) -> None:
        """Start dragging the piece on the given square from the given coordinate.

        Args:
            square: Square the dragged piece originates from.
            coord: Pointer position where the drag begins, expressed in viewport coordinates.
        """
        ...

    def update_drag(self, coord: Coord) -> None:
        """Update the drag.

        Args:
            coord: Updated pointer position in viewport coordinates.
        """
        ...

    def clear_drag(self) -> None:
        """Clear any active drag state."""
        ...

    # Highlight
    def set_last_move(self, move: Move) -> None:
        """Store the move that should be highlighted as the last move.

        Args:
            move: Move to highlight as the most recently played move.
        """
        ...

    def clear_last_move(self) -> None:
        """Clear the stored last-move highlight."""
        ...

    # Other
    def clear_interaction(self) -> None:
        """Clear all interaction-related highlight and selection state."""
        ...


class PromotionSessionProtocol(Protocol):
    """Protocol for promotion session implementations."""

    @classmethod
    def create(
        cls,
        game_adapter: GameAdapterProtocol,
        query: BoardQuery,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
    ) -> PromotionSessionProtocol:
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
        ...

    def has_active_promotion(self) -> bool:
        """Return whether promotion selection is currently active.

        Returns:
            ``True`` when the promotion chooser is open and waiting for a piece selection.
        """
        ...

    def is_promotion_move(self, move: Move) -> bool:
        """Return whether ``move`` requires a promotion choice.

        Args:
            move: Move to inspect for promotion handling.

        Returns:
            ``True`` when ``move`` reaches a promotion rank and needs a promotion piece.
        """
        ...

    def promote(self, move: Move) -> None:
        """Apply a promotion move using the selected piece.

        Args:
            move: Promotion move to apply.
        """
        ...

    def set_white_promotion_pieces(self, white_promotion_pieces: tuple[Piece, ...]) -> None:
        """Set the white promotion piece options shown by the UI.

        Args:
            white_promotion_pieces: White promotion pieces to store.
        """
        ...

    def set_black_promotion_pieces(self, black_promotion_pieces: tuple[Piece, ...]) -> None:
        """Set the black promotion piece options shown by the UI.

        Args:
            black_promotion_pieces: Black promotion pieces to store.
        """
        ...

    def show_promotion(self, move: Move, color: PlayerColor, coord: Coord) -> None:
        """Open the promotion chooser for ``move`` and seed its initial highlight.

        Args:
            move: Promotion move awaiting a piece choice.
            color: Player color whose promotion options should be shown.
            coord: Pointer position used to initialize the highlighted promotion choice.
        """
        ...

    def update_promotion_highlight(self, coord: Coord) -> None:
        """Update the promotion highlight.

        Args:
            coord: Pointer position used to determine which promotion option is highlighted.
        """
        ...

    def clear_promotion_highlight(self) -> None:
        """Clear the currently highlighted promotion choice."""
        ...

    def commit_promotion(self, coord: Coord) -> None:
        """Commit the currently pointed-at promotion option, if any.

        Args:
            coord: Pointer position used to resolve the selected promotion option.
        """
        ...

    def close_promotion(self) -> None:
        """Close the active promotion chooser without applying a promotion."""
        ...


class AnnotationSessionProtocol(Protocol):
    """Protocol for annotation session implementations."""

    @classmethod
    def create(cls, annotation_state: AnnotationState, promotion_state: PromotionState) -> AnnotationSessionProtocol:
        """Create an instance from the provided collaborators.

        Args:
            annotation_state: Annotation state to update.
            promotion_state: Promotion state to update.

        Returns:
            A newly created instance of ``cls``.
        """
        ...

    def set_circle_preview(self, circle_type: CircleType, square: Square) -> None:
        """Store the preview circle that should be rendered before it is committed.

        Args:
            circle_type: Circle annotation type to use.
            square: Square where the preview circle should be shown.
        """
        ...

    def set_arrow_preview(
        self, arrow_type: ArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store the preview arrow that should be rendered before it is committed.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the preview arrow.
            to_square: End square of the preview arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ...

    def clear_preview(self) -> None:
        """Clear any active annotation preview state."""
        ...

    def add_circle(self, circle_type: CircleType, square: Square) -> None:
        """Store a circle annotation for the given square.

        Args:
            circle_type: Circle annotation type to use.
            square: Square that should carry the circle annotation.
        """
        ...

    def remove_circle(self, square: Square) -> None:
        """Remove the stored circle annotation for the given square.

        Args:
            square: Square whose circle annotation should be removed.
        """
        ...

    def clear_circles(self) -> None:
        """Remove all stored circle annotations."""
        ...

    def add_arrow(
        self, arrow_type: ArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store an arrow annotation between two squares.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the arrow.
            to_square: End square of the arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ...

    def remove_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored arrow annotation between two squares.

        Args:
            from_square: Start square of the stored arrow.
            to_square: End square of the stored arrow.
        """
        ...

    def clear_arrows(self) -> None:
        """Remove all stored arrow annotations."""
        ...

    def add_hint_arrow(
        self, arrow_type: HintArrowType, from_square: Square, to_square: Square, has_corner: bool = False
    ) -> None:
        """Store a hint arrow between two squares.

        Args:
            arrow_type: Arrow annotation type to use.
            from_square: Start square of the hint arrow.
            to_square: End square of the hint arrow.
            has_corner: Whether the arrow should include a corner.
        """
        ...

    def remove_hint_arrow(self, from_square: Square, to_square: Square) -> None:
        """Remove the stored hint arrow between two squares.

        Args:
            from_square: Start square of the stored hint arrow.
            to_square: End square of the stored hint arrow.
        """
        ...

    def clear_hint_arrows(self) -> None:
        """Remove all stored hint arrows."""
        ...
