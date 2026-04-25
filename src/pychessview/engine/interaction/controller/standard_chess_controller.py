# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Chess controller implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...core.annotation_types import ArrowType, CircleType
from ...core.primitives import Move, Piece, PieceKind
from ..controller_event_result import ControllerEventResult
from ..input.modifiers import Modifier
from ..input.mouse_buttons import MouseButton
from .protocols import ControllerProtocol

if TYPE_CHECKING:
    from typing import Final

    from ...core.primitives import Square
    from ...core.query.board_query import BoardQuery
    from ...core.session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from ...core.state.view_state import ViewState
    from ...layout.primitives import Coord


class _SquareData:
    """Stores a square together with the piece currently on it.

    Attributes:
        square: Board square represented by the snapshot.
        piece: Piece on the square, if one is present.
    """

    __slots__ = "square", "piece"

    square: Final[Square]
    piece: Final[Piece] | None

    def __init__(self, square: Square, piece: Piece | None) -> None:
        """Initialize the square data with its initial configuration.

        Args:
            square: Board square represented by the snapshot.
            piece: Piece on the square, if one is present.
        """
        self.square = square
        self.piece = piece

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            A readable description of the square snapshot and its current piece, if any.
        """
        if self.piece is None:
            return f"square {self.square.file.text}{self.square.rank.value} without a piece"
        return f"square {self.square.file.text}{self.square.rank.value} with {str(self.piece)}"

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            A debug-oriented string that includes the square snapshot fields.
        """
        return f"_SquareData(square={repr(self.square)}, piece={repr(self.piece)})"


class _AnnotationInteraction:
    """Manage annotation creation, deletion, preview, and cancellation."""

    __slots__ = "_annotation", "_origin", "_delete_mode", "_circle_type", "_arrow_type"

    _annotation: AnnotationSessionProtocol
    _origin: Square | None
    _delete_mode: bool
    _circle_type: CircleType
    _arrow_type: ArrowType

    def __init__(self, annotation: AnnotationSessionProtocol) -> None:
        """Initialize the annotation controller.

        Args:
            annotation: Annotation session that stores previews, circles, and arrows.
        """
        self._annotation = annotation
        self._origin = None
        self._delete_mode = False
        self._circle_type = CircleType.PRIMARY
        self._arrow_type = ArrowType.PRIMARY

    def is_active(self) -> bool:
        """Return whether an annotation interaction is active.

        Returns:
            ``True`` when an annotation start square is currently stored.
        """
        return self._origin is not None

    def is_delete_mode(self) -> bool:
        """Return whether the active annotation interaction deletes annotations.

        Returns:
            ``True`` when the active annotation interaction should remove existing annotations.
        """
        return self._delete_mode

    def begin(self, square: Square, modifier: Modifier) -> ControllerEventResult:
        """Begin an annotation creation interaction.

        Args:
            square: Square where the annotation interaction starts.
            modifier: Keyboard modifier that selects the annotation style.

        Returns:
            Controller event result describing whether preview rendering is required.
        """
        self._origin = square
        self._delete_mode = False

        if modifier is Modifier.SHIFT:
            self._circle_type = CircleType.PRIMARY
            self._arrow_type = ArrowType.PRIMARY
        elif modifier is Modifier.CTRL:
            self._circle_type = CircleType.SECONDARY
            self._arrow_type = ArrowType.SECONDARY
        else:
            self._circle_type = CircleType.ALTERNATIVE
            self._arrow_type = ArrowType.ALTERNATIVE

        self._annotation.set_circle_preview(self._circle_type, square)

        return ControllerEventResult(handled=True, requires_render=True)

    def begin_delete(self, square: Square) -> ControllerEventResult:
        """Begin an annotation deletion interaction.

        Args:
            square: Square where the deletion interaction starts.

        Returns:
            Controller event result describing whether preview rendering is required.
        """
        self._origin = square
        self._delete_mode = True
        self._annotation.clear_preview()
        return ControllerEventResult(handled=True, requires_render=True)

    def update(self, square: Square | None) -> ControllerEventResult:
        """Update the active annotation preview.

        Args:
            square: Square currently under the pointer, or ``None`` when the pointer is outside the board.

        Returns:
            Controller event result describing whether preview rendering is required.
        """
        if square is None or self._origin is None:
            return ControllerEventResult()
        if self._delete_mode:
            return ControllerEventResult(handled=True)

        if self._origin == square:
            self._annotation.set_circle_preview(self._circle_type, self._origin)
            return ControllerEventResult(handled=True, requires_render=True)

        self._annotation.set_arrow_preview(self._arrow_type, self._origin, square, False)
        return ControllerEventResult(handled=True, requires_render=True)

    def commit(self, square: Square) -> None:
        """Commit the active annotation interaction.

        Args:
            square: Square where the annotation interaction ends.
        """
        if self._origin is None:
            return

        if self._delete_mode:
            if self._origin == square:
                self._annotation.remove_circle(self._origin)
            else:
                self._annotation.remove_arrow(self._origin, square)
        elif self._origin == square:
            self._annotation.add_circle(self._circle_type, self._origin)
        else:
            self._annotation.add_arrow(self._arrow_type, self._origin, square, False)

        self.cancel()

    def release(self, square: Square | None) -> ControllerEventResult:
        """Handle release for the active annotation interaction.

        Args:
            square: Board square under the release coordinate, or ``None`` when the release is outside the board.

        Returns:
            Controller event result requiring redraw after annotation commit or cancellation.
        """
        if square is None:
            self.cancel()
        else:
            self.commit(square)
        return ControllerEventResult(handled=True, requires_render=True)

    def cancel(self) -> None:
        """Cancel the active annotation interaction."""
        self._annotation.clear_preview()
        self._origin = None
        self._delete_mode = False


class _PromotionInteraction:
    """Manage promotion interaction routing and cleanup."""

    __slots__ = "_promotion"

    _promotion: PromotionSessionProtocol

    def __init__(self, promotion: PromotionSessionProtocol) -> None:
        """Initialize the promotion interaction controller.

        Args:
            promotion: Promotion session that manages active promotion choices.
        """
        self._promotion = promotion

    def is_active(self) -> bool:
        """Return whether a promotion interaction is active.

        Returns:
            ``True`` when a promotion choice is currently shown.
        """
        return self._promotion.has_active_promotion()

    def update(self, coord: Coord) -> ControllerEventResult:
        """Update promotion highlighting for a pointer coordinate.

        Args:
            coord: Pointer position in viewport coordinates.

        Returns:
            Controller event result requiring a redraw after the highlight update.
        """
        self._promotion.update_promotion_highlight(coord)
        return ControllerEventResult(handled=True, requires_render=True)

    def release(self, coord: Coord, button: MouseButton) -> ControllerEventResult:
        """Handle release while promotion is active.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the release.

        Returns:
            Controller event result for the promotion release.
        """
        if button is MouseButton.RIGHT:
            return ControllerEventResult()
        self._promotion.commit_promotion(coord)
        return ControllerEventResult(handled=True, requires_render=True)

    def clear_highlight(self) -> ControllerEventResult:
        """Clear the active promotion highlight.

        Returns:
            Controller event result requiring a redraw after highlight cleanup.
        """
        self._promotion.clear_promotion_highlight()
        return ControllerEventResult(requires_render=True)


class _PieceInteraction:
    """Manage piece selection, drag state, move validation, and move execution."""

    __slots__ = "_view_state", "_game", "_interaction", "_promotion", "_query"

    _view_state: ViewState
    _game: GameSessionProtocol
    _interaction: InteractionSessionProtocol
    _promotion: PromotionSessionProtocol
    _query: BoardQuery

    def __init__(
        self,
        *,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> None:
        """Initialize the piece interaction controller.

        Args:
            view_state: View state that controls selection and drag restrictions.
            game: Game session that exposes board-state operations.
            interaction: Interaction session that manages selection and drag state.
            promotion: Promotion session used to detect promotion moves.
            query: Board query helper that maps viewport coordinates to board data.
        """
        self._view_state = view_state
        self._game = game
        self._interaction = interaction
        self._promotion = promotion
        self._query = query

    def square_at(self, coord: Coord) -> Square | None:
        """Return the board square located at the given viewport coordinate, if any.

        Args:
            coord: Pointer position in viewport coordinates.

        Returns:
            The square under ``coord``, or ``None`` when the pointer is outside the board.
        """
        return self._query.square_at(coord.x, coord.y)

    def clear_selection(self) -> None:
        """Clear any selected piece."""
        self._interaction.clear_selection()

    def has_active_drag(self) -> bool:
        """Return whether a drag interaction is active.

        Returns:
            ``True`` when a piece drag is currently active.
        """
        return self._interaction.has_active_drag()

    def update_drag(self, coord: Coord) -> ControllerEventResult:
        """Update active piece drag coordinates.

        Args:
            coord: Pointer position in viewport coordinates.

        Returns:
            Controller event result requiring redraw when drag is active.
        """
        if self._interaction.has_active_drag():
            self._interaction.update_drag(coord)
            return ControllerEventResult(handled=True, requires_render=True)

        return ControllerEventResult()

    def clear_drag(self) -> ControllerEventResult:
        """Clear active drag state.

        Returns:
            Controller event result requiring redraw after drag cleanup.
        """
        self._interaction.clear_drag()
        return ControllerEventResult(requires_render=True)

    def press_square(self, square: Square, coord: Coord) -> ControllerEventResult:
        """Handle a non-annotation press on a board square.

        Args:
            square: Board square under the pointer.
            coord: Pointer position in viewport coordinates.

        Returns:
            Controller event result describing selection or drag changes.
        """
        if self._can_move_selected_to(square):
            return ControllerEventResult(handled=True)

        piece = self._game.piece_at(square)
        if piece is None:
            self._interaction.clear_selection()
            return ControllerEventResult(requires_render=True)

        is_player_piece = piece.color == self._view_state.player

        if self._view_state.restrict_to_player_pieces and not is_player_piece:
            self._interaction.clear_selection()
            return ControllerEventResult(requires_render=True)

        self._interaction.select_piece(square)

        if self._can_drag(piece):
            self._interaction.begin_drag(square, coord)

        return ControllerEventResult(handled=True, requires_render=True)

    def release(self, coord: Coord) -> ControllerEventResult:
        """Handle a non-annotation release for selection and move execution.

        Args:
            coord: Pointer position in viewport coordinates.

        Returns:
            Controller event result describing move execution or cleanup.
        """
        selected_data = self._interaction.get_selected()
        if selected_data is None:
            return ControllerEventResult()

        square_data = self._get_square_data(coord)
        if square_data is None:
            if self._interaction.has_active_drag():
                self._interaction.clear_drag()
            else:
                self._interaction.clear_selection()
            return ControllerEventResult(handled=True, requires_render=True)

        self._interaction.clear_drag()

        if selected_data.square != square_data.square:
            move = Move(selected_data.square, square_data.square)
            if self._promotion.is_promotion_move(move):
                if self._game.is_legal_move(move.with_promotion(PieceKind.QUEEN)):
                    self._promotion.show_promotion(move, self._game.turn, coord)
                    return ControllerEventResult(handled=True, requires_render=True)
            elif self._can_move_selected_to(square_data.square):
                self._game.move(move)
                return ControllerEventResult(handled=True, requires_render=True)

        return ControllerEventResult(requires_render=True)

    def _get_square_data(self, coord: Coord) -> _SquareData | None:
        """Return square data for the given viewport coordinate.

        Args:
            coord: Pointer position in viewport coordinates.

        Returns:
            A square snapshot for the square under ``coord``, or ``None`` when the pointer is outside the board.
        """
        square = self._query.square_at(coord.x, coord.y)
        if square is None:
            return None

        return _SquareData(square, self._game.piece_at(square))

    def _can_move_selected_to(self, square: Square) -> bool:
        """Return whether the currently selected piece can move to the target square.

        Args:
            square: Destination square to validate against the current selection.

        Returns:
            ``True`` when the currently selected piece has a legal move to ``square``.
        """
        selected_data = self._interaction.get_selected()
        if selected_data is None:
            return False

        move = Move(selected_data.square, square)
        if self._promotion.is_promotion_move(move):
            move = move.with_promotion(PieceKind.QUEEN)

        return self._game.is_legal_move(move)

    def _can_drag(self, piece: Piece) -> bool:
        """Return whether the given piece may start a drag interaction.

        Args:
            piece: Piece that would be dragged if interaction is allowed.

        Returns:
            ``True`` when dragging ``piece`` is allowed under the current turn and view restrictions.
        """
        if self._game.is_checkmate():
            return False

        is_player_piece = piece.color == self._view_state.player
        is_players_turn = self._game.turn == self._view_state.player
        allow_opponent_move = not self._view_state.restrict_to_select_opponent_pieces
        return (is_player_piece and is_players_turn) or (
            not is_player_piece and not is_players_turn and allow_opponent_move
        )


class StandardChessController(ControllerProtocol):
    """Controller that routes standard chess input behavior."""

    __slots__ = "_view_state", "_annotation_interaction", "_piece_interaction", "_promotion_interaction"

    _view_state: ViewState
    _annotation_interaction: _AnnotationInteraction
    _piece_interaction: _PieceInteraction
    _promotion_interaction: _PromotionInteraction

    def __init__(
        self,
        *,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        annotation: AnnotationSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> None:
        """Initialize the chess controller with the collaborators required to process board input.

        Args:
            view_state: View state that controls interaction rules and board orientation.
            game: Game session that exposes board-state operations.
            interaction: Interaction session that manages selection and drag state.
            annotation: Annotation session that manages circles and arrows.
            promotion: Promotion session that manages promotion choice flow.
            query: Board query helper that maps viewport coordinates to board data.
        """
        self._view_state = view_state
        self._annotation_interaction = _AnnotationInteraction(annotation)
        self._piece_interaction = _PieceInteraction(
            view_state=view_state,
            game=game,
            interaction=interaction,
            promotion=promotion,
            query=query,
        )
        self._promotion_interaction = _PromotionInteraction(promotion)

    @classmethod
    def create(
        cls,
        *,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        annotation: AnnotationSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> StandardChessController:
        """Create an instance from the provided collaborators.

        Args:
            view_state: View state to use.
            game: Game session that exposes board-state operations.
            interaction: Interaction session that manages selection and drag state.
            annotation: Annotation session that manages circles and arrows.
            promotion: Promotion session that manages promotion choice flow.
            query: Board query helper to use.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(
            view_state=view_state,
            game=game,
            interaction=interaction,
            annotation=annotation,
            promotion=promotion,
            query=query,
        )

    def on_press(
        self,
        coord: Coord,
        button: MouseButton,
        modifier: Modifier | None = None,
    ) -> ControllerEventResult:
        """Handle the press event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the press initiated
            or contributed to an active interaction step and whether the view
            should be redrawn.
        """
        if self._promotion_interaction.is_active():
            return ControllerEventResult()

        square = self._piece_interaction.square_at(coord)
        if square is None:
            self._piece_interaction.clear_selection()
            return ControllerEventResult(requires_render=True)

        if button is MouseButton.RIGHT:
            if not self._view_state.annotations_enabled:
                return ControllerEventResult()
            return self._annotation_interaction.begin_delete(square)

        if modifier is not None:
            if not self._view_state.annotations_enabled:
                return ControllerEventResult()
            return self._annotation_interaction.begin(square, modifier)

        return self._piece_interaction.press_square(square, coord)

    def on_press_outside_view(self) -> ControllerEventResult:
        """Handle the press outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        return ControllerEventResult()

    def on_pointer_move(self, coord: Coord, modifier: Modifier | None = None) -> ControllerEventResult:
        """Handle the pointer move event.

        Args:
            coord: Pointer position in viewport coordinates.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the move contributed
            to an active interaction step and whether the view should be
            redrawn.
        """
        _ = modifier

        if self._promotion_interaction.is_active():
            return self._promotion_interaction.update(coord)

        if self._annotation_interaction.is_active():
            return self._annotation_interaction.update(self._piece_interaction.square_at(coord))

        return self._piece_interaction.update_drag(coord)

    def on_pointer_move_outside_view(self) -> ControllerEventResult:
        """Handle the pointer move outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        if self._promotion_interaction.is_active():
            return self._promotion_interaction.clear_highlight()

        if self._piece_interaction.has_active_drag():
            return self._piece_interaction.clear_drag()

        return ControllerEventResult()

    def on_release(
        self,
        coord: Coord,
        button: MouseButton,
        modifier: Modifier | None = None,
    ) -> ControllerEventResult:
        """Handle the release event.

        Args:
            coord: Pointer position in viewport coordinates.
            button: Mouse button that triggered the event.
            modifier: Optional keyboard modifier.

        Returns:
            A controller event result describing whether the release completed
            or modified an active interaction step and whether the view should
            be redrawn.
        """
        _ = modifier

        if self._promotion_interaction.is_active():
            return self._promotion_interaction.release(coord, button)

        if self._annotation_interaction.is_active():
            return self._annotation_interaction.release(self._piece_interaction.square_at(coord))

        if button is MouseButton.RIGHT:
            return ControllerEventResult()

        return self._piece_interaction.release(coord)

    def on_release_outside_view(self) -> ControllerEventResult:
        """Handle the release outside view event.

        Returns:
            A controller event result describing any required visual cleanup
            or redraw outside the board view.
        """
        if self._promotion_interaction.is_active():
            return self._promotion_interaction.clear_highlight()

        if self._annotation_interaction.is_active():
            self._annotation_interaction.cancel()
            return ControllerEventResult(requires_render=True)

        if self._piece_interaction.has_active_drag():
            return self._piece_interaction.clear_drag()

        return ControllerEventResult()
