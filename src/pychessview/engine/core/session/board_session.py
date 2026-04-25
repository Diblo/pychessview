# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board session orchestration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...interaction.controller_proxy import ControllerProxy
from ..primitives import PlayerColor

if TYPE_CHECKING:
    from ...interaction.controller.protocols import ControllerProtocol
    from ...layout.layout_engine import LayoutEngine
    from ...render.layers.annotation_layer import AnnotationLayer
    from ...render.layers.board_layer import BoardLayer
    from ...render.layers.highlight_layer import HighlightLayer
    from ...render.layers.piece_layer import PieceLayer
    from ...render.layers.promotion_layer import PromotionLayer
    from ...render.renderer.protocol import RendererProtocol
    from ...theme.theme import Theme
    from ..domain.game_spec import GameSpec
    from ..primitives import Piece
    from ..query.board_query import BoardQuery
    from ..state.view_state import ViewState
    from .board_session_builder import BoardSessionComponents
    from .protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )


class BoardSession:
    """Coordinates the assembled pychessview runtime."""

    __slots__ = ("_components", "_controller_enabled", "_controller")

    _components: BoardSessionComponents
    _controller_enabled: bool
    _controller: ControllerProxy

    def __init__(self, components: BoardSessionComponents) -> None:
        """Initialize the board session with its initial configuration.

        Args:
            components: Value used to initialize ``components``.
        """
        self._components = components
        self._controller_enabled = True
        self._controller = ControllerProxy.create(
            view_state=components.view_state,
            game=components.game_session,
            interaction=components.interaction_session,
            annotation=components.annotation_session,
            promotion=components.promotion_session,
            query=components.query,
        )
        self._controller.switch_controller(components.game_controller)

    @property
    def renderer(self) -> RendererProtocol:
        """Renderer used by the board session.

        Returns:
            Renderer used by the board session.
        """
        return self._components.renderer

    @property
    def theme(self) -> Theme:
        """Active theme used to render the pychessview.

        Returns:
            Active theme used to render the pychessview.
        """
        return self._components.theme

    @property
    def view_state(self) -> ViewState:
        """View state used by the board session.

        Returns:
            View state used by the board session.
        """
        return self._components.view_state

    @property
    def geometry(self) -> LayoutEngine:
        """Layout engine used by the board session.

        Returns:
            Layout engine used by the board session.
        """
        return self._components.geometry

    @property
    def game_session(self) -> GameSessionProtocol:
        """Game session used by the board session.

        Returns:
            Game session used by the board session.
        """
        return self._components.game_session

    @property
    def interaction_session(self) -> InteractionSessionProtocol:
        """Interaction session used by the board session.

        Returns:
            Interaction session used by the board session.
        """
        return self._components.interaction_session

    @property
    def annotation_session(self) -> AnnotationSessionProtocol:
        """Annotation session used by the board session.

        Returns:
            Annotation session used by the board session.
        """
        return self._components.annotation_session

    @property
    def promotion_session(self) -> PromotionSessionProtocol:
        """Promotion session used by the board session.

        Returns:
            Promotion session used by the board session.
        """
        return self._components.promotion_session

    @property
    def query(self) -> BoardQuery:
        """Board query helper exposed by the view.

        Returns:
            Board query helper exposed by the view.
        """
        return self._components.query

    @property
    def controller_enabled(self) -> bool:
        """Whether the active controller handles input events.

        Returns:
            ``True`` when the active controller handles input events; otherwise, ``False``.
        """
        return self._controller_enabled

    @controller_enabled.setter
    def controller_enabled(self, enabled: bool) -> None:
        """Enable or disable board input handling.

        Args:
            enabled: Whether controller-driven board input handling should be enabled.
        """
        self._controller_enabled = enabled
        self._sync_controller()

    @property
    def controller(self) -> ControllerProtocol:
        """Controller currently handling board input.

        Returns:
            Controller currently handling board input.
        """
        return self._controller

    @property
    def board_layer(self) -> BoardLayer:
        """Rendering layer for the board background and labels.

        Returns:
            Rendering layer for the board background and labels.
        """
        return self._components.board_layer

    @property
    def highlight_layer(self) -> HighlightLayer:
        """Rendering layer for highlights.

        Returns:
            Rendering layer for highlights.
        """
        return self._components.highlight_layer

    @property
    def piece_layer(self) -> PieceLayer:
        """Rendering layer for pieces.

        Returns:
            Rendering layer for pieces.
        """
        return self._components.piece_layer

    @property
    def annotation_layer(self) -> AnnotationLayer:
        """Rendering layer for annotations.

        Returns:
            Rendering layer for annotations.
        """
        return self._components.annotation_layer

    @property
    def promotion_layer(self) -> PromotionLayer:
        """Rendering layer for promotion choices.

        Returns:
            Rendering layer for promotion choices.
        """
        return self._components.promotion_layer

    def load_game(
        self,
        game_spec: GameSpec,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
    ) -> None:
        """Load a new game specification into the session and rebuild dependent state.

        Args:
            game_spec: Game specification to load.
            player: Player color to use.
            default_fen: Default FEN string to use.
            white_promotion_pieces: White promotion pieces to store.
            black_promotion_pieces: Black promotion pieces to store.
        """
        self._reset_runtime_state()
        self._apply_game_settings(
            game_spec=game_spec,
            player=player,
            white_promotion_pieces=white_promotion_pieces,
            black_promotion_pieces=black_promotion_pieces,
        )
        self._replace_game_adapter(game_spec, default_fen)
        self._replace_game_controller(game_spec)
        self._sync_controller()
        self._update_highlight()

    def _reset_runtime_state(self) -> None:
        """Reset transient runtime state before loading a game."""
        self._components.highlight_state.clear_all()
        self._components.piece_ui_state.clear_all()
        self._components.annotation_state.clear_all()
        self._components.promotion_state.clear_all()

    def _apply_game_settings(
        self,
        *,
        game_spec: GameSpec,
        player: PlayerColor,
        white_promotion_pieces: tuple[Piece, ...] | None,
        black_promotion_pieces: tuple[Piece, ...] | None,
    ) -> None:
        """Apply game-specific state to the current board.

        Args:
            game_spec: Game specification involved in the operation.
            player: Player color to use.
            white_promotion_pieces: Promotion pieces that white may choose from.
            black_promotion_pieces: Promotion pieces that black may choose from.
        """
        self._components.view_state.player = player
        self._components.theme.load(game_spec.theme_provider.create_theme())
        self._components.promotion_session.set_white_promotion_pieces(
            white_promotion_pieces or game_spec.definition.white_promotion_pieces
        )
        self._components.promotion_session.set_black_promotion_pieces(
            black_promotion_pieces or game_spec.definition.black_promotion_pieces
        )

    def _replace_game_adapter(self, game_spec: GameSpec, default_fen: str | None = None) -> None:
        """Replace the active game adapter.

        Args:
            game_spec: Game specification involved in the operation.
            default_fen: Fallback FEN string to use when no explicit position is provided.
        """
        self._components.game_adapter.switch_adapter(game_spec.adapter_factory.create_game_adapter(default_fen))

    def _replace_game_controller(self, game_spec: GameSpec) -> None:
        """Replace the active game controller.

        Args:
            game_spec: Game specification involved in the operation.
        """
        self._components.game_controller = game_spec.controller_factory.create_controller(
            self._components.view_state,
            self._components.game_session,
            self._components.interaction_session,
            self._components.annotation_session,
            self._components.promotion_session,
            self._components.query,
        )

    def _sync_controller(self) -> None:
        """Synchronize the controller proxy with the enabled state."""
        if self._controller_enabled:
            self._controller.switch_controller(self._components.game_controller)
            return
        self._controller.switch_controller(self._components.null_controller)

    def _update_highlight(self) -> None:
        """Refresh highlight state from the active game."""
        if self._components.game_adapter.has_move_history():
            self._components.highlight_state.set_last_move(self._components.game_adapter.move_history[-1])

        if not (self._components.game_adapter.is_check() or self._components.game_adapter.is_checkmate()):
            self._components.highlight_state.clear_check()
            return

        king_square = self._components.game_adapter.king(self._components.game_adapter.turn)
        if king_square is not None:
            self._components.highlight_state.set_check(king_square)
