# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Top-level public API for the pychessview.qt package."""

from .renderer.qt_renderer import QtRenderer
from .widget.chessboard_widget import ChessboardWidget

__all__ = [
    # Basic API
    "ChessboardWidget",
    # Required contracts
    "QtRenderer",
]
