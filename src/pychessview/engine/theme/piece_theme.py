# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Piece theme configuration for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.primitives import Piece, PieceKind, PlayerColor
from .loaders import build_image_asset, get_theme_setting_float, get_theme_setting_path, validate_factor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Any

    from ..render.image_assets import ImageAsset


class PieceTheme:
    """Theme settings for piece rendering.

    Attributes:
        assets: Piece assets keyed by piece value.
        factor: Scale factor applied during rendering.
        drag_factor: Scale factor applied while dragging a piece.
    """

    __slots__ = "assets", "factor", "drag_factor"

    assets: dict[Piece, ImageAsset]
    factor: float
    drag_factor: float

    def __init__(self, assets: dict[Piece, ImageAsset], factor: float, drag_factor: float) -> None:
        """Initialize the piece theme with its initial configuration.

        Args:
            assets: Value used to initialize ``assets``.
            factor: Value used to initialize ``factor``.
            drag_factor: Value used to initialize ``drag_factor``.
        """
        self.assets = assets
        self.factor = validate_factor("piece factor", factor, 0.5, 1.2)
        self.drag_factor = validate_factor("piece drag factor", drag_factor, 1.0, 1.6)

    def add_asset(self, piece: Piece, asset: ImageAsset) -> None:
        """Register an asset path under the given key.

        Args:
            piece: Piece whose rendered asset should be replaced.
            asset: Image asset that should be used for ``piece``.
        """
        self.assets[piece] = asset

    def load(self, theme: PieceTheme) -> None:
        """Load settings or cached state from the provided source.

        Args:
            theme: Theme instance to use.
        """
        self.assets = dict(theme.assets)
        self.factor = theme.factor
        self.drag_factor = theme.drag_factor


def load_piece_theme_from_settings(data: Mapping[str, Any], root: Path) -> PieceTheme:
    """Create piece theme settings from parsed theme data.

    Args:
        data: Mapping containing the source data for the operation.
        root: Root directory used to resolve relative paths.

    Returns:
        Piece theme settings from parsed theme data.
    """
    return PieceTheme(
        assets={
            Piece(color, kind): build_image_asset(
                get_theme_setting_path(data, f"piece.{color.value}.{kind.text}.file", root)
            )
            for kind in PieceKind
            for color in (PlayerColor.WHITE, PlayerColor.BLACK)
        },
        factor=get_theme_setting_float(data, "piece.factor"),
        drag_factor=get_theme_setting_float(data, "piece.drag.factor"),
    )
