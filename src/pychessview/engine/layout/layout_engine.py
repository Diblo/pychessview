# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board layout geometry calculations for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.state.view_state import ViewState
    from ..theme.theme import Theme
    from .primitives import Viewport


def _round_half_up(value: float) -> int:
    """Round a floating-point value using half-up semantics.

    Args:
        value: Value to validate or inspect.

    Returns:
        A floating-point value using half-up semantics.
    """
    return int(value + 0.5)


def _distributed_sizes(total_px: int, n_parts: int) -> tuple[int, ...]:
    """Split a pixel total into near-even segment sizes.

    Args:
        total_px: Integer value supplied for ``total_px``.
        n_parts: Integer value supplied for ``n_parts``.

    Returns:
        Split a pixel total into near-even segment sizes.
    """
    edges = [_round_half_up(i * total_px / n_parts) for i in range(n_parts + 1)]
    return tuple(edges[i + 1] - edges[i] for i in range(n_parts))


def _calc_edges(origin: int, sizes: tuple[int, ...]) -> tuple[int, ...]:
    """Build cumulative edge coordinates from segment sizes.

    Args:
        origin: Integer value supplied for ``origin``.
        sizes: Value supplied for ``sizes``.

    Returns:
        Cumulative edge coordinates from segment sizes.
    """
    edges = [origin]
    for size in sizes:
        edges.append(edges[-1] + size)
    return tuple(edges)


class LayoutEngine:
    """Computes board and overlay geometry for the current view.

    Attributes:
        border_width: Computed border width in pixels.
        file_sizes: Computed widths for each file in pixels.
        rank_sizes: Computed heights for each rank in pixels.
        vertical_edges: Computed x-axis edges for the board grid.
        horizontal_edges: Computed y-axis edges for the board grid.
    """

    __slots__ = (
        "_viewport",
        "_view_state",
        "_theme",
        "_key",
        "_is_renderable",
        "border_width",
        "file_sizes",
        "rank_sizes",
        "vertical_edges",
        "horizontal_edges",
    )

    _viewport: Viewport
    _view_state: ViewState
    _theme: Theme
    _key: tuple[object, ...]
    _is_renderable: bool

    border_width: int
    file_sizes: tuple[int, ...]
    rank_sizes: tuple[int, ...]
    vertical_edges: tuple[int, ...]
    horizontal_edges: tuple[int, ...]

    def __init__(self, view_state: ViewState, theme: Theme, viewport: Viewport) -> None:
        """Initialize the layout engine with the state and theme inputs required to compute render layouts.

        Args:
            view_state: View state used to control the rendered board presentation.
            theme: Theme object that provides colors, images, and other visual settings.
            viewport: Viewport describing the available drawing area.
        """
        self._view_state = view_state
        self._theme = theme
        self._key = ()
        self._is_renderable = False

        self.update(viewport)

    def update(self, viewport: Viewport) -> None:
        """Update cached state to reflect the current inputs.

        Args:
            viewport: Viewport to render.
        """
        self._viewport = viewport

        if viewport.width <= 0 or viewport.height <= 0:
            self._key = ()
            self._is_renderable = False
            return

        view_state = self._view_state
        border_factor = self._theme.border_factor

        key = (
            viewport.x,
            viewport.y,
            viewport.width,
            viewport.height,
            view_state.show_border,
            view_state.stretch_to_fit,
            border_factor,
        )
        if key == self._key:
            return

        size = min(viewport.width, viewport.height)

        if view_state.show_border:
            border_width = max(1, int(size * border_factor))
        else:
            border_width = 0
        double_border_width = 2 * border_width

        if view_state.stretch_to_fit:
            x = viewport.x
            y = viewport.y
            board_width = viewport.width
            board_height = viewport.height
        else:
            x = viewport.x + (viewport.width - size) // 2
            y = viewport.y + (viewport.height - size) // 2
            board_width = size
            board_height = size

        inner_width = board_width - double_border_width
        inner_height = board_height - double_border_width
        if inner_width < 16 or inner_height < 16:
            self._key = ()
            self._is_renderable = False
            return

        file_sizes = _distributed_sizes(board_width - double_border_width, 8)
        rank_sizes = _distributed_sizes(board_height - double_border_width, 8)

        self._is_renderable = True
        self.border_width = border_width
        self.file_sizes = file_sizes
        self.rank_sizes = rank_sizes
        self.vertical_edges = (x, *_calc_edges(x + border_width, file_sizes), x + board_width)
        self.horizontal_edges = (y, *_calc_edges(y + border_width, rank_sizes), y + board_height)

        self._key = key

    @property
    def key(self) -> tuple[object, ...]:
        """Cache key representing the current layout inputs.

        Returns:
            Cache key representing the current layout inputs.
        """
        return self._key

    @property
    def viewport(self) -> Viewport:
        """Current render viewport.

        Returns:
            Current render viewport.
        """
        return self._viewport

    @property
    def is_renderable(self) -> bool:
        """Whether the current viewport is large enough to render.

        Returns:
            ``True`` when the current viewport is large enough to render; otherwise, ``False``.
        """
        return self._is_renderable
