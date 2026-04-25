# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Arrow theme configuration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .loaders import get_theme_setting_color, get_theme_setting_float, validate_factor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..layout.primitives import Color


class ArrowTheme:
    """Theme settings for arrow annotations.

    Attributes:
        shaft_factor: Shaft-width factor for arrows.
        head_length_factor: Arrow head-length factor.
        head_width_factor: Arrow head-width factor.
        primary_fill: Primary fill color.
        secondary_fill: Secondary fill color.
        alternative_fill: Alternative fill color.
        hint_primary_fill: Primary hint fill color.
        hint_secondary_fill: Secondary hint fill color.
        hint_alternative_fill: Alternative hint fill color.
    """

    __slots__ = (
        "shaft_factor",
        "head_length_factor",
        "head_width_factor",
        "primary_fill",
        "secondary_fill",
        "alternative_fill",
        "hint_primary_fill",
        "hint_secondary_fill",
        "hint_alternative_fill",
    )

    shaft_factor: float
    head_length_factor: float
    head_width_factor: float
    primary_fill: Color
    secondary_fill: Color
    alternative_fill: Color
    hint_primary_fill: Color
    hint_secondary_fill: Color
    hint_alternative_fill: Color

    def __init__(
        self,
        shaft_factor: float,
        head_length_factor: float,
        head_width_factor: float,
        primary_fill: Color,
        secondary_fill: Color,
        alternative_fill: Color,
        hint_primary_fill: Color,
        hint_secondary_fill: Color,
        hint_alternative_fill: Color,
    ) -> None:
        """Initialize the arrow theme with its initial configuration.

        Args:
            shaft_factor: Value used to initialize ``shaft_factor``.
            head_length_factor: Value used to initialize ``head_length_factor``.
            head_width_factor: Value used to initialize ``head_width_factor``.
            primary_fill: Value used to initialize ``primary_fill``.
            secondary_fill: Value used to initialize ``secondary_fill``.
            alternative_fill: Value used to initialize ``alternative_fill``.
            hint_primary_fill: Value used to initialize ``hint_primary_fill``.
            hint_secondary_fill: Value used to initialize ``hint_secondary_fill``.
            hint_alternative_fill: Value used to initialize ``hint_alternative_fill``.
        """
        self.shaft_factor = validate_factor("arrow shaft factor", shaft_factor, 0.0, 0.3)
        self.head_length_factor = validate_factor("arrow head length factor", head_length_factor, 0.0, 0.6)
        self.head_width_factor = validate_factor("arrow head width factor", head_width_factor, 0.0, 0.6)
        self.primary_fill = primary_fill
        self.secondary_fill = secondary_fill
        self.alternative_fill = alternative_fill
        self.hint_primary_fill = hint_primary_fill
        self.hint_secondary_fill = hint_secondary_fill
        self.hint_alternative_fill = hint_alternative_fill

    def load(self, theme: ArrowTheme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        self.shaft_factor = theme.shaft_factor
        self.head_length_factor = theme.head_length_factor
        self.head_width_factor = theme.head_width_factor
        self.primary_fill = theme.primary_fill
        self.secondary_fill = theme.secondary_fill
        self.alternative_fill = theme.alternative_fill
        self.hint_primary_fill = theme.hint_primary_fill
        self.hint_secondary_fill = theme.hint_secondary_fill
        self.hint_alternative_fill = theme.hint_alternative_fill


def load_arrow_theme_from_settings(data: Mapping[str, Any]) -> ArrowTheme:
    """Create arrow theme settings from parsed theme data.

    Args:
        data: Mapping containing the source data for the operation.

    Returns:
        Arrow theme settings from parsed theme data.
    """
    return ArrowTheme(
        shaft_factor=get_theme_setting_float(data, "annotation.arrow.shaft"),
        head_length_factor=get_theme_setting_float(data, "annotation.arrow.head.length"),
        head_width_factor=get_theme_setting_float(data, "annotation.arrow.head.width"),
        primary_fill=get_theme_setting_color(data, "annotation.arrow.primary"),
        secondary_fill=get_theme_setting_color(data, "annotation.arrow.secondary"),
        alternative_fill=get_theme_setting_color(data, "annotation.arrow.alternative"),
        hint_primary_fill=get_theme_setting_color(data, "annotation.arrow.hint.primary"),
        hint_secondary_fill=get_theme_setting_color(data, "annotation.arrow.hint.secondary"),
        hint_alternative_fill=get_theme_setting_color(data, "annotation.arrow.hint.alternative"),
    )
