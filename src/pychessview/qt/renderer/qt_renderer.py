# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Qt renderer implementation for the pychessview.qt package."""

from __future__ import annotations

from math import atan2, cos, degrees, hypot, sin
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtSvg import QSvgRenderer

from pychessview import RendererProtocol
from pychessview.engine.layout.primitives import HorizontalAlign, VerticalAlign

from .painter_adapter import PainterAdapter

if TYPE_CHECKING:
    from pathlib import Path

    from pychessview.engine.layout.primitives import Color, Coord, Viewport
    from pychessview.engine.render.items.arrow_item import ArrowItem
    from pychessview.engine.render.items.circle_item import CircleItem
    from pychessview.engine.render.items.color_square_item import ColorSquareItem
    from pychessview.engine.render.items.image_square_item import ImageSquareItem
    from pychessview.engine.render.items.label_item import LabelItem


def _align_offset(align: HorizontalAlign | VerticalAlign | None, outer: float, inner: float) -> float:
    """Return the alignment offset needed to place an item inside the outer span.

    Args:
        align: Alignment to apply within the available span.
        outer: Size of the available span.
        inner: Size of the item that should be aligned.

    Returns:
        Offset needed to place the item inside the outer span.
    """
    if outer <= 0:
        return 0.0

    # If the text bounds are larger than the target box we anchor at the start edge.
    max_offset = max(0.0, outer - inner)

    if align is HorizontalAlign.CENTER or align is VerticalAlign.CENTER:
        return max_offset / 2.0

    if align is HorizontalAlign.RIGHT or align is VerticalAlign.BOTTOM:
        return max_offset

    return 0.0


def _build_arrow_geometry(
    item: ArrowItem, points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]
) -> tuple[QPainterPath, QPainterPath, QPainterPath]:
    """Build Qt painter paths for an arrow render item.

    Args:
        item: Arrow render item that defines the shaft and head dimensions.
        points: Arrow control points in painter coordinates.

    Returns:
        Tuple containing the tail cap, shaft fill, and head paths for the arrow.
    """
    qpoints = [QPointF(coord.x, coord.y) for coord in points]

    tip_point = qpoints[-1]

    # shaft
    prev_shaft_point = qpoints[-2]
    delta_x = tip_point.x() - prev_shaft_point.x()
    delta_y = tip_point.y() - prev_shaft_point.y()

    angle = atan2(delta_y, delta_x)
    shaft_end_distance = max(0.0, hypot(delta_x, delta_y) - item.head_length)
    shaft_end_point = QPointF(
        prev_shaft_point.x() + shaft_end_distance * cos(angle), prev_shaft_point.y() + shaft_end_distance * sin(angle)
    )

    shaft_points = [*qpoints[:-1], shaft_end_point]
    shaft_path = QPainterPath(shaft_points[0])
    for point in shaft_points[1:]:
        shaft_path.lineTo(point)

    stroker = QPainterPathStroker()
    stroker.setWidth(float(item.shaft_width))
    stroker.setCapStyle(Qt.PenCapStyle.FlatCap)
    shaft_fill_path = stroker.createStroke(shaft_path)

    # tail cap
    start_shaft_point = shaft_points[0]
    next_shaft_point = shaft_points[1]
    shaft_radius = item.shaft_width / 2.0
    tail_angle = atan2(next_shaft_point.y() - start_shaft_point.y(), next_shaft_point.x() - start_shaft_point.x())
    tail_arc_rect = QRectF(
        start_shaft_point.x() - shaft_radius, start_shaft_point.y() - shaft_radius, item.shaft_width, item.shaft_width
    )
    tail_cap_path = QPainterPath()
    tail_start_angle = 90.0 - degrees(tail_angle)
    tail_cap_path.arcMoveTo(tail_arc_rect, tail_start_angle)
    tail_cap_path.arcTo(tail_arc_rect, tail_start_angle, 180.0)
    tail_cap_path.closeSubpath()

    # head
    head_width = item.head_width / 2.0
    left_point = QPointF(
        tip_point.x() - item.head_length * cos(angle) + head_width * sin(angle),
        tip_point.y() - item.head_length * sin(angle) - head_width * cos(angle),
    )
    right_point = QPointF(
        tip_point.x() - item.head_length * cos(angle) - head_width * sin(angle),
        tip_point.y() - item.head_length * sin(angle) + head_width * cos(angle),
    )
    head_path = QPainterPath()
    head_path.addPolygon(QPolygonF([tip_point, left_point, right_point]))
    head_path.closeSubpath()

    return (tail_cap_path, shaft_fill_path, head_path)


class QtRenderer(RendererProtocol):
    """Renderer that draws pychessview items with Qt."""

    __slots__ = "_painter_adapter", "_svg_renderer_cache", "_pixmap_cache", "_font_family_cache"

    _painter_adapter: PainterAdapter
    _svg_renderer_cache: dict[Path, QSvgRenderer]
    _pixmap_cache: dict[Path, QPixmap]
    _font_family_cache: dict[Path, str]

    def __init__(self) -> None:
        """Initialize the Qt renderer with the painter adapter and assets used to draw render items."""
        self._painter_adapter = PainterAdapter()
        self._svg_renderer_cache = {}
        self._pixmap_cache = {}
        self._font_family_cache = {}

    def set_painter(self, painter: QPainter) -> None:
        """Store the active ``QPainter`` used for subsequent drawing calls.

        Args:
            painter: QPainter instance to store.
        """
        self._painter_adapter.set_painter(painter)

    def begin_frame(self, viewport: Viewport) -> None:
        """Begin drawing a frame.

        Args:
            viewport: Viewport to render.
        """
        _ = viewport
        painter = self._painter_adapter.require_painter()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    def draw_square_color(self, item: ColorSquareItem) -> None:
        """Draw a solid-color square item.

        Args:
            item: Render item to process.
        """
        painter = self._painter_adapter.require_painter()
        rect = item.rect
        color = item.color
        painter.fillRect(QRectF(rect.x, rect.y, rect.width, rect.height), QColor(color.r, color.g, color.b, color.a))

    def draw_square_image(self, item: ImageSquareItem) -> None:
        """Draw an image-backed square item.

        Args:
            item: Render item to process.
        """
        rect = item.rect
        image_asset = item.image_asset
        image_path = image_asset.path

        qrect = QRectF(rect.x, rect.y, rect.width, rect.height)

        if image_path.suffix.lower() == ".svg":
            self._draw_svg(image_path, qrect)
            return

        self._draw_raster(image_path, qrect)

    def draw_circle(self, item: CircleItem, color: Color) -> None:
        """Draw a circle item.

        Args:
            item: Render item to process.
            color: Stroke color to use for the circle.
        """
        painter = self._painter_adapter.require_painter()
        stroke_width = float(item.stroke_width)
        inset = stroke_width / 2.0

        pen = QPen(QColor(color.r, color.g, color.b, color.a))
        pen.setWidthF(stroke_width)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            QRectF(
                item.rect.x + inset,
                item.rect.y + inset,
                max(0.0, item.rect.width - stroke_width),
                max(0.0, item.rect.height - stroke_width),
            )
        )

    def draw_arrow(
        self, item: ArrowItem, color: Color, points: tuple[Coord, Coord] | tuple[Coord, Coord, Coord]
    ) -> None:
        """Draw an arrow item.

        Args:
            item: Render item to process.
            color: Fill color to use for the arrow geometry.
            points: Arrow geometry points to draw.
        """
        painter = self._painter_adapter.require_painter()
        tail_cap_path, shaft_path, head_path = _build_arrow_geometry(item, points)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color.r, color.g, color.b, color.a))
        painter.drawPath(tail_cap_path.united(shaft_path).united(head_path))

    def draw_text_ink(self, item: LabelItem) -> None:
        """Draw a text label item.

        Args:
            item: Render item to process.
        """
        painter = self._painter_adapter.require_painter()
        rect = item.rect
        color = item.color

        painter.setPen(QColor(color.r, color.g, color.b, color.a))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Set the font and font size
        font = self._ensure_font_family(item.font)
        font.setPointSizeF(float(item.size))
        painter.setFont(font)

        # Calculate the position to draw the text based on the alignment and bounding box of the text.
        metrics = QFontMetricsF(font)
        bounds = metrics.tightBoundingRect(item.text)

        x_offset = _align_offset(item.h_align, rect.width, bounds.width())
        y_offset = _align_offset(item.v_align, rect.height, bounds.height())

        desired_left = float(rect.x) + x_offset
        desired_top = float(rect.y) + y_offset
        baseline_x = desired_left - bounds.left()
        baseline_y = desired_top - bounds.top()

        # Draw the text at the calculated position.
        painter.drawText(QPointF(baseline_x, baseline_y), item.text)

    def end_frame(self) -> None:
        """Finish drawing a frame."""
        pass

    def _draw_svg(self, image_path: Path, rect: QRectF) -> None:
        """Draw an SVG asset into the target rectangle.

        Args:
            image_path: Filesystem path to the SVG asset.
            rect: Target rectangle in painter coordinates.
        """
        painter = self._painter_adapter.require_painter()

        renderer = self._svg_renderer_cache.get(image_path)
        if renderer is None:
            renderer = QSvgRenderer(str(image_path))
            if not renderer.isValid():
                raise RuntimeError(f"failed to load svg '{image_path}'")
            self._svg_renderer_cache[image_path] = renderer

        renderer.render(painter, rect)

    def _draw_raster(self, image_path: Path, rect: QRectF) -> None:
        """Draw a raster asset into the target rectangle.

        Args:
            image_path: Filesystem path to the raster asset.
            rect: Target rectangle in painter coordinates.
        """
        painter = self._painter_adapter.require_painter()

        pixmap = self._pixmap_cache.get(image_path)
        if pixmap is None:
            pixmap = QPixmap(str(image_path))
            if pixmap.isNull():
                raise RuntimeError(f"failed to load image '{image_path}'")
            self._pixmap_cache[image_path] = pixmap

        painter.drawPixmap(rect, pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))

    def _ensure_font_family(self, font_path: Path | None) -> QFont:
        """Return a QFont for the requested font file.

        Args:
            font_path: Filesystem path to the font file that should be loaded.

        Returns:
            ``QFont`` configured with the requested family.
        """
        if font_path is None:
            raise RuntimeError("font_path is None, but QtRenderer requires a valid font file path to render text")

        family = self._font_family_cache.get(font_path)
        if family is not None:
            return QFont(family)

        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            raise RuntimeError(f"failed to register font file '{font_path}' in QFontDatabase")

        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            raise RuntimeError(f"QFontDatabase returned no families for '{font_path}'")

        family = str(families[0])
        self._font_family_cache[font_path] = family
        return QFont(family)
