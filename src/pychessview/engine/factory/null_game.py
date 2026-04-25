# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Null game factory definitions for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.domain.adapters.null_game_adapter import NullGameAdapter
from ..core.domain.game_spec import (
    ControllerFactoryProtocol,
    GameAdapterFactoryProtocol,
    GameDefinition,
    GameFactoryProtocol,
    GameSpec,
    ThemeProviderProtocol,
)
from ..interaction.controller.null_controller import NullController
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


class NullThemeProvider(ThemeProviderProtocol):
    """Theme provider for the null game configuration."""

    def create_theme(self) -> Theme:
        """Create the theme object configured by the specification.

        Returns:
            The theme instance configured by the specification.
        """
        return load_theme(ThemeName.DEFAULT)


class NullGameAdapterFactory(GameAdapterFactoryProtocol):
    """Factory that creates null game adapters."""

    __slots__ = "_default_fen"

    _default_fen: str

    def __init__(self, default_fen: str) -> None:
        """Initialize the factory with the default FEN used when creating null game adapters.

        Args:
            default_fen: Default FEN string used to initialize or reset the game state.
        """
        self._default_fen = default_fen

    @classmethod
    def create(cls, default_fen: str) -> NullGameAdapterFactory:
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
        return NullGameAdapter(default_fen or self._default_fen)


class NullControllerFactory(ControllerFactoryProtocol):
    """Factory that creates null controllers."""

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
        return NullController.create(
            view_state=view_state,
            game=game,
            interaction=interaction,
            annotation=annotation,
            promotion=promotion,
            query=query,
        )


class NullGameFactory(GameFactoryProtocol):
    """Factory that creates the null game specification."""

    @staticmethod
    def create_game_spec(default_fen: str | None = None) -> GameSpec:
        """Create a game specification for the requested game mode.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A game specification describing how the board should be initialized.
        """
        default_fen = default_fen or ""

        return GameSpec(
            definition=GameDefinition(default_fen, white_promotion_pieces=(), black_promotion_pieces=()),
            theme_provider=NullThemeProvider(),
            adapter_factory=NullGameAdapterFactory.create(default_fen),
            controller_factory=NullControllerFactory(),
        )
