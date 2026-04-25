# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Theme loading and composition for the pychessview package."""

from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path
from typing import TYPE_CHECKING

from .arrow_theme import load_arrow_theme_from_settings
from .circle_theme import load_circle_theme_from_settings
from .highlight_theme_name import HighlightThemeName
from .label_theme import load_label_theme_from_settings
from .loaders import (
    build_image_asset,
    get_theme_setting_color,
    get_theme_setting_float,
    get_theme_setting_path,
    load_setting_data,
    validate_factor,
)
from .piece_theme import load_piece_theme_from_settings
from .promotion_theme import load_promotion_theme_from_settings
from .theme_name import ThemeName

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from ..layout.primitives import Color
    from ..render.image_assets import ImageAsset
    from .arrow_theme import ArrowTheme
    from .circle_theme import CircleTheme
    from .label_theme import LabelTheme
    from .piece_theme import PieceTheme
    from .promotion_theme import PromotionTheme


class Theme:
    """Stores the assets and colors used to render a pychessview.

    Attributes:
        background_fill: Background fill color outside the board.
        board_fill: Fill color used behind the board content.
        border_factor: Board border thickness factor.
        light_square_asset: Image asset used for light squares.
        dark_square_asset: Image asset used for dark squares.
        highlight_assets: Highlight image assets keyed by highlight name.
    """

    __slots__ = (
        "background_fill",
        "board_fill",
        "border_factor",
        "light_square_asset",
        "dark_square_asset",
        "highlight_assets",
        "_label",
        "_piece",
        "_promotion",
        "_circle",
        "_arrow",
    )

    background_fill: Color
    board_fill: Color
    border_factor: float
    light_square_asset: ImageAsset
    dark_square_asset: ImageAsset
    highlight_assets: dict[HighlightThemeName, ImageAsset]
    _label: LabelTheme
    _piece: PieceTheme
    _promotion: PromotionTheme
    _circle: CircleTheme
    _arrow: ArrowTheme

    def __init__(
        self,
        background_fill: Color,
        board_fill: Color,
        border_factor: float,
        light_square_asset: ImageAsset,
        dark_square_asset: ImageAsset,
        highlight_assets: dict[HighlightThemeName, ImageAsset],
        label: LabelTheme,
        piece: PieceTheme,
        promotion: PromotionTheme,
        circle: CircleTheme,
        arrow: ArrowTheme,
    ) -> None:
        """Initialize the theme with its initial configuration.

        Args:
            background_fill: Value used to initialize ``background_fill``.
            board_fill: Value used to initialize ``board_fill``.
            border_factor: Value used to initialize ``border_factor``.
            light_square_asset: Value used to initialize ``light_square_asset``.
            dark_square_asset: Value used to initialize ``dark_square_asset``.
            highlight_assets: Value used to initialize ``highlight_assets``.
            label: Label value associated with the object.
            piece: Piece value associated with the object or operation.
            promotion: Value used to initialize ``promotion``.
            circle: Circle value used to initialize the object.
            arrow: Arrow value used to initialize the object.
        """
        self.background_fill = background_fill
        self.board_fill = board_fill
        self.border_factor = validate_factor("border factor", border_factor, 0.0, 0.2)
        self.light_square_asset = light_square_asset
        self.dark_square_asset = dark_square_asset
        self.highlight_assets = highlight_assets
        self._label = label
        self._piece = piece
        self._promotion = promotion
        self._circle = circle
        self._arrow = arrow

    def load(self, theme: Theme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        if theme is self:
            return

        self.background_fill = theme.background_fill
        self.board_fill = theme.board_fill
        self.border_factor = theme.border_factor
        self.light_square_asset = theme.light_square_asset
        self.dark_square_asset = theme.dark_square_asset
        self.highlight_assets = dict(theme.highlight_assets)

        self._label.load(theme.label)
        self._piece.load(theme.piece)
        self._promotion.load(theme.promotion)
        self._circle.load(theme.circle)
        self._arrow.load(theme.arrow)

    def add_highlight_asset(self, highlight_name: HighlightThemeName, highlight_asset: ImageAsset) -> None:
        """Register a highlight asset path under the given highlight type.

        Args:
            highlight_name: Highlight theme slot that should receive the asset.
            highlight_asset: Image asset that should be used for ``highlight_name``.
        """
        self.highlight_assets[highlight_name] = highlight_asset

    @property
    def label(self) -> LabelTheme:
        """Label theme settings.

        Returns:
            Label theme settings.
        """
        return self._label

    @property
    def piece(self) -> PieceTheme:
        """Piece theme settings.

        Returns:
            Piece theme settings.
        """
        return self._piece

    @property
    def promotion(self) -> PromotionTheme:
        """Promotion theme settings.

        Returns:
            Promotion theme settings.
        """
        return self._promotion

    @property
    def circle(self) -> CircleTheme:
        """Circle annotation theme settings.

        Returns:
            Circle annotation theme settings.
        """
        return self._circle

    @property
    def arrow(self) -> ArrowTheme:
        """Arrow annotation theme settings.

        Returns:
            Arrow annotation theme settings.
        """
        return self._arrow


def load_theme_from_settings(data: Mapping[str, Any], root: Path) -> Theme:
    """Build a theme from parsed theme settings.

    Args:
        data: Mapping containing the source data for the operation.
        root: Root directory used to resolve relative paths.

    Returns:
        A theme from parsed theme settings.
    """
    return Theme(
        background_fill=get_theme_setting_color(data, "fill"),
        board_fill=get_theme_setting_color(data, "board.fill"),
        border_factor=get_theme_setting_float(data, "board.border.factor"),
        light_square_asset=build_image_asset(get_theme_setting_path(data, "board.square.light.file", root)),
        dark_square_asset=build_image_asset(get_theme_setting_path(data, "board.square.dark.file", root)),
        highlight_assets={
            name: build_image_asset(get_theme_setting_path(data, f"highlight.{name.value}.file", root))
            for name in HighlightThemeName
        },
        label=load_label_theme_from_settings(data, root),
        piece=load_piece_theme_from_settings(data, root),
        promotion=load_promotion_theme_from_settings(data),
        circle=load_circle_theme_from_settings(data),
        arrow=load_arrow_theme_from_settings(data),
    )


def load_theme(path: ThemeName | Path | str) -> Theme:
    """Load a theme from a built-in name or filesystem path.

    Args:
        path: Filesystem path involved in the operation.

    Returns:
        A theme from a built-in name or filesystem path.
    """
    if isinstance(path, ThemeName):
        resource = files("pychessview.assets.themes").joinpath(path.value).joinpath("settings.yaml")
        with as_file(resource) as settings_path:
            return load_theme_from_settings(load_setting_data(settings_path), settings_path.parent)

    if isinstance(path, str):
        path = Path(path)

    if not path.is_file():
        path = path / "settings.yaml"

    return load_theme_from_settings(load_setting_data(path), path.parent)
