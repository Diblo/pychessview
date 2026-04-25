# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Board layout model for the pychessview package."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from ...core.exceptions import LayoutError
from ...core.label_types import FileLabelSide, RankLabelSide
from ...core.primitives import SQUARES, File, Rank
from ...render.image_assets import ImageAsset
from ...render.items.color_square_item import ColorSquareItem
from ...render.items.image_square_item import ImageSquareItem
from ...render.items.label_item import LabelItem
from ..primitives import NULL_RECT, Color, HorizontalAlign, Rect, VerticalAlign
from .base import Layout

if TYPE_CHECKING:
    from typing import TypeAlias

    from ...core.primitives import Square
    from .base import CacheKey

BorderLabelConfig: TypeAlias = dict[FileLabelSide | RankLabelSide, int]
"""Type alias for border label index configuration maps."""

_BORDER_LABEL_CONFIG: BorderLabelConfig = {
    FileLabelSide.TOP: 0,
    RankLabelSide.RIGHT: -2,
    FileLabelSide.BOTTOM: -2,
    RankLabelSide.LEFT: 0,
}

_ROTATED_BORDER_LABEL_CONFIG: BorderLabelConfig = {
    FileLabelSide.TOP: -2,
    RankLabelSide.RIGHT: 0,
    FileLabelSide.BOTTOM: 0,
    RankLabelSide.LEFT: -2,
}

SquareLabelConfig: TypeAlias = dict[FileLabelSide | RankLabelSide, tuple[Rank | File, VerticalAlign, HorizontalAlign]]
"""Type alias for in-square label configuration maps."""

_SQUARE_LABEL_CONFIG: SquareLabelConfig = {
    FileLabelSide.TOP: (Rank.EIGHT, VerticalAlign.TOP, HorizontalAlign.RIGHT),
    RankLabelSide.RIGHT: (File.H, VerticalAlign.BOTTOM, HorizontalAlign.RIGHT),
    FileLabelSide.BOTTOM: (Rank.ONE, VerticalAlign.BOTTOM, HorizontalAlign.LEFT),
    RankLabelSide.LEFT: (File.A, VerticalAlign.TOP, HorizontalAlign.LEFT),
}

_ROTATED_SQUARE_LABEL_CONFIG: SquareLabelConfig = {
    FileLabelSide.TOP: (Rank.ONE, VerticalAlign.BOTTOM, HorizontalAlign.LEFT),
    RankLabelSide.RIGHT: (File.A, VerticalAlign.TOP, HorizontalAlign.LEFT),
    FileLabelSide.BOTTOM: (Rank.EIGHT, VerticalAlign.TOP, HorizontalAlign.RIGHT),
    RankLabelSide.LEFT: (File.H, VerticalAlign.BOTTOM, HorizontalAlign.RIGHT),
}

LabelMapKey: TypeAlias = tuple[FileLabelSide, File] | tuple[RankLabelSide, Rank]
"""Type alias for board edge label lookup keys."""

_LABEL_MAP: tuple[LabelMapKey, ...] = tuple((side, index) for index in File for side in FileLabelSide) + tuple(
    (side, index) for index in Rank for side in RankLabelSide
)


class BoardLayout(Layout):
    """Computed layout data for board and label rendering."""

    __slots__ = "_background_item", "_board_item", "_squares_item", "_square_items", "_label_items"

    _background_item: ColorSquareItem | None
    _board_item: ColorSquareItem
    _square_items: list[ImageSquareItem]
    _label_items: dict[LabelMapKey, LabelItem]

    def _initialization(self) -> None:
        """Initialize cached state for the layout."""
        self._background_item = None
        self._board_item = ColorSquareItem(Color(0, 0, 0), NULL_RECT)
        self._square_items = [ImageSquareItem(ImageAsset(".", 1, 1), NULL_RECT) for _ in SQUARES]
        self._label_items = {
            cast("LabelMapKey", (side, axis)): LabelItem(NULL_RECT, axis.text) for side, axis in _LABEL_MAP
        }

    def _rebuild(self) -> None:
        """Rebuild cached state for the current inputs."""
        geometry = self.geometry
        view_state = self.view_state
        theme = self.theme

        # Background item
        if geometry.viewport.width != geometry.viewport.height and not view_state.stretch_to_fit:
            self._background_item = ColorSquareItem(theme.background_fill, geometry.viewport.as_rect())
        else:
            self._background_item = None

        # Board item
        vertical_edges = geometry.vertical_edges
        horizontal_edges = geometry.horizontal_edges

        x = vertical_edges[0]
        y = horizontal_edges[0]
        self._board_item.rect = Rect(x, y, vertical_edges[-1] - x, horizontal_edges[-1] - y)
        self._board_item.color = theme.board_fill

        # Board item
        for square in SQUARES:
            item = self._square_items[square.index]
            item.rect = self.square_rects[square.index]

            if not view_state.white_at_bottom:
                square = square.rotated()

            if square.is_light():
                item.image_asset = theme.light_square_asset
            else:
                item.image_asset = theme.dark_square_asset

        if view_state.show_labels and any(view_state.label_side_visibility):
            if view_state.show_border:
                self._update_border_label_items()
            else:
                self._update_square_label_items()

    def _update_border_label_items(self) -> None:
        """Update cached border label items."""
        geometry = self.geometry
        view_state = self.view_state
        label_theme = self.theme.label

        margin = int(geometry.border_width * label_theme.border_margin_factor)
        double_margin = margin * 2
        if double_margin >= geometry.border_width:
            raise LayoutError(
                f"invalid factor: {label_theme.border_margin_factor}, results in margin_px={margin} "
                f"which is too large for border_width={geometry.border_width}"
            )

        label_size = geometry.border_width - double_margin
        if label_size < 1:
            raise LayoutError(
                f"invalid label_border_margin_factor: results in border label size {label_size} which is too small"
            )

        if view_state.rotate_labels and not view_state.white_at_bottom:
            label_config = _ROTATED_BORDER_LABEL_CONFIG
        else:
            label_config = _BORDER_LABEL_CONFIG

        for side in FileLabelSide:
            if not view_state.is_label_side_visible(side):
                continue
            for axis in File:
                file = axis if view_state.white_at_bottom else 7 - axis

                self._update_border_label_item(
                    self._label_items[(side, axis)],
                    Rect(
                        geometry.vertical_edges[file + 1] + margin,
                        geometry.horizontal_edges[label_config[side]] + margin,
                        geometry.file_sizes[file] - double_margin,
                        geometry.border_width - double_margin,
                    ),
                    label_size,
                )

        for side in RankLabelSide:
            if not view_state.is_label_side_visible(side):
                continue
            for axis in Rank:
                rank = 7 - axis if view_state.white_at_bottom else axis

                self._update_border_label_item(
                    self._label_items[(side, axis)],
                    Rect(
                        geometry.vertical_edges[label_config[side]] + margin,
                        geometry.horizontal_edges[rank + 1] + margin,
                        geometry.border_width - double_margin,
                        geometry.rank_sizes[rank] - double_margin,
                    ),
                    label_size,
                )

    def _update_border_label_item(self, item: LabelItem, rect: Rect, size: int) -> None:
        """Update a single border label item.

        Args:
            item: Render item involved in the operation.
            rect: Value supplied for ``rect``.
            size: Size value involved in the operation.
        """
        label_theme = self.theme.label

        item.rect = rect
        item.size = size
        item.color = label_theme.border_fill
        item.font = label_theme.border_font
        item.v_align = VerticalAlign.CENTER
        item.h_align = HorizontalAlign.CENTER

    def _update_square_label_items(self) -> None:
        """Update cached in-square label items."""
        geometry = self.geometry
        view_state = self.view_state
        label_theme = self.theme.label

        squares_width = geometry.vertical_edges[-2] - geometry.vertical_edges[1]
        squares_height = geometry.horizontal_edges[-2] - geometry.horizontal_edges[1]
        square_mean_dim = (squares_width + squares_height) / 16

        margin = int(square_mean_dim * label_theme.square_margin_factor)
        double_margin = margin * 2
        if double_margin >= square_mean_dim:
            raise LayoutError(
                f"invalid factor: {label_theme.square_margin_factor}, results in margin_px={margin} "
                f"which is too large for square_mean_dim={square_mean_dim}"
            )

        label_size = int((square_mean_dim - double_margin) * label_theme.square_factor)
        if label_size < 1:
            raise LayoutError(
                f"invalid label_square_factor: results in square label size {label_size} which is too small"
            )

        if view_state.rotate_labels and not view_state.white_at_bottom:
            label_config = _ROTATED_SQUARE_LABEL_CONFIG
        else:
            label_config = _SQUARE_LABEL_CONFIG

        for side in FileLabelSide:
            if not view_state.is_label_side_visible(side):
                continue
            anchor_axis, v_align, h_align = label_config[side]
            for axis in File:
                self._update_square_label_item(
                    self._label_items[(side, axis)],
                    axis if view_state.white_at_bottom else 7 - axis,
                    cast("Rank", anchor_axis),
                    margin,
                    label_size,
                    v_align,
                    h_align,
                )

        for side in RankLabelSide:
            if not view_state.is_label_side_visible(side):
                continue
            anchor_axis, v_align, h_align = label_config[side]
            for axis in Rank:
                self._update_square_label_item(
                    self._label_items[(side, axis)],
                    cast("File", anchor_axis),
                    7 - axis if view_state.white_at_bottom else axis,
                    margin,
                    label_size,
                    v_align,
                    h_align,
                )

    def _update_square_label_item(
        self,
        item: LabelItem,
        file: int,
        rank: int,
        margin: int,
        size: int,
        v_align: VerticalAlign,
        h_align: HorizontalAlign,
    ) -> None:
        """Update a single in-square label item.

        Args:
            item: Render item involved in the operation.
            file: Board file involved in the operation.
            rank: Integer value supplied for ``rank``.
            margin: Integer value supplied for ``margin``.
            size: Size value involved in the operation.
            v_align: Value supplied for ``v_align``.
            h_align: Value supplied for ``h_align``.
        """
        geometry = self.geometry
        label_theme = self.theme.label

        item.rect = Rect(
            geometry.vertical_edges[file + 1] + margin,
            geometry.horizontal_edges[rank + 1] + margin,
            geometry.file_sizes[file] - (2 * margin),
            geometry.rank_sizes[rank] - (2 * margin),
        )
        item.size = size
        item.color = label_theme.square_dark_fill if (file + rank) % 2 == 0 else label_theme.square_light_fill
        item.font = label_theme.square_font
        item.v_align = v_align
        item.h_align = h_align

    def _build_key(self) -> CacheKey:
        """Build the cache key for the current inputs.

        Returns:
            The cache key for the current inputs.
        """
        view_state = self.view_state
        theme = self.theme
        label_theme = theme.label

        key = (view_state.white_at_bottom, theme.board_fill, theme.light_square_asset, theme.dark_square_asset)

        show_labels = view_state.show_labels and any(view_state.label_side_visibility)
        if show_labels:
            if view_state.show_border:
                return key + (
                    view_state.rotate_labels,
                    view_state.label_side_visibility,
                    label_theme.border_fill,
                    label_theme.border_font,
                    label_theme.border_margin_factor,
                )
            return key + (
                view_state.rotate_labels,
                view_state.label_side_visibility,
                label_theme.square_light_fill,
                label_theme.square_dark_fill,
                label_theme.square_font,
                label_theme.square_margin_factor,
                label_theme.square_factor,
            )

        return key

    def background_item(self) -> ColorSquareItem | None:
        """Return the render item for the board background.

        Returns:
            The render item that draws the board background.
        """
        if self._background_item is None:
            return None
        return self._background_item.copy()

    def board_item(self) -> ColorSquareItem:
        """Return the render item for the board surface.

        Returns:
            The render item that draws the board surface.
        """
        return self._board_item.copy()

    def square_item(self, square: Square) -> ImageSquareItem:
        """Return the render item for an individual square.

        Args:
            square: Square whose board texture item should be returned.

        Returns:
            The render item that draws a single board square.
        """
        return self._square_items[square.index].copy()

    def label_item(self, side: FileLabelSide | RankLabelSide, axis: File | Rank) -> LabelItem:
        """Return the render item for a board edge label.

        Args:
            side: Board edge whose label should be returned.
            axis: File or rank value that determines the label text.

        Returns:
            The render item that draws one board edge label.
        """
        return self._label_items[cast("LabelMapKey", (side, axis))].copy()
