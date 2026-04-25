# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Highlight layout model for the pychessview package."""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING

from ...core.highlight_types import HighlightPlayer, HintStyle
from ...render.items.image_square_item import ImageSquareItem
from ...theme.highlight_theme_name import HighlightThemeName
from .base import Layout

if TYPE_CHECKING:
    from ...core.primitives import Square
    from .base import CacheKey

_HINT_THEME_MAPPING = {
    HighlightPlayer.PLAYER: {
        HintStyle.HINT: HighlightThemeName.HINT,
        HintStyle.OCCUPIED: HighlightThemeName.HINT_OCCUPIED,
        HintStyle.PSEUDO_HINT: HighlightThemeName.PSEUDO_HINT,
        HintStyle.PSEUDO_OCCUPIED: HighlightThemeName.PSEUDO_HINT_OCCUPIED,
    },
    HighlightPlayer.OPPONENT: {
        HintStyle.HINT: HighlightThemeName.OPPONENT_HINT,
        HintStyle.OCCUPIED: HighlightThemeName.OPPONENT_HINT_OCCUPIED,
        HintStyle.PSEUDO_HINT: HighlightThemeName.OPPONENT_PSEUDO_HINT,
        HintStyle.PSEUDO_OCCUPIED: HighlightThemeName.OPPONENT_PSEUDO_HINT_OCCUPIED,
    },
}


class HighlightLayout(Layout):
    """Computed layout data for highlight rendering."""

    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        pass

    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        pass

    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs.

        Returns:
            The cache key for the current inputs.
        """
        return ()

    def _get_item(self, theme_name: HighlightThemeName, square: Square) -> ImageSquareItem:
        """Return the render item associated with the given highlight state.

        Args:
            theme_name: Value supplied for ``theme_name``.
            square: Board square involved in the operation.

        Returns:
            The render item matching the requested highlight state, or ``None`` when the state is inactive.
        """
        if not self.view_state.white_at_bottom:
            square = square.rotated()
        return ImageSquareItem(copy(self.theme.highlight_assets[theme_name]), copy(self.square_rects[square.index]))

    def hint(self, highlight_player: HighlightPlayer, style: HintStyle, square: Square) -> ImageSquareItem:
        """Return the render item used for hint highlights.

        Args:
            highlight_player: Highlight owner to use.
            style: Highlight style to use.
            square: Square that should be rendered with the requested hint style.

        Returns:
            The render item used to draw hint highlights.
        """
        return self._get_item(_HINT_THEME_MAPPING[highlight_player][style], square)

    def selected(self, highlight_player: HighlightPlayer, square: Square) -> ImageSquareItem:
        """Return the render item used for selected-square highlights.

        Args:
            highlight_player: Highlight owner to use.
            square: Square that should be rendered as selected.

        Returns:
            The render item used to draw selected-square highlights.
        """
        if highlight_player is highlight_player.PLAYER:
            return self._get_item(HighlightThemeName.SELECTED, square)
        return self._get_item(HighlightThemeName.OPPONENT_SELECTED, square)

    def last_move(self, square: Square) -> ImageSquareItem:
        """Return the render item used for last-move highlights.

        Args:
            square: Square that should be rendered as part of the last-move highlight.

        Returns:
            The render item used to draw last-move highlights.
        """
        return self._get_item(HighlightThemeName.LAST_MOVE, square)

    def check(self, square: Square) -> ImageSquareItem:
        """Return the render item used for check highlights.

        Args:
            square: Square that should be rendered as the checked king square.

        Returns:
            The render item used to draw check highlights.
        """
        return self._get_item(HighlightThemeName.CHECK, square)
