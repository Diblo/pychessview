# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Qt widget integration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from pychessview import View
from pychessview.engine.core.primitives import PlayerColor

from ..integration.qt_controller_adapter import QtControllerAdapter
from ..renderer.qt_renderer import QtRenderer

if TYPE_CHECKING:
    from typing import Any

    from PySide6.QtGui import QMouseEvent, QPaintEvent

    from pychessview import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        GameSpec,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from pychessview.engine.core.primitives import Piece
    from pychessview.engine.core.query.board_query import BoardQuery
    from pychessview.engine.core.state.view_state import ViewState
    from pychessview.engine.theme.theme import Theme


class ChessboardWidget(QWidget):
    """Qt widget that hosts and renders a pychessview view."""

    __slots__ = "_renderer", "_board_view", "_controller_adapter"

    _renderer: QtRenderer
    _board_view: View
    _controller_adapter: QtControllerAdapter

    def __init__(
        self,
        parent: Any | None = None,
        *,
        game_spec: GameSpec,
        player: PlayerColor = PlayerColor.WHITE,
        default_fen: str | None = None,
        white_promotion_pieces: tuple[Piece, ...] | None = None,
        black_promotion_pieces: tuple[Piece, ...] | None = None,
        game_session_class: type[GameSessionProtocol] | None = None,
        interaction_session_class: type[InteractionSessionProtocol] | None = None,
        annotation_session_class: type[AnnotationSessionProtocol] | None = None,
        promotion_session_class: type[PromotionSessionProtocol] | None = None,
    ) -> None:
        """Initialize the widget with the view, controller, and optional Qt parent object.

        Args:
            parent: Optional parent object used by the surrounding framework.
        """
        super().__init__(parent)
        self.setMouseTracking(True)

        self._renderer = QtRenderer()
        self._board_view = View(
            self._renderer,
            game_spec,
            player=player,
            default_fen=default_fen,
            white_promotion_pieces=white_promotion_pieces,
            black_promotion_pieces=black_promotion_pieces,
            game_session_class=game_session_class,
            interaction_session_class=interaction_session_class,
            annotation_session_class=annotation_session_class,
            promotion_session_class=promotion_session_class,
        )
        self._controller_adapter = QtControllerAdapter(self._board_view)

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
        self._board_view.load_game(
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
        return self._board_view.theme

    @theme.setter
    def theme(self, theme: Theme) -> None:
        """Set the theme currently used to render the board.

        Args:
            theme: Theme instance to use.
        """
        self._board_view.theme = theme

    @property
    def settings(self) -> ViewState:
        """View state settings for the pychessview.

        Returns:
            View state settings for the pychessview.
        """
        return self._board_view.settings

    @property
    def fen(self) -> str:
        """Current board position as a FEN string.

        Returns:
            Current board position as a FEN string.
        """
        return self._board_view.fen

    def load_position_from_fen(self, fen: str) -> None:
        """Load a board position from a FEN string.

        Args:
            fen: FEN string describing the position that should become active.
        """
        self._board_view.load_position_from_fen(fen)

    def reset_board(self, fen: str | None = None) -> None:
        """Reset the board to its initial state.

        Args:
            fen: Optional FEN string to load instead of the configured default position.
        """
        self._board_view.reset_board(fen)

    @property
    def game(self) -> GameSessionProtocol:
        """Game session exposed by the view.

        Returns:
            Game session exposed by the view.
        """
        return self._board_view.game

    @property
    def interaction(self) -> InteractionSessionProtocol:
        """Interaction session exposed by the view.

        Returns:
            Interaction session exposed by the view.
        """
        return self._board_view.interaction

    @property
    def annotation(self) -> AnnotationSessionProtocol:
        """Annotation session exposed by the view.

        Returns:
            Annotation session exposed by the view.
        """
        return self._board_view.annotation

    @property
    def query(self) -> BoardQuery:
        """Board query helper exposed by the view.

        Returns:
            Board query helper exposed by the view.
        """
        return self._board_view.query

    @property
    def controller_enabled(self) -> bool:
        """Whether the active controller handles input events.

        Returns:
            ``True`` when the active controller handles input events; otherwise, ``False``.
        """
        return self._board_view.controller_enabled

    @controller_enabled.setter
    def controller_enabled(self, enabled: bool) -> None:
        """Enable or disable board input handling.

        Args:
            enabled: Whether controller-driven board input handling should be enabled.
        """
        self._board_view.controller_enabled = enabled

    def sizeHint(self) -> QSize:
        """Return the widget's preferred size.

        Returns:
            Preferred size reported to Qt layout code.
        """
        return QSize(512, 512)

    def minimumSizeHint(self) -> QSize:
        """Return the widget's minimum preferred size.

        Returns:
            Minimum preferred size reported to Qt layout code.
        """
        return QSize(30, 30)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a Qt paint event.

        Args:
            event: Qt event to handle.
        """
        _ = event
        painter = QPainter(self)
        try:
            self._renderer.set_painter(painter)
            self._board_view.render_frame(self.width(), self.height())
        finally:
            painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle a Qt mouse press event.

        Args:
            event: Qt event to handle.
        """
        result = self._controller_adapter.handle_press(event)
        if result.requires_render:
            self.update()

        if result.handled:
            self.grabMouse()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle a Qt mouse move event.

        Args:
            event: Qt event to handle.
        """
        result = self._controller_adapter.handle_move(event)
        if result.requires_render:
            self.update()

        if not result.handled:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle a Qt mouse release event.

        Args:
            event: Qt event to handle.
        """
        try:
            result = self._controller_adapter.handle_release(event)
            if result.requires_render:
                self.update()

            if not result.handled:
                super().mouseReleaseEvent(event)
        finally:
            self.releaseMouse()
