# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for QtRenderer drawing contracts."""

from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication

from pychessview.engine.layout.primitives import Color, Coord, HorizontalAlign, Rect, VerticalAlign, Viewport
from pychessview.engine.render.image_assets import ImageAsset
from pychessview.engine.render.items.arrow_item import ArrowItem
from pychessview.engine.render.items.circle_item import CircleItem
from pychessview.engine.render.items.color_square_item import ColorSquareItem
from pychessview.engine.render.items.image_square_item import ImageSquareItem
from pychessview.engine.render.items.label_item import LabelItem
from pychessview.qt.renderer.qt_renderer import (
    QtRenderer,
    _align_offset,  # pyright: ignore[reportPrivateUsage]
    _build_arrow_geometry,  # pyright: ignore[reportPrivateUsage]
)

from .._helpers import SpyRenderer, image_has_visible_pixel

pytestmark = [pytest.mark.unit, pytest.mark.requires_qt]


def test_align_offset_handles_edges_center_and_oversized_content() -> None:
    """Calculate image/text offsets for edge alignment, centering, and oversized content.

    Oversized content is clamped to the origin so the renderer does not produce
    negative offsets when the content is larger than the available span.
    """
    assert _align_offset(HorizontalAlign.LEFT, 100.0, 20.0) == 0.0
    assert _align_offset(HorizontalAlign.CENTER, 100.0, 20.0) == 40.0
    assert _align_offset(HorizontalAlign.RIGHT, 100.0, 20.0) == 80.0
    assert _align_offset(VerticalAlign.BOTTOM, 100.0, 20.0) == 80.0
    assert _align_offset(HorizontalAlign.CENTER, 10.0, 20.0) == 0.0


def test_build_arrow_geometry_returns_tail_shaft_and_head_paths() -> None:
    """Build the three drawable path components for an arrow item.

    The renderer draws arrows as separate tail cap, shaft, and head paths; this
    test protects the geometry helper from returning empty paths for a normal
    diagonal arrow.
    """
    tail_cap_path, shaft_path, head_path = _build_arrow_geometry(
        ArrowItem(12, 24, 18),
        (Coord(10, 10), Coord(80, 50)),
    )

    assert tail_cap_path.isEmpty() is False
    assert shaft_path.isEmpty() is False
    assert head_path.isEmpty() is False


def test_qt_renderer_requires_painter_before_frame() -> None:
    """Reject frame rendering when no active Qt painter has been installed.

    ``QtRenderer`` depends on the widget paint event to provide a painter before
    rendering begins, so calling ``begin_frame`` directly fails with a clear
    runtime error instead of silently doing nothing.
    """
    renderer = QtRenderer()

    with pytest.raises(RuntimeError, match="QtRenderer painter is not set"):
        renderer.begin_frame(Viewport(0, 0, 10, 10))


def test_set_painter_installs_painter_used_by_frame_setup() -> None:
    """Install the painter that frame initialization configures.

    ``begin_frame`` configures render hints on the active painter. The test uses
    those hints as the observable contract that ``set_painter`` stored the
    painter used for subsequent rendering.
    """
    image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
    painter = QPainter(image)
    renderer = QtRenderer()

    try:
        renderer.set_painter(painter)
        renderer.begin_frame(Viewport(0, 0, 32, 32))
        render_hints = painter.renderHints()
    finally:
        painter.end()

    assert render_hints & QPainter.RenderHint.Antialiasing
    assert render_hints & QPainter.RenderHint.TextAntialiasing
    assert render_hints & QPainter.RenderHint.SmoothPixmapTransform


def test_draw_square_color_fills_the_requested_rectangle() -> None:
    """Paint solid square items with the requested color inside the target rectangle.

    The renderer should translate the core color and rectangle primitives into
    Qt drawing commands without needing external assets or renderer-owned
    painter lifetime.
    """
    image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer = QtRenderer()
    renderer.set_painter(painter)

    try:
        renderer.draw_square_color(ColorSquareItem(Color(10, 20, 30, 255), Rect(4, 5, 20, 20)))
    finally:
        painter.end()

    pixel = image.pixelColor(10, 10)
    assert (pixel.red(), pixel.green(), pixel.blue(), pixel.alpha()) == (10, 20, 30, 255)


def test_draw_circle_strokes_visible_geometry_without_owning_the_painter() -> None:
    """Stroke circle geometry on the caller-provided painter.

    Annotation circles are drawn by the renderer but painter ownership remains
    with the widget. A visible output check protects the drawing contract
    without depending on exact antialiasing pixels.
    """
    image = QImage(48, 48, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer = QtRenderer()
    renderer.set_painter(painter)

    try:
        renderer.draw_circle(CircleItem(4, Rect(8, 8, 32, 32)), Color(200, 30, 40, 255))
    finally:
        painter.end()

    assert image_has_visible_pixel(image)


def test_draw_arrow_fills_visible_arrow_geometry() -> None:
    """Paint arrow geometry from core arrow items and resolved endpoints.

    Arrow rendering combines tail, shaft, and head paths into visible output.
    The test protects that public drawing method without asserting fragile
    pixel-perfect geometry.
    """
    image = QImage(96, 96, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer = QtRenderer()
    renderer.set_painter(painter)

    try:
        renderer.draw_arrow(ArrowItem(8, 18, 22), Color(20, 120, 220, 255), (Coord(12, 12), Coord(80, 70)))
    finally:
        painter.end()

    assert image_has_visible_pixel(image)


def test_draw_text_ink_paints_label_text_with_the_resolved_font(
    monkeypatch: pytest.MonkeyPatch,
    qapp: QApplication,
) -> None:
    """Paint label text through Qt after font resolution succeeds.

    Font-file registration is covered by the private font helper; this public
    method test replaces font resolution so it can focus on label layout and
    drawing without depending on platform font files.
    """
    _ = qapp
    image = QImage(96, 48, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer = QtRenderer()
    renderer.set_painter(painter)

    monkeypatch.setattr(QtRenderer, "_ensure_font_family", lambda self, font_path: QFont())  # type: ignore

    try:
        renderer.draw_text_ink(
            LabelItem(
                Rect(0, 0, 96, 48),
                "A1",
                Color(0, 0, 0, 255),
                18,
                h_align=HorizontalAlign.CENTER,
                v_align=VerticalAlign.CENTER,
            )
        )
    finally:
        painter.end()

    assert image_has_visible_pixel(image)


def test_end_frame_does_not_close_or_clear_the_active_painter() -> None:
    """Leave painter lifetime under the caller's control during frame finalization.

    The widget owns ``QPainter.end()``. ``QtRenderer.end_frame`` is therefore
    expected to be safe to call without ending the painter or preventing later
    drawing on the same painter.
    """
    image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer = QtRenderer()
    renderer.set_painter(painter)

    try:
        renderer.end_frame()
        assert painter.isActive()
        renderer.draw_square_color(ColorSquareItem(Color(40, 50, 60, 255), Rect(0, 0, 10, 10)))
    finally:
        painter.end()

    assert image_has_visible_pixel(image)


def test_draw_square_image_dispatches_svg_and_raster_assets() -> None:
    """Dispatch square image drawing to SVG or raster-specific rendering paths.

    Asset file extensions determine whether ``QtRenderer`` uses the SVG path or
    raster path. The spy renderer records both branches without requiring real
    asset files on disk.
    """
    image = QImage(32, 32, QImage.Format.Format_ARGB32_Premultiplied)
    painter = QPainter(image)
    renderer = SpyRenderer()
    renderer.set_painter(painter)

    try:
        renderer.draw_square_image(ImageSquareItem(ImageAsset("piece.svg", 200, 100), Rect(0, 0, 100, 100)))
        renderer.draw_square_image(ImageSquareItem(ImageAsset("piece.png", 100, 200), Rect(0, 0, 100, 100)))
    finally:
        painter.end()

    assert renderer.svg_calls == [(Path("piece.svg"), (0.0, 0.0, 100.0, 100.0))]
    assert renderer.raster_calls == [(Path("piece.png"), (0.0, 0.0, 100.0, 100.0))]
