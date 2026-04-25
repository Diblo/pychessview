# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Base layout model for the pychessview package."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...core.primitives import SQUARES, Rank
from ..primitives import Rect

if TYPE_CHECKING:
    from ...core.state.view_state import ViewState
    from ...theme.theme import Theme
    from ..layout_engine import LayoutEngine

CacheKey = tuple[object, ...]
"""Type alias for layout cache keys."""


class Layout(ABC):
    """Base class for computed layout data.

    Attributes:
        theme: Theme used to build layout or render output.
        view_state: View state used to build layout or render output.
        geometry: Layout engine used to compute geometry.
        square_rects: Per-square rectangles indexed by board square.
    """

    __slots__ = "_cache_key", "_geometry_key", "theme", "view_state", "geometry", "square_rects"

    _cache_key: CacheKey
    _geometry_key: tuple[object, ...]

    theme: Theme
    view_state: ViewState
    geometry: LayoutEngine
    square_rects: tuple[Rect, ...]

    def __init__(self, theme: Theme, view_state: ViewState, geometry: LayoutEngine) -> None:
        """Initialize the layout with its initial configuration.

        Args:
            theme: Theme object that provides colors, images, and other visual settings.
            view_state: View state used to control the rendered board presentation.
            geometry: Value used to initialize ``geometry``.
        """
        self._cache_key = ()
        self._geometry_key = ()
        self.theme = theme
        self.view_state = view_state
        self.geometry = geometry

        self._initialization()

    @abstractmethod
    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        ...

    @abstractmethod
    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        ...

    @abstractmethod
    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs."""
        ...

    def update(self) -> None:
        """Update cached state to reflect the current inputs."""
        key = self._build_key()
        if key != self._cache_key or self.geometry.key != self._geometry_key:
            self._create_square_rects()
            self._rebuild()

            self._cache_key = key
            self._geometry_key = self.geometry.key

    def _create_square_rects(self) -> None:
        """Create square rectangles for the current geometry."""
        vertical_edges = self.geometry.vertical_edges
        horizontal_edges = self.geometry.horizontal_edges
        file_sizes = self.geometry.file_sizes
        rank_sizes = self.geometry.rank_sizes

        self.square_rects = tuple(
            Rect(
                vertical_edges[square.file + 1],
                horizontal_edges[Rank.EIGHT - square.rank + 1],
                file_sizes[square.file],
                rank_sizes[Rank.EIGHT - square.rank],
            )
            for square in SQUARES
        )
