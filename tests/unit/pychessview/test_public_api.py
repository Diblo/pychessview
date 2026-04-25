# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the pychessview package facade."""

import pytest

import pychessview as pychessview_api
from pychessview.engine.core.domain.adapters.protocol import GameAdapterProtocol
from pychessview.engine.core.domain.game_spec import (
    ControllerFactoryProtocol,
    GameAdapterFactoryProtocol,
    GameDefinition,
    GameFactoryProtocol,
    GameSpec,
    ThemeProviderProtocol,
)
from pychessview.engine.core.session.protocols import (
    AnnotationSessionProtocol,
    GameSessionProtocol,
    InteractionSessionProtocol,
    PromotionSessionProtocol,
)
from pychessview.engine.factory.standard_chess import StandardChessFactory
from pychessview.engine.interaction.controller.protocols import ControllerProtocol
from pychessview.engine.render.renderer.protocol import RendererProtocol
from pychessview.engine.theme.theme import load_theme
from pychessview.engine.theme.theme_name import ThemeName
from pychessview.engine.view import View

pytestmark = [pytest.mark.unit]


def test_top_level_package_exports_current_public_api() -> None:
    """Expose the documented package-root symbols as stable implementation aliases.

    Application code imports core construction helpers, protocols, and the view
    from ``pychessview``. The facade must continue resolving to the concrete
    implementation objects users depend on.
    """
    assert pychessview_api.View is View
    assert pychessview_api.StandardChessFactory is StandardChessFactory
    assert pychessview_api.load_theme is load_theme
    assert pychessview_api.ThemeName is ThemeName
    assert pychessview_api.RendererProtocol is RendererProtocol
    assert pychessview_api.GameDefinition is GameDefinition
    assert pychessview_api.GameSpec is GameSpec
    assert pychessview_api.GameFactoryProtocol is GameFactoryProtocol
    assert pychessview_api.GameAdapterProtocol is GameAdapterProtocol
    assert pychessview_api.GameAdapterFactoryProtocol is GameAdapterFactoryProtocol
    assert pychessview_api.ThemeProviderProtocol is ThemeProviderProtocol
    assert pychessview_api.ControllerProtocol is ControllerProtocol
    assert pychessview_api.ControllerFactoryProtocol is ControllerFactoryProtocol
    assert pychessview_api.GameSessionProtocol is GameSessionProtocol
    assert pychessview_api.InteractionSessionProtocol is InteractionSessionProtocol
    assert pychessview_api.PromotionSessionProtocol is PromotionSessionProtocol
    assert pychessview_api.AnnotationSessionProtocol is AnnotationSessionProtocol


def test_top_level_all_matches_exported_public_api() -> None:
    """Keep ``__all__`` limited to the supported package facade.

    Star imports should expose the same public surface as the documented
    top-level package API and should not leak implementation-only names.
    """
    assert set(pychessview_api.__all__) == {
        "View",
        "StandardChessFactory",
        "load_theme",
        "ThemeName",
        "RendererProtocol",
        "GameDefinition",
        "GameSpec",
        "GameFactoryProtocol",
        "GameAdapterProtocol",
        "GameAdapterFactoryProtocol",
        "ThemeProviderProtocol",
        "ControllerProtocol",
        "ControllerFactoryProtocol",
        "GameSessionProtocol",
        "InteractionSessionProtocol",
        "PromotionSessionProtocol",
        "AnnotationSessionProtocol",
    }
