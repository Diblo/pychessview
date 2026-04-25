# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Painter adapter helpers for the pychessview.qt package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter


class PainterAdapter:
    """Store and validate the active QPainter instance."""

    __slots__ = ("_painter",)

    _painter: QPainter | None

    def __init__(self) -> None:
        """Initialize the painter adapter with the Qt painter used for drawing commands."""
        self._painter = None

    def set_painter(self, painter: QPainter) -> None:
        """Store the active ``QPainter`` used for subsequent drawing calls.

        Args:
            painter: QPainter instance to store.
        """
        self._painter = painter

    def require_painter(self) -> QPainter:
        """Return the active ``QPainter`` instance or raise if no painter is set.

        Returns:
            The active painter instance.
        """
        if self._painter is None:
            raise RuntimeError("QtRenderer painter is not set. Call set_painter(painter) before render_frame().")
        return self._painter
