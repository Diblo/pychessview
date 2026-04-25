# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board session assembly for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...interaction.controller.null_controller import NullController
from ...layout.layout_engine import LayoutEngine
from ...layout.models.annotation_layout import AnnotationLayout
from ...layout.models.board_layout import BoardLayout
from ...layout.models.highlight_layout import HighlightLayout
from ...layout.models.piece_layout import PieceLayout
from ...layout.models.promotion_layout import PromotionLayout
from ...render.layers.annotation_layer import AnnotationLayer
from ...render.layers.board_layer import BoardLayer
from ...render.layers.highlight_layer import HighlightLayer
from ...render.layers.piece_layer import PieceLayer
from ...render.layers.promotion_layer import PromotionLayer
from ..domain.game_adapter_proxy import GameAdapterProxy
from ..primitives import PlayerColor
from ..query.board_query import BoardQuery
from ..state.annotation_state import AnnotationState
from ..state.highlight_state import HighlightState
from ..state.piece_ui_state import PieceUiState
from ..state.promotion_state import PromotionState
from ..state.view_state import ViewState
from .annotation_session import AnnotationSession
from .game_session import GameSession
from .interaction_session import InteractionSession
from .promotion_session import PromotionSession

if TYPE_CHECKING:
    from ...interaction.controller.protocols import ControllerProtocol
    from ...layout.primitives import Viewport
    from ...render.renderer.protocol import RendererProtocol
    from ...theme.theme import Theme
    from ..domain.game_spec import GameSpec
    from ..primitives import Piece
    from .protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )


class BoardSessionComponents:
    """Stores the runtime objects assembled for a board session."""

    __slots__ = (
        "renderer",
        "theme",
        "view_state",
        "geometry",
        "game_adapter",
        "highlight_state",
        "piece_ui_state",
        "annotation_state",
        "promotion_state",
        "game_session",
        "interaction_session",
        "annotation_session",
        "promotion_session",
        "query",
        "null_controller",
        "game_controller",
        "board_layer",
        "highlight_layer",
        "piece_layer",
        "annotation_layer",
        "promotion_layer",
    )

    def __init__(
        self,
        *,
        renderer: RendererProtocol,
        theme: Theme,
        view_state: ViewState,
        geometry: LayoutEngine,
        game_adapter: GameAdapterProxy,
        highlight_state: HighlightState,
        piece_ui_state: PieceUiState,
        annotation_state: AnnotationState,
        promotion_state: PromotionState,
        game_session: GameSessionProtocol,
        interaction_session: InteractionSessionProtocol,
        annotation_session: AnnotationSessionProtocol,
        promotion_session: PromotionSessionProtocol,
        query: BoardQuery,
        null_controller: ControllerProtocol,
        game_controller: ControllerProtocol,
        board_layer: BoardLayer,
        highlight_layer: HighlightLayer,
        piece_layer: PieceLayer,
        annotation_layer: AnnotationLayer,
        promotion_layer: PromotionLayer,
    ) -> None:
        """Initialize the board session components with its initial configuration.

        Args:
            renderer: Renderer instance to use.
            theme: Theme instance to use.
            view_state: Value supplied for ``view_state``.
            geometry: Value supplied for ``geometry``.
            game_adapter: Value supplied for ``game_adapter``.
            highlight_state: Value supplied for ``highlight_state``.
            piece_ui_state: Value supplied for ``piece_ui_state``.
            annotation_state: Value supplied for ``annotation_state``.
            promotion_state: Value supplied for ``promotion_state``.
            game_session: Value supplied for ``game_session``.
            interaction_session: Value supplied for ``interaction_session``.
            annotation_session: Value supplied for ``annotation_session``.
            promotion_session: Value supplied for ``promotion_session``.
            query: Value supplied for ``query``.
            null_controller: Value supplied for ``null_controller``.
            game_controller: Value supplied for ``game_controller``.
            board_layer: Value supplied for ``board_layer``.
            highlight_layer: Value supplied for ``highlight_layer``.
            piece_layer: Value supplied for ``piece_layer``.
            annotation_layer: Value supplied for ``annotation_layer``.
            promotion_layer: Value supplied for ``promotion_layer``.
        """
        self.renderer = renderer
        self.theme = theme
        self.view_state = view_state
        self.geometry = geometry
        self.game_adapter = game_adapter
        self.highlight_state = highlight_state
        self.piece_ui_state = piece_ui_state
        self.annotation_state = annotation_state
        self.promotion_state = promotion_state
        self.game_session = game_session
        self.interaction_session = interaction_session
        self.annotation_session = annotation_session
        self.promotion_session = promotion_session
        self.query = query
        self.null_controller = null_controller
        self.game_controller = game_controller
        self.board_layer = board_layer
        self.highlight_layer = highlight_layer
        self.piece_layer = piece_layer
        self.annotation_layer = annotation_layer
        self.promotion_layer = promotion_layer


class BoardSessionBuilder:
    """Build the runtime objects needed for a board session."""

    __slots__ = ()

    @staticmethod
    def build(
        renderer: RendererProtocol,
        game_spec: GameSpec,
        viewport: Viewport,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
        game_session_class: type[GameSessionProtocol] | None = None,
        interaction_session_class: type[InteractionSessionProtocol] | None = None,
        annotation_session_class: type[AnnotationSessionProtocol] | None = None,
        promotion_session_class: type[PromotionSessionProtocol] | None = None,
    ) -> BoardSessionComponents:
        """Create a complete board session from the configured dependencies.

        Args:
            renderer: Renderer instance to use.
            game_spec: Game specification to load.
            viewport: Viewport to render.
            player: Player color to use.
            default_fen: Default FEN string to use.
            white_promotion_pieces: White promotion pieces to store.
            black_promotion_pieces: Black promotion pieces to store.
            game_session_class: Custom game session implementation to instantiate instead of ``GameSession``.
            interaction_session_class: Custom interaction session implementation to instantiate instead of
                ``InteractionSession``.
            annotation_session_class: Custom annotation session implementation to instantiate instead of
                ``AnnotationSession``.
            promotion_session_class: Custom promotion session implementation to instantiate instead of
                ``PromotionSession``.

        Returns:
            A complete board session from the configured dependencies.
        """
        theme = game_spec.theme_provider.create_theme()
        view_state = ViewState(player)
        geometry = LayoutEngine(view_state, theme, viewport)
        game_adapter = GameAdapterProxy(game_spec.adapter_factory.create_game_adapter(default_fen))

        highlight_state = HighlightState()
        piece_ui_state = PieceUiState(game_adapter)
        annotation_state = AnnotationState()
        promotion_state = PromotionState(
            white_promotion_pieces or game_spec.definition.white_promotion_pieces,
            black_promotion_pieces or game_spec.definition.black_promotion_pieces,
        )
        query = BoardQuery(view_state, promotion_state, geometry)

        game_session_class = game_session_class or GameSession
        interaction_session_class = interaction_session_class or InteractionSession
        annotation_session_class = annotation_session_class or AnnotationSession
        promotion_session_class = promotion_session_class or PromotionSession

        game_session = game_session_class.create(
            game_adapter, highlight_state, piece_ui_state, annotation_state, promotion_state
        )
        interaction_session = interaction_session_class.create(
            view_state, game_adapter, highlight_state, piece_ui_state, promotion_state, annotation_state
        )
        annotation_session = annotation_session_class.create(annotation_state, promotion_state)
        promotion_session = promotion_session_class.create(
            game_adapter, query, highlight_state, piece_ui_state, annotation_state, promotion_state
        )

        board_layer = BoardLayer(view_state, None, renderer, BoardLayout(theme, view_state, geometry))
        highlight_layer = HighlightLayer(
            view_state, highlight_state, renderer, HighlightLayout(theme, view_state, geometry)
        )
        piece_layer = PieceLayer(view_state, piece_ui_state, renderer, PieceLayout(theme, view_state, geometry))
        annotation_layer = AnnotationLayer(
            view_state, annotation_state, renderer, AnnotationLayout(theme, view_state, geometry)
        )
        promotion_layer = PromotionLayer(
            view_state, promotion_state, renderer, PromotionLayout(theme, view_state, geometry)
        )

        null_controller = NullController.create(
            view_state=view_state,
            game=game_session,
            interaction=interaction_session,
            annotation=annotation_session,
            promotion=promotion_session,
            query=query,
        )
        game_controller = game_spec.controller_factory.create_controller(
            view_state, game_session, interaction_session, annotation_session, promotion_session, query
        )

        return BoardSessionComponents(
            renderer=renderer,
            theme=theme,
            view_state=view_state,
            geometry=geometry,
            game_adapter=game_adapter,
            highlight_state=highlight_state,
            piece_ui_state=piece_ui_state,
            annotation_state=annotation_state,
            promotion_state=promotion_state,
            game_session=game_session,
            interaction_session=interaction_session,
            annotation_session=annotation_session,
            promotion_session=promotion_session,
            query=query,
            null_controller=null_controller,
            game_controller=game_controller,
            board_layer=board_layer,
            highlight_layer=highlight_layer,
            piece_layer=piece_layer,
            annotation_layer=annotation_layer,
            promotion_layer=promotion_layer,
        )
