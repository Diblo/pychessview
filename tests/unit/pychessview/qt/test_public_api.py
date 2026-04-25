# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the pychessview.qt package facade."""

import pytest

import pychessview.qt as qt_api
from pychessview.qt.renderer.qt_renderer import QtRenderer
from pychessview.qt.widget.chessboard_widget import ChessboardWidget

pytestmark = [pytest.mark.unit, pytest.mark.requires_qt]


def test_top_level_package_exports_current_public_api() -> None:
    """Expose the documented package-root symbols as stable implementation aliases.

    Application code imports the Qt widget, renderer, and core convenience
    factories from ``pychessview.qt``. The facade must continue resolving to the
    concrete implementation objects users depend on.
    """
    assert qt_api.ChessboardWidget is ChessboardWidget
    assert qt_api.QtRenderer is QtRenderer


def test_top_level_all_matches_exported_public_api() -> None:
    """Keep ``__all__`` limited to the supported package facade.

    Star imports should expose the same public surface as the documented
    top-level package API and should not leak implementation-only names.
    """
    assert set(qt_api.__all__) == {"ChessboardWidget", "QtRenderer"}
