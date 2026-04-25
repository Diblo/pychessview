# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Standard chess factory definitions for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.domain.adapters.python_chess_adapter import PythonChessGameAdapter
from ..core.domain.game_spec import (
    ControllerFactoryProtocol,
    GameAdapterFactoryProtocol,
    GameDefinition,
    GameFactoryProtocol,
    GameSpec,
    ThemeProviderProtocol,
)
from ..core.primitives import Piece, PieceKind, PlayerColor
from ..interaction.controller.standard_chess_controller import StandardChessController
from ..theme.theme import ThemeName, load_theme

if TYPE_CHECKING:
    from ..core.domain.adapters.protocol import GameAdapterProtocol
    from ..core.query.board_query import BoardQuery
    from ..core.session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from ..core.state.view_state import ViewState
    from ..interaction.controller.protocols import ControllerProtocol
    from ..theme.theme import Theme


class StandardChessThemeProvider(ThemeProviderProtocol):
    """Theme provider for the standard chess configuration."""

    def create_theme(self) -> Theme:
        """Create the theme object configured by the specification.

        Returns:
            The theme instance configured by the specification.
        """
        return load_theme(ThemeName.STANDARD_CHESS)


class StandardChessAdapterFactory(GameAdapterFactoryProtocol):
    """Factory that creates standard chess adapters."""

    __slots__ = "_default_fen"

    _default_fen: str

    def __init__(self, default_fen: str) -> None:
        """Initialize the factory with the default FEN and optional backend board used for created adapters.

        Args:
            default_fen: Default FEN string used to initialize or reset the game state.
        """
        self._default_fen = default_fen

    @classmethod
    def create(cls, default_fen: str) -> StandardChessAdapterFactory:
        """Create an instance from the provided collaborators.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A newly created instance of ``cls``.
        """
        return cls(default_fen)

    def create_game_adapter(self, default_fen: str | None = None) -> GameAdapterProtocol:
        """Create the game adapter used for board state operations.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A game adapter instance ready to manage board state.
        """
        return PythonChessGameAdapter(default_fen or self._default_fen)


class StandardChessControllerFactory(ControllerFactoryProtocol):
    """Factory that creates standard chess controllers."""

    def create_controller(
        self,
        view_state: ViewState,
        game: GameSessionProtocol,
        interaction: InteractionSessionProtocol,
        annotation: AnnotationSessionProtocol,
        promotion: PromotionSessionProtocol,
        query: BoardQuery,
    ) -> ControllerProtocol:
        """Create the controller used for input handling.

        Args:
            view_state: View state to use.
            game: Game session that exposes board-state operations.
            interaction: Interaction session that manages selection and drag state.
            annotation: Annotation session that manages circles and arrows.
            promotion: Promotion session that manages promotion choice flow.
            query: Board query helper to use.

        Returns:
            A controller instance configured for the current board session.
        """
        return StandardChessController.create(
            view_state=view_state,
            game=game,
            interaction=interaction,
            annotation=annotation,
            promotion=promotion,
            query=query,
        )


class StandardChessFactory(GameFactoryProtocol):
    """Factory that creates the standard chess game specification."""

    @staticmethod
    def create_game_spec(default_fen: str | None = None) -> GameSpec:
        """Create a game specification for the requested game mode.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A game specification describing how the board should be initialized.
        """
        default_fen = default_fen or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        return GameSpec(
            definition=GameDefinition(
                default_fen,
                (
                    Piece(PlayerColor.WHITE, PieceKind.QUEEN),
                    Piece(PlayerColor.WHITE, PieceKind.ROOK),
                    Piece(PlayerColor.WHITE, PieceKind.BISHOP),
                    Piece(PlayerColor.WHITE, PieceKind.KNIGHT),
                ),
                (
                    Piece(PlayerColor.BLACK, PieceKind.QUEEN),
                    Piece(PlayerColor.BLACK, PieceKind.ROOK),
                    Piece(PlayerColor.BLACK, PieceKind.BISHOP),
                    Piece(PlayerColor.BLACK, PieceKind.KNIGHT),
                ),
            ),
            theme_provider=StandardChessThemeProvider(),
            adapter_factory=StandardChessAdapterFactory.create(default_fen),
            controller_factory=StandardChessControllerFactory(),
        )
