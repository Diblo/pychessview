# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Label theme configuration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .loaders import get_theme_setting_color, get_theme_setting_float, get_theme_setting_path, validate_factor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any

    from ..layout.primitives import Color


class LabelTheme:
    """Theme settings for board labels.

    Attributes:
        border_fill: Fill color for border labels.
        border_font: Font path for border labels.
        border_margin_factor: Margin factor for border labels.
        square_light_fill: Fill color for labels on light squares.
        square_dark_fill: Fill color for labels on dark squares.
        square_font: Font path for square labels.
        square_factor: Font-size factor for square labels.
        square_margin_factor: Margin factor for square labels.
    """

    __slots__ = (
        "border_fill",
        "border_font",
        "border_margin_factor",
        "square_light_fill",
        "square_dark_fill",
        "square_font",
        "square_factor",
        "square_margin_factor",
    )

    border_fill: Color
    border_font: Path
    border_margin_factor: float
    square_light_fill: Color
    square_dark_fill: Color
    square_font: Path
    square_factor: float
    square_margin_factor: float

    def __init__(
        self,
        border_fill: Color,
        border_font: Path,
        border_margin_factor: float,
        square_light_fill: Color,
        square_dark_fill: Color,
        square_font: Path,
        square_factor: float,
        square_margin_factor: float,
    ) -> None:
        """Initialize the label theme with its initial configuration.

        Args:
            border_fill: Value used to initialize ``border_fill``.
            border_font: Value used to initialize ``border_font``.
            border_margin_factor: Value used to initialize ``border_margin_factor``.
            square_light_fill: Value used to initialize ``square_light_fill``.
            square_dark_fill: Value used to initialize ``square_dark_fill``.
            square_font: Value used to initialize ``square_font``.
            square_factor: Value used to initialize ``square_factor``.
            square_margin_factor: Value used to initialize ``square_margin_factor``.
        """
        self.border_fill = border_fill
        self.border_font = border_font
        self.border_margin_factor = validate_factor("label border margin factor", border_margin_factor, 0.0, 0.4)
        self.square_light_fill = square_light_fill
        self.square_dark_fill = square_dark_fill
        self.square_font = square_font
        self.square_factor = validate_factor("label square factor", square_factor, 0.0, 1.0)
        self.square_margin_factor = validate_factor("label square margin factor", square_margin_factor, 0.0, 0.4)

    def load(self, theme: LabelTheme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        self.border_fill = theme.border_fill
        self.border_font = theme.border_font
        self.border_margin_factor = theme.border_margin_factor
        self.square_light_fill = theme.square_light_fill
        self.square_dark_fill = theme.square_dark_fill
        self.square_font = theme.square_font
        self.square_factor = theme.square_factor
        self.square_margin_factor = theme.square_margin_factor


def load_label_theme_from_settings(data: Mapping[str, Any], root: Path) -> LabelTheme:
    """Create label theme settings from parsed theme data.

    Args:
        data: Mapping containing the source data for the operation.
        root: Root directory used to resolve relative paths.

    Returns:
        Label theme settings from parsed theme data.
    """
    return LabelTheme(
        border_fill=get_theme_setting_color(data, "board.label.border.fill"),
        border_font=get_theme_setting_path(data, "board.label.border.font", root),
        border_margin_factor=get_theme_setting_float(data, "board.label.border.margin.factor"),
        square_light_fill=get_theme_setting_color(data, "board.label.square.light.fill"),
        square_dark_fill=get_theme_setting_color(data, "board.label.square.dark.fill"),
        square_font=get_theme_setting_path(data, "board.label.square.font", root),
        square_factor=get_theme_setting_float(data, "board.label.square.factor"),
        square_margin_factor=get_theme_setting_float(data, "board.label.square.margin.factor"),
    )
