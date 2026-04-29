# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Public view API for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .core.primitives import PlayerColor
from .core.session.board_session import BoardSession
from .core.session.board_session_builder import BoardSessionBuilder
from .layout.primitives import Viewport

if TYPE_CHECKING:
    from .core.domain.game_spec import GameSpec
    from .core.primitives import Piece
    from .core.query.board_query import BoardQuery
    from .core.session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from .core.state.view_state import ViewState
    from .interaction.controller.protocols import ControllerProtocol
    from .render.renderer.protocol import RendererProtocol
    from .theme.theme import Theme


class View:
    """High-level API for loading, querying, and rendering a pychessview."""

    __slots__ = "_session"

    _session: BoardSession

    def __init__(
        self,
        renderer: RendererProtocol,
        game_spec: GameSpec,
        width: int = 1,
        height: int = 1,
        x: int = 0,
        y: int = 0,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
        game_session_class: type[GameSessionProtocol] | None = None,
        interaction_session_class: type[InteractionSessionProtocol] | None = None,
        annotation_session_class: type[AnnotationSessionProtocol] | None = None,
        promotion_session_class: type[PromotionSessionProtocol] | None = None,
    ) -> None:
        """Initialize the view with the subsystems used to query, lay out, and render the board.

        Args:
            renderer: Renderer instance used to turn render items into drawing commands.
            game_spec: Value used to initialize ``game_spec``.
            width: Width value used for sizing.
            height: Height value used for sizing.
            x: Horizontal coordinate or component.
            y: Vertical coordinate or component.
            player: Player color whose perspective controls interaction and board orientation.
            default_fen: Optional FEN string used to initialize the game state.
            white_promotion_pieces: Optional promotion choices available to white.
            black_promotion_pieces: Optional promotion choices available to black.
            game_session_class: Optional game session implementation override.
            interaction_session_class: Optional interaction session implementation override.
            annotation_session_class: Optional annotation session implementation override.
            promotion_session_class: Optional promotion session implementation override.
        """
        components = BoardSessionBuilder.build(
            renderer,
            game_spec,
            Viewport(x, y, width, height),
            player=player,
            default_fen=default_fen,
            white_promotion_pieces=white_promotion_pieces,
            black_promotion_pieces=black_promotion_pieces,
            game_session_class=game_session_class,
            interaction_session_class=interaction_session_class,
            annotation_session_class=annotation_session_class,
            promotion_session_class=promotion_session_class,
        )
        self._session = BoardSession(components)

    def load_game(
        self,
        game_spec: GameSpec,
        *,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
    ) -> None:
        """Load a new game specification into the session and reset state.

        Args:
            game_spec: Game specification to load.
            player: Player color to use.
            default_fen: Default FEN string to use.
            white_promotion_pieces: White promotion pieces to store.
            black_promotion_pieces: Black promotion pieces to store.
        """
        self._session.load_game(
            game_spec,
            player=player,
            default_fen=default_fen,
            white_promotion_pieces=white_promotion_pieces,
            black_promotion_pieces=black_promotion_pieces,
        )

    @property
    def theme(self) -> Theme:
        """Active theme used to render the pychessview.

        Returns:
            Active theme used to render the pychessview.
        """
        return self._session.theme

    @theme.setter
    def theme(self, theme: Theme) -> None:
        """Set the theme currently used to render the board.

        Args:
            theme: Theme instance to use.
        """
        self._session.theme.load(theme)

    @property
    def settings(self) -> ViewState:
        """View state settings for the pychessview.

        Returns:
            View state settings for the pychessview.
        """
        return self._session.view_state

    @property
    def fen(self) -> str:
        """Current board position as a FEN string.

        Returns:
            Current board position as a FEN string.
        """
        return self._session.game_session.fen

    def load_position_from_fen(self, fen: str) -> None:
        """Load a board position from a FEN string.

        Args:
            fen: FEN string describing the position that should become active.
        """
        self._session.game_session.load_fen(fen)

    def reset_board(self, fen: str | None = None) -> None:
        """Reset the board to its initial state.

        Args:
            fen: Optional FEN string to load instead of the configured default position.
        """
        self._session.game_session.reset(fen)

    @property
    def game(self) -> GameSessionProtocol:
        """Game session exposed by the view.

        Returns:
            Game session exposed by the view.
        """
        return self._session.game_session

    @property
    def interaction(self) -> InteractionSessionProtocol:
        """Interaction session exposed by the view.

        Returns:
            Interaction session exposed by the view.
        """
        return self._session.interaction_session

    @property
    def annotation(self) -> AnnotationSessionProtocol:
        """Annotation session exposed by the view.

        Returns:
            Annotation session exposed by the view.
        """
        return self._session.annotation_session

    @property
    def query(self) -> BoardQuery:
        """Board query helper exposed by the view.

        Returns:
            Board query helper exposed by the view.
        """
        return self._session.query

    @property
    def controller_enabled(self) -> bool:
        """Whether the active controller handles input events.

        Returns:
            ``True`` when the active controller handles input events; otherwise, ``False``.
        """
        return self._session.controller_enabled

    @controller_enabled.setter
    def controller_enabled(self, enabled: bool) -> None:
        """Enable or disable board input handling.

        Args:
            enabled: Whether controller-driven board input handling should be enabled.
        """
        self._session.controller_enabled = enabled

    @property
    def controller(self) -> ControllerProtocol:
        """Controller currently handling board input.

        Returns:
            Controller currently handling board input.
        """
        return self._session.controller

    def render_frame(
        self, width: int | None = None, height: int | None = None, x: int | None = None, y: int | None = None
    ) -> None:
        """Render the current board state into the configured renderer.

        Args:
            width: Optional viewport width to use for this frame.
            height: Optional viewport height to use for this frame.
            x: Optional viewport left coordinate to use for this frame.
            y: Optional viewport top coordinate to use for this frame.
        """
        renderer = self._session.renderer
        geometry = self._session.geometry

        # Update geometry
        geometry.update(
            Viewport(
                x if x is not None else geometry.viewport.x,
                y if y is not None else geometry.viewport.y,
                width if width is not None else geometry.viewport.width,
                height if height is not None else geometry.viewport.height,
            )
        )

        # Render
        renderer.begin_frame(geometry.viewport)

        if geometry.is_renderable:
            self._session.board_layer.render()
            self._session.highlight_layer.render()
            self._session.piece_layer.render()
            self._session.annotation_layer.render()
            self._session.promotion_layer.render()

        renderer.end_frame()
