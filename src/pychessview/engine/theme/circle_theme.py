# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Circle theme configuration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .loaders import get_theme_setting_color, get_theme_setting_float, validate_factor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..layout.primitives import Color


class CircleTheme:
    """Theme settings for circle annotations.

    Attributes:
        scale_factor: Scale factor for the themed element.
        stroke_factor: Stroke-width factor for the themed element.
        primary_fill: Primary fill color.
        secondary_fill: Secondary fill color.
        alternative_fill: Alternative fill color.
    """

    __slots__ = "scale_factor", "stroke_factor", "primary_fill", "secondary_fill", "alternative_fill"

    scale_factor: float
    stroke_factor: float
    primary_fill: Color
    secondary_fill: Color
    alternative_fill: Color

    def __init__(
        self,
        scale_factor: float,
        stroke_factor: float,
        primary_fill: Color,
        secondary_fill: Color,
        alternative_fill: Color,
    ) -> None:
        """Initialize the circle theme with its initial configuration.

        Args:
            scale_factor: Value used to initialize ``scale_factor``.
            stroke_factor: Value used to initialize ``stroke_factor``.
            primary_fill: Value used to initialize ``primary_fill``.
            secondary_fill: Value used to initialize ``secondary_fill``.
            alternative_fill: Value used to initialize ``alternative_fill``.
        """
        self.scale_factor = validate_factor("circle scale factor", scale_factor, 0.0, 1.0)
        self.stroke_factor = validate_factor("circle stroke factor", stroke_factor, 0.0, 1.0)
        self.primary_fill = primary_fill
        self.secondary_fill = secondary_fill
        self.alternative_fill = alternative_fill

    def load(self, theme: CircleTheme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        self.scale_factor = theme.scale_factor
        self.stroke_factor = theme.stroke_factor
        self.primary_fill = theme.primary_fill
        self.secondary_fill = theme.secondary_fill
        self.alternative_fill = theme.alternative_fill


def load_circle_theme_from_settings(data: Mapping[str, Any]) -> CircleTheme:
    """Create circle theme settings from parsed theme data.

    Args:
        data: Mapping containing the source data for the operation.

    Returns:
        Circle theme settings from parsed theme data.
    """
    return CircleTheme(
        scale_factor=get_theme_setting_float(data, "annotation.circle.scale"),
        stroke_factor=get_theme_setting_float(data, "annotation.circle.stroke"),
        primary_fill=get_theme_setting_color(data, "annotation.circle.primary"),
        secondary_fill=get_theme_setting_color(data, "annotation.circle.secondary"),
        alternative_fill=get_theme_setting_color(data, "annotation.circle.alternative"),
    )
