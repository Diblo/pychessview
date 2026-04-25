# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Direct unit tests for concrete theme value objects."""

from pathlib import Path

import pytest

from pychessview.engine.core.exceptions import ThemeError
from pychessview.engine.core.primitives import Piece, PieceKind, PlayerColor
from pychessview.engine.layout.primitives import Color
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.theme.arrow_theme import ArrowTheme
from pychessview.engine.theme.circle_theme import CircleTheme
from pychessview.engine.theme.label_theme import LabelTheme
from pychessview.engine.theme.piece_theme import PieceTheme
from pychessview.engine.theme.promotion_theme import PromotionTheme

pytestmark = pytest.mark.unit


def test_annotation_theme_objects_reject_factors_outside_renderable_bounds() -> None:
    """Fail at theme construction before invalid annotation geometry reaches layout or rendering."""
    color = Color(1, 2, 3)

    with pytest.raises(ThemeError, match="arrow shaft factor"):
        ArrowTheme(0.31, 0.1, 0.1, color, color, color, color, color, color)

    with pytest.raises(ThemeError, match="circle scale factor"):
        CircleTheme(1.1, 0.1, color, color, color)


def test_piece_and_promotion_themes_reject_invalid_piece_scale_factors() -> None:
    """Protect piece rendering from scale factors outside the supported visual range."""
    color = Color(1, 2, 3)

    with pytest.raises(ThemeError, match="piece factor"):
        PieceTheme({}, 0.4, 1.1)

    with pytest.raises(ThemeError, match="promotion piece factor"):
        PromotionTheme(color, 1.1, color)


def test_piece_theme_load_copies_mutable_asset_mapping() -> None:
    """Avoid sharing asset dictionaries when replacing the active piece theme in-place."""
    king = Piece(PlayerColor.WHITE, PieceKind.KING)
    queen = Piece(PlayerColor.WHITE, PieceKind.QUEEN)
    king_asset = ImageAsset("king.svg", 10, 10)
    queen_asset = ImageAsset("queen.svg", 20, 20)
    source = PieceTheme({king: king_asset}, 1.0, 1.1)
    target = PieceTheme({}, 0.9, 1.1)

    target.load(source)
    source.add_asset(queen, queen_asset)

    assert target.assets == {king: king_asset}
    assert target.factor == 1.0
    assert target.drag_factor == 1.1


def test_label_theme_load_replaces_all_label_related_values() -> None:
    """Update label colors, fonts, and factors as one coherent value object."""
    source = LabelTheme(
        border_fill=Color(1, 2, 3),
        border_font=Path("border.ttf"),
        border_margin_factor=0.2,
        square_light_fill=Color(4, 5, 6),
        square_dark_fill=Color(7, 8, 9),
        square_font=Path("square.ttf"),
        square_factor=0.6,
        square_margin_factor=0.1,
    )
    target = LabelTheme(
        border_fill=Color(0, 0, 0),
        border_font=Path("old-border.ttf"),
        border_margin_factor=0.1,
        square_light_fill=Color(0, 0, 0),
        square_dark_fill=Color(0, 0, 0),
        square_font=Path("old-square.ttf"),
        square_factor=0.5,
        square_margin_factor=0.1,
    )

    target.load(source)

    assert target.border_fill == Color(1, 2, 3)
    assert target.border_font == Path("border.ttf")
    assert target.border_margin_factor == 0.2
    assert target.square_light_fill == Color(4, 5, 6)
    assert target.square_dark_fill == Color(7, 8, 9)
    assert target.square_font == Path("square.ttf")
    assert target.square_factor == 0.6
    assert target.square_margin_factor == 0.1


def test_circle_arrow_and_promotion_load_replace_visual_values() -> None:
    """Keep in-place theme replacement complete for annotation and promotion rendering settings."""
    red = Color(255, 0, 0)
    green = Color(0, 255, 0)
    blue = Color(0, 0, 255)
    arrow_source = ArrowTheme(0.1, 0.2, 0.3, red, green, blue, red, green, blue)
    arrow_target = ArrowTheme(0.05, 0.1, 0.2, blue, blue, blue, blue, blue, blue)
    circle_source = CircleTheme(0.8, 0.2, red, green, blue)
    circle_target = CircleTheme(0.5, 0.1, blue, blue, blue)
    promotion_source = PromotionTheme(red, 0.7, green)
    promotion_target = PromotionTheme(blue, 0.6, blue)

    arrow_target.load(arrow_source)
    circle_target.load(circle_source)
    promotion_target.load(promotion_source)

    assert (arrow_target.shaft_factor, arrow_target.head_length_factor, arrow_target.head_width_factor) == (
        0.1,
        0.2,
        0.3,
    )
    assert (arrow_target.primary_fill, arrow_target.secondary_fill, arrow_target.alternative_fill) == (
        red,
        green,
        blue,
    )
    assert (circle_target.scale_factor, circle_target.stroke_factor) == (0.8, 0.2)
    assert (circle_target.primary_fill, circle_target.secondary_fill, circle_target.alternative_fill) == (
        red,
        green,
        blue,
    )
    assert promotion_target.fill == red
    assert promotion_target.piece_factor == 0.7
    assert promotion_target.highlight_fill == green
