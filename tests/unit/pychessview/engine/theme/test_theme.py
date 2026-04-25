# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for composed theme objects."""

import pytest

from pychessview.engine.core.exceptions import ThemeError
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.theme.highlight_theme_name import HighlightThemeName
from pychessview.engine.theme.theme import Theme, load_theme
from pychessview.engine.theme.theme_name import ThemeName

pytestmark = [pytest.mark.unit, pytest.mark.requires_imagesize]


def test_load_theme_reads_built_in_default_assets() -> None:
    """Load the built-in theme into the composed theme model.

    The factory and board-session tests depend on built-in theme loading, so a
    focused unit test protects the package resource path and required assets.
    """
    theme = load_theme(ThemeName.DEFAULT)

    assert isinstance(theme, Theme)
    assert theme.border_factor > 0
    assert theme.light_square_asset.width > 0
    assert theme.dark_square_asset.height > 0
    assert HighlightThemeName.SELECTED in theme.highlight_assets
    assert Piece(PlayerColor.WHITE, PieceKind.KING) in theme.piece.assets


def test_theme_load_copies_mutable_asset_mappings() -> None:
    """Copy mutable theme mappings when loading another theme instance.

    ``Theme.load`` is used to replace active theme settings in-place. The target
    theme should not keep references to mutable dictionaries owned by source.
    """
    source = load_theme(ThemeName.DEFAULT)
    target = load_theme(ThemeName.DEFAULT)
    replacement = ImageAsset("replacement.svg", 1, 1)

    source.add_highlight_asset(HighlightThemeName.SELECTED, replacement)
    target.load(source)
    source.add_highlight_asset(HighlightThemeName.SELECTED, ImageAsset("other.svg", 2, 2))

    assert target.highlight_assets[HighlightThemeName.SELECTED] == replacement


def test_theme_rejects_invalid_border_factor() -> None:
    """Reject composed themes with board border factors outside supported bounds.

    Layout uses the border factor to calculate playable board space, so invalid
    values must fail while the theme object is built.
    """
    base = load_theme(ThemeName.DEFAULT)

    with pytest.raises(ThemeError, match="border factor"):
        Theme(
            base.background_fill,
            base.board_fill,
            1.0,
            base.light_square_asset,
            base.dark_square_asset,
            base.highlight_assets,
            base.label,
            base.piece,
            base.promotion,
            base.circle,
            base.arrow,
        )
