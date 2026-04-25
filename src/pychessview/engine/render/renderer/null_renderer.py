# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Null renderer implementation for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .protocol import RendererProtocol

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    from ...layout.primitives import Color, Coord, Viewport
    from ..items.arrow_item import ArrowItem
    from ..items.circle_item import CircleItem
    from ..items.color_square_item import ColorSquareItem
    from ..items.image_square_item import ImageSquareItem
    from ..items.label_item import LabelItem


class _RenderCommandBase:
    """Base class for commands recorded by the null renderer."""

    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        """Return whether ``other`` represents the same value as this instance.

        Args:
            other: Object to compare against this instance.

        Returns:
            ``True`` when ``other`` represents the same value as this instance; otherwise, ``False``.
        """
        if type(self) is not type(other):
            return False

        slots = type(self).__slots__
        if isinstance(slots, str):
            slots = (slots,)

        return all(getattr(self, field) == getattr(other, field) for field in slots)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            Human-readable representation of the instance.
        """
        slots = type(self).__slots__
        if isinstance(slots, str):
            slots = (slots,)

        field_parts = ", ".join(f"{field}={getattr(self, field)!r}" for field in slots)
        return f"{type(self).__name__}({field_parts})"

    __repr__ = __str__


class BeginFrameCommand(_RenderCommandBase):
    """Recorded command that begins a frame.

    Attributes:
        kind: Piece kind associated with the object.
        viewport: Stored value for viewport.
    """

    __slots__ = "viewport"

    kind: Literal["begin_frame"] = "begin_frame"

    viewport: Viewport

    def __init__(self, viewport: Viewport) -> None:
        """Initialize the begin frame command with its initial configuration.

        Args:
            viewport: Viewport describing the available drawing area.
        """
        self.viewport = viewport


class DrawSquareColorCommand(_RenderCommandBase):
    """Recorded command that draws a solid square.

    Attributes:
        kind: Piece kind associated with the object.
        item: Render item associated with the recorded command.
    """

    __slots__ = "item"

    kind: Literal["draw_square_color"] = "draw_square_color"

    item: ColorSquareItem

    def __init__(self, item: ColorSquareItem) -> None:
        """Initialize the draw square color command with its initial configuration.

        Args:
            item: Value used to initialize ``item``.
        """
        self.item = item


class DrawSquareImageCommand(_RenderCommandBase):
    """Recorded command that draws an image-backed square.

    Attributes:
        kind: Piece kind associated with the object.
        item: Render item associated with the recorded command.
    """

    __slots__ = "item"

    kind: Literal["draw_square_image"] = "draw_square_image"

    item: ImageSquareItem

    def __init__(self, item: ImageSquareItem) -> None:
        """Initialize the draw square image command with its initial configuration.

        Args:
            item: Value used to initialize ``item``.
        """
        self.item = item


class DrawTextInkCommand(_RenderCommandBase):
    """Recorded command that draws text.

    Attributes:
        kind: Piece kind associated with the object.
        item: Render item associated with the recorded command.
    """

    __slots__ = "item"

    kind: Literal["draw_text_ink"] = "draw_text_ink"

    item: LabelItem

    def __init__(self, item: LabelItem) -> None:
        """Initialize the draw text ink command with its initial configuration.

        Args:
            item: Value used to initialize ``item``.
        """
        self.item = item


class DrawCircleCommand(_RenderCommandBase):
    """Recorded command that draws a circle.

    Attributes:
        kind: Piece kind associated with the object.
        item: Render item associated with the recorded command.
        color: Color value associated with the object.
    """

    __slots__ = "item", "color"

    kind: Literal["draw_circle"] = "draw_circle"

    item: CircleItem
    color: Color

    def __init__(self, item: CircleItem, color: Color) -> None:
        """Initialize the draw circle command with its initial configuration.

        Args:
            item: Value used to initialize ``item``.
            color: Color value associated with the object or operation.
        """
        self.item = item
        self.color = color


class DrawArrowCommand(_RenderCommandBase):
    """Recorded command that draws an arrow.

    Attributes:
        kind: Piece kind associated with the object.
        item: Render item associated with the recorded command.
        color: Color value associated with the object.
        points: Arrow geometry points used by the recorded command.
    """

    __slots__ = "item", "color", "points"

    kind: Literal["draw_arrow"] = "draw_arrow"

    item: ArrowItem
    color: Color
    points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]

    def __init__(self, item: ArrowItem, color: Color, points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]) -> None:
        """Initialize the draw arrow command with its initial configuration.

        Args:
            item: Value used to initialize ``item``.
            color: Color value associated with the object or operation.
            points: Value used to initialize ``points``.
        """
        self.item = item
        self.color = color
        self.points = points


class EndFrameCommand(_RenderCommandBase):
    """Recorded command that ends a frame.

    Attributes:
        kind: Piece kind associated with the object.
    """

    __slots__ = ()

    kind: Literal["end_frame"] = "end_frame"


RenderCommand: TypeAlias = (
    BeginFrameCommand
    | DrawSquareColorCommand
    | DrawSquareImageCommand
    | DrawTextInkCommand
    | DrawCircleCommand
    | DrawArrowCommand
    | EndFrameCommand
)
"""Type alias for commands recorded by NullRenderer."""


class NullRenderer(RendererProtocol):
    """Renderer that records draw commands instead of painting them.

    Attributes:
        commands: Recorded render commands.
    """

    __slots__ = "commands"

    commands: list[RenderCommand]

    def __init__(self) -> None:
        """Initialize the null renderer with its initial configuration."""
        self.commands = []

    def begin_frame(self, viewport: Viewport) -> None:
        """Begin drawing a frame.

        Args:
            viewport: Viewport to render.
        """
        self.commands.append(BeginFrameCommand(viewport=viewport))

    def draw_square_color(self, item: ColorSquareItem) -> None:
        """Draw a solid-color square item.

        Args:
            item: Render item to process.
        """
        self.commands.append(DrawSquareColorCommand(item))

    def draw_square_image(self, item: ImageSquareItem) -> None:
        """Draw an image-backed square item.

        Args:
            item: Render item to process.
        """
        self.commands.append(DrawSquareImageCommand(item))

    def draw_text_ink(self, item: LabelItem) -> None:
        """Draw a text label item.

        Args:
            item: Render item to process.
        """
        self.commands.append(DrawTextInkCommand(item))

    def draw_circle(self, item: CircleItem, color: Color) -> None:
        """Draw a circle item.

        Args:
            item: Render item to process.
            color: Stroke color to store with the recorded circle command.
        """
        self.commands.append(DrawCircleCommand(item, color))

    def draw_arrow(
        self, item: ArrowItem, color: Color, points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]
    ) -> None:
        """Draw an arrow item.

        Args:
            item: Render item to process.
            color: Fill color to store with the recorded arrow command.
            points: Arrow geometry points to draw.
        """
        self.commands.append(DrawArrowCommand(item, color, points))

    def end_frame(self) -> None:
        """Finish drawing a frame."""
        self.commands.append(EndFrameCommand())
