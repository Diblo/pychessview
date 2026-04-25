# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Game specification contracts and value objects for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Final

    from ...interaction.controller.protocols import ControllerProtocol
    from ...theme.theme import Theme
    from ..primitives import Piece
    from ..query.board_query import BoardQuery
    from ..session.protocols import (
        AnnotationSessionProtocol,
        GameSessionProtocol,
        InteractionSessionProtocol,
        PromotionSessionProtocol,
    )
    from ..state.view_state import ViewState
    from .adapters.protocol import GameAdapterProtocol


class ThemeProviderProtocol(Protocol):
    """Protocol for objects that create themes."""

    def create_theme(self) -> Theme:
        """Create the theme object configured by the specification.

        Returns:
            The theme instance configured by the specification.
        """
        ...


class GameAdapterFactoryProtocol(Protocol):
    """Protocol for factories that create game adapters."""

    @classmethod
    def create(cls, default_fen: str) -> GameAdapterFactoryProtocol:
        """Create an instance from the provided collaborators.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A newly created instance of ``cls``.
        """
        ...

    def create_game_adapter(self, default_fen: str | None = None) -> GameAdapterProtocol:
        """Create the game adapter used for board state operations.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A game adapter instance ready to manage board state.
        """
        ...


class ControllerFactoryProtocol(Protocol):
    """Protocol for factories that create controllers."""

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
        ...


class GameFactoryProtocol(Protocol):
    """Protocol for factories that create game specifications."""

    @staticmethod
    def create_game_spec(default_fen: str | None = None) -> GameSpec:
        """Create a game specification for the requested game mode.

        Args:
            default_fen: Default FEN string to use.

        Returns:
            A game specification describing how the board should be initialized.
        """
        ...


class GameDefinition:
    """Defines the default FEN and promotion options for a game.

    Attributes:
        default_fen: Default FEN string for the game definition or adapter.
        white_promotion_pieces: Promotion pieces available to white.
        black_promotion_pieces: Promotion pieces available to black.
    """

    __slots__ = "default_fen", "white_promotion_pieces", "black_promotion_pieces"

    default_fen: Final[str]
    white_promotion_pieces: Final[tuple[Piece, ...]]
    black_promotion_pieces: Final[tuple[Piece, ...]]

    def __init__(
        self, default_fen: str, white_promotion_pieces: tuple[Piece, ...], black_promotion_pieces: tuple[Piece, ...]
    ) -> None:
        """Initialize the game definition with its initial configuration.

        Args:
            default_fen: Default FEN string used to initialize or reset the game state.
            white_promotion_pieces: Value used to initialize ``white_promotion_pieces``.
            black_promotion_pieces: Value used to initialize ``black_promotion_pieces``.
        """
        self.default_fen = default_fen
        self.white_promotion_pieces = white_promotion_pieces
        self.black_promotion_pieces = black_promotion_pieces

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, GameDefinition):
            return NotImplemented

        return (
            self.default_fen == other.default_fen
            and self.white_promotion_pieces == other.white_promotion_pieces
            and self.black_promotion_pieces == other.black_promotion_pieces
        )

    def __hash__(self) -> int:
        """Return a hash value for the instance.

        Returns:
            Hash value for the instance.
        """
        return hash((self.default_fen, self.white_promotion_pieces, self.black_promotion_pieces))

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return (
            "GameDefinition("
            f"default_fen={self.default_fen!r}, "
            f"white_promotion_pieces={self.white_promotion_pieces!r}, "
            f"black_promotion_pieces={self.black_promotion_pieces!r})"
        )


class GameSpec:
    """Bundles the factories and defaults needed to load a game.

    Attributes:
        definition: Game definition containing the default position and promotion options.
        theme_provider: Theme provider used when loading the game.
        adapter_factory: Factory that creates the active game adapter.
        controller_factory: Factory that creates the active controller.
    """

    __slots__ = "definition", "theme_provider", "adapter_factory", "controller_factory"

    definition: Final[GameDefinition]
    theme_provider: Final[ThemeProviderProtocol]
    adapter_factory: Final[GameAdapterFactoryProtocol]
    controller_factory: Final[ControllerFactoryProtocol]

    def __init__(
        self,
        definition: GameDefinition,
        theme_provider: ThemeProviderProtocol,
        adapter_factory: GameAdapterFactoryProtocol,
        controller_factory: ControllerFactoryProtocol,
    ) -> None:
        """Initialize the game spec with its initial configuration.

        Args:
            definition: Value used to initialize ``definition``.
            theme_provider: Value used to initialize ``theme_provider``.
            adapter_factory: Value used to initialize ``adapter_factory``.
            controller_factory: Value used to initialize ``controller_factory``.
        """
        self.definition = definition
        self.theme_provider = theme_provider
        self.adapter_factory = adapter_factory
        self.controller_factory = controller_factory

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if not isinstance(other, GameSpec):
            return NotImplemented

        return (
            self.definition == other.definition
            and self.theme_provider == other.theme_provider
            and self.adapter_factory == other.adapter_factory
            and self.controller_factory == other.controller_factory
        )

    def __hash__(self) -> int:
        """Return a hash value for the instance.

        Returns:
            Hash value for the instance.
        """
        return hash((self.definition, self.theme_provider, self.adapter_factory, self.controller_factory))

    def __repr__(self) -> str:
        """Return a developer-oriented representation of the instance.

        Returns:
            Developer-oriented representation of the instance.
        """
        return (
            "GameSpec("
            f"definition={self.definition!r}, "
            f"theme_provider={self.theme_provider!r}, "
            f"adapter_factory={self.adapter_factory!r}, "
            f"controller_factory={self.controller_factory!r})"
        )
