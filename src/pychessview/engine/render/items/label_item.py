# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Label item render item definitions for the pychessview package."""

from __future__ import annotations

from copy import copy
from pathlib import Path
from typing import TYPE_CHECKING

from ...layout.primitives import Color
from .base import Item

if TYPE_CHECKING:
    from ...layout.primitives import HorizontalAlign, Rect, VerticalAlign


class LabelItem(Item):
    """Renderable item describing a text label.

    Attributes:
        rect: Rectangle occupied by the render item.
        text: Text content for the label item.
        color: Color value associated with the object.
        size: Font size for the label item.
        font: Optional font path for the label item.
        v_align: Vertical alignment for label rendering.
        h_align: Horizontal alignment for label rendering.
    """

    __slots__ = "text", "color", "size", "font", "v_align", "h_align", "rect"

    rect: Rect
    text: str
    color: Color
    size: int
    font: Path | None
    v_align: VerticalAlign | None
    h_align: HorizontalAlign | None

    def __init__(
        self,
        rect: Rect,
        text: str,
        color: Color = Color(0, 0, 0),
        size: int = 12,
        *,
        font: Path | None = None,
        v_align: VerticalAlign | None = None,
        h_align: HorizontalAlign | None = None,
    ) -> None:
        """Initialize the label item with its initial configuration.

        Args:
            rect: Rectangle used to define geometry or clipping bounds.
            text: Text value to store or display.
            color: Color value associated with the object or operation.
            size: Size value used for layout or rendering.
        """
        self.rect = rect
        self.text = text
        self.color = color
        self.size = size
        self.font = font
        self.v_align = v_align
        self.h_align = h_align

    def __copy__(self) -> LabelItem:
        """Return a shallow copy of the instance.

        Returns:
            Shallow copy of the instance.
        """
        return type(self)(
            rect=copy(self.rect),
            text=self.text,
            color=copy(self.color),
            size=self.size,
            font=Path(self.font) if self.font else None,
            v_align=self.v_align,
            h_align=self.h_align,
        )
