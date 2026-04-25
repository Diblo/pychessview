# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the null renderer."""

import pytest

from pychessview.engine.layout.primitives import Color, Coord, Rect, Viewport
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.render.items.arrow_item import ArrowItem
from pychessview.engine.render.items.circle_item import CircleItem
from pychessview.engine.render.items.color_square_item import ColorSquareItem
from pychessview.engine.render.items.image_square_item import ImageSquareItem
from pychessview.engine.render.items.label_item import LabelItem
from pychessview.engine.render.renderer.null_renderer import (
    BeginFrameCommand,
    DrawArrowCommand,
    DrawCircleCommand,
    DrawSquareColorCommand,
    DrawSquareImageCommand,
    DrawTextInkCommand,
    EndFrameCommand,
    NullRenderer,
)

pytestmark = pytest.mark.unit


def test_null_renderer_records_commands_in_render_order() -> None:
    """Record the renderer protocol surface as structured command objects.

    The null renderer is used by tests and non-GUI inspection code. It must
    preserve every draw call in order without doing real rendering.
    """
    renderer = NullRenderer()
    viewport = Viewport(0, 0, 100, 100)
    square_item = ColorSquareItem(Color(1, 2, 3), Rect(0, 0, 10, 10))
    image_item = ImageSquareItem(ImageAsset("piece.svg", 10, 10), Rect(0, 0, 10, 10))
    label_item = LabelItem(Rect(0, 0, 10, 10), "A")
    circle_item = CircleItem(2, Rect(0, 0, 10, 10))
    arrow_item = ArrowItem(2, 4, 6)
    arrow_points = (Coord(1, 1), Coord(9, 9))

    renderer.begin_frame(viewport)
    renderer.draw_square_color(square_item)
    renderer.draw_square_image(image_item)
    renderer.draw_text_ink(label_item)
    renderer.draw_circle(circle_item, Color(4, 5, 6))
    renderer.draw_arrow(arrow_item, Color(7, 8, 9), arrow_points)
    renderer.end_frame()

    assert renderer.commands == [
        BeginFrameCommand(viewport),
        DrawSquareColorCommand(square_item),
        DrawSquareImageCommand(image_item),
        DrawTextInkCommand(label_item),
        DrawCircleCommand(circle_item, Color(4, 5, 6)),
        DrawArrowCommand(arrow_item, Color(7, 8, 9), arrow_points),
        EndFrameCommand(),
    ]


def test_render_commands_compare_by_recorded_values() -> None:
    """Compare recorded commands by command type and stored fields.

    Tests that inspect render output should not need object identity. Command
    equality keeps assertions focused on the rendering contract.
    """
    viewport = Viewport(1, 2, 3, 4)

    assert BeginFrameCommand(viewport) == BeginFrameCommand(Viewport(1, 2, 3, 4))
    assert BeginFrameCommand(viewport) != EndFrameCommand()
    assert repr(BeginFrameCommand(viewport)) == "BeginFrameCommand(viewport=Viewport(x=1, y=2, width=3, height=4))"
