# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Top-level public API for the pychessview package.

This module exposes:

1. Basic usage API (default entry points)
2. Required runtime contracts
3. Extension API for variants, controllers, and behavior customization
"""

from importlib.metadata import PackageNotFoundError, version

from .engine.core.domain.adapters.protocol import GameAdapterProtocol
from .engine.core.domain.game_spec import (
    ControllerFactoryProtocol,
    GameAdapterFactoryProtocol,
    GameDefinition,
    GameFactoryProtocol,
    GameSpec,
    ThemeProviderProtocol,
)
from .engine.core.session.protocols import (
    AnnotationSessionProtocol,
    GameSessionProtocol,
    InteractionSessionProtocol,
    PromotionSessionProtocol,
)
from .engine.factory.standard_chess import StandardChessFactory
from .engine.interaction.controller.protocols import ControllerProtocol
from .engine.render.renderer.protocol import RendererProtocol
from .engine.theme.theme import load_theme
from .engine.theme.theme_name import ThemeName
from .engine.view import View

try:
    __version__ = version("pychessview")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    # Metadata
    "__version__",
    # Basic API
    "View",
    "StandardChessFactory",
    "load_theme",
    "ThemeName",
    # Required contracts
    "RendererProtocol",
    # Game Variant API
    "GameDefinition",
    "GameSpec",
    "GameFactoryProtocol",
    "GameAdapterProtocol",
    "GameAdapterFactoryProtocol",
    "ThemeProviderProtocol",
    # Controller API
    "ControllerProtocol",
    "ControllerFactoryProtocol",
    # Session API
    "GameSessionProtocol",
    "InteractionSessionProtocol",
    "PromotionSessionProtocol",
    "AnnotationSessionProtocol",
]
