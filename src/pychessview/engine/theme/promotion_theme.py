# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Promotion theme configuration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .loaders import get_theme_setting_color, get_theme_setting_float, validate_factor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..layout.primitives import Color


class PromotionTheme:
    """Theme settings for promotion rendering.

    Attributes:
        fill: Base fill color for the themed element.
        piece_factor: Scale factor applied to promotion pieces.
        highlight_fill: Highlight fill color for the themed element.
    """

    __slots__ = "fill", "piece_factor", "highlight_fill"

    fill: Color
    piece_factor: float
    highlight_fill: Color

    def __init__(self, fill: Color, piece_factor: float, highlight_fill: Color) -> None:
        """Initialize the promotion theme with its initial configuration.

        Args:
            fill: Value used to initialize ``fill``.
            piece_factor: Value used to initialize ``piece_factor``.
            highlight_fill: Value used to initialize ``highlight_fill``.
        """
        self.fill = fill
        self.piece_factor = validate_factor("promotion piece factor", piece_factor, 0.5, 1.0)
        self.highlight_fill = highlight_fill

    def load(self, theme: PromotionTheme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        self.fill = theme.fill
        self.piece_factor = theme.piece_factor
        self.highlight_fill = theme.highlight_fill


def load_promotion_theme_from_settings(data: Mapping[str, Any]) -> PromotionTheme:
    """Create promotion theme settings from parsed theme data.

    Args:
        data: Mapping containing the source data for the operation.

    Returns:
        Promotion theme settings from parsed theme data.
    """
    return PromotionTheme(
        fill=get_theme_setting_color(data, "promotion.fill"),
        piece_factor=get_theme_setting_float(data, "promotion.piece.factor"),
        highlight_fill=get_theme_setting_color(data, "promotion.highlight.fill"),
    )
