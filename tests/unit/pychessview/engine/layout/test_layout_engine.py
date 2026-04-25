# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the layout engine."""

import pytest

from pychessview.engine.core.primitives import File, PlayerColor, Rank, Square
from pychessview.engine.core.state.view_state import ViewState
from pychessview.engine.layout.layout_engine import (
    _calc_edges,  # pyright: ignore[reportPrivateUsage]
    _distributed_sizes,  # pyright: ignore[reportPrivateUsage]
    _round_half_up,  # pyright: ignore[reportPrivateUsage]
)
from pychessview.engine.layout.primitives import Viewport

from .._helpers import create_layout_engine

pytestmark = pytest.mark.unit


def test_layout_helper_functions_use_half_up_pixel_distribution() -> None:
    """Keep pixel splitting deterministic when board sizes do not divide evenly.

    Layout rectangles are built from these helpers, so cumulative edges must
    preserve the total pixel size without introducing rounding drift.
    """
    assert _round_half_up(1.4) == 1
    assert _round_half_up(1.5) == 2
    assert _distributed_sizes(10, 3) == (3, 4, 3)
    assert _calc_edges(5, (2, 3, 4)) == (5, 7, 10, 14)


def test_layout_engine_centers_square_board_when_not_stretched() -> None:
    """Compute a square board inside a non-square viewport.

    The default layout keeps the board square and centered, with an optional
    border separating board edges from playable squares.
    """
    engine = create_layout_engine()

    assert engine.is_renderable is True
    assert engine.border_width == 5
    assert engine.vertical_edges[0] == 10
    assert engine.horizontal_edges[0] == 30
    assert engine.vertical_edges[-1] == 110
    assert engine.horizontal_edges[-1] == 130
    assert sum(engine.file_sizes) == 90
    assert sum(engine.rank_sizes) == 90


def test_layout_engine_stretches_to_full_viewport_when_enabled() -> None:
    """Use the entire viewport when stretch-to-fit is enabled.

    Integrations that want rectangular board scaling rely on the engine using
    viewport width and height directly instead of forcing a square board.
    """
    view_state = ViewState(PlayerColor.WHITE, stretch_to_fit=True)
    engine = create_layout_engine(view_state=view_state)

    assert engine.vertical_edges[0] == 10
    assert engine.horizontal_edges[0] == 20
    assert engine.vertical_edges[-1] == 110
    assert engine.horizontal_edges[-1] == 140


def test_layout_engine_marks_too_small_viewports_as_not_renderable() -> None:
    """Avoid building square geometry when the playable area is too small.

    Query and render layers use ``is_renderable`` to skip work that would
    otherwise depend on missing edge and size data.
    """
    engine = create_layout_engine(viewport=Viewport(0, 0, 10, 10))

    assert engine.is_renderable is False
    assert engine.key == ()


def test_layout_engine_square_rect_inputs_follow_board_coordinates() -> None:
    """Expose geometry data that maps core squares to board coordinates.

    The layout engine stores edges and sizes rather than prebuilt rectangles;
    callers combine those values with file and rank indexes to position items.
    """
    engine = create_layout_engine(viewport=Viewport(0, 0, 80, 80))
    square = Square(File.A, Rank.ONE)
    file_index = int(square.file)
    rank_index = Rank.EIGHT.value - square.rank.value

    assert engine.vertical_edges[file_index + 1] == 4
    assert engine.horizontal_edges[rank_index + 1] == 67
