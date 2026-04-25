# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Private layout helpers for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .primitives import Rect

if TYPE_CHECKING:
    from ..render.image_assets import ImageAsset


def fit_piece_asset_rect(piece_asset: ImageAsset, rect: Rect) -> Rect:
    """Scale and center a piece asset inside a target rectangle.

    Args:
        piece_asset: Value supplied for ``piece_asset``.
        rect: Value supplied for ``rect``.

    Returns:
        Scale and center a piece asset inside a target rectangle.
    """
    scale = min(rect.width / piece_asset.width, rect.height / piece_asset.height)
    draw_width = max(1, int(piece_asset.width * scale))
    draw_height = max(1, int(piece_asset.height * scale))

    x = rect.x + (rect.width - draw_width) // 2
    y = rect.y + (rect.height - draw_height) // 2

    return Rect(x=x, y=y, width=draw_width, height=draw_height)
