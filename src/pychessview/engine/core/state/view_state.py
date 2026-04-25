# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""View state container for the pychessview package."""

from ..label_types import FileLabelSide, RankLabelSide
from ..primitives import PlayerColor
from .base import State


class ViewState(State):
    """Stores board presentation and interaction settings.

    Attributes:
        player: Player color used by the view state.
        restrict_to_player_pieces: Whether selection is limited to the configured player pieces.
        restrict_to_select_opponent_pieces: Whether opponent-piece selection is restricted.
        show_player_hints: Whether hints for the configured player are shown.
        show_opponent_hints: Whether hints for the opponent are shown.
        annotations_enabled: Whether annotation interactions are enabled.
        show_border: Whether the board border is rendered.
        stretch_to_fit: Whether the board stretches to fill the viewport.
        white_at_bottom: Whether white is rendered at the bottom of the board.
        show_labels: Whether board labels are rendered.
        rotate_labels: Whether labels rotate with board orientation.
    """

    __slots__ = (
        "_player",
        "restrict_to_player_pieces",
        "restrict_to_select_opponent_pieces",
        "show_player_hints",
        "show_opponent_hints",
        "annotations_enabled",
        "show_border",
        "stretch_to_fit",
        "white_at_bottom",
        "show_labels",
        "rotate_labels",
        "_label_side_visibility",
    )

    _player: PlayerColor
    restrict_to_player_pieces: bool
    restrict_to_select_opponent_pieces: bool
    show_player_hints: bool
    show_opponent_hints: bool
    annotations_enabled: bool
    show_border: bool
    stretch_to_fit: bool
    white_at_bottom: bool
    show_labels: bool
    rotate_labels: bool
    _label_side_visibility: tuple[bool, bool, bool, bool]

    def __init__(
        self,
        player: PlayerColor,
        restrict_to_player_pieces: bool = True,
        restrict_to_select_opponent_pieces: bool = False,
        show_player_hints: bool = True,
        show_opponent_hints: bool = True,
        annotations_enabled: bool = True,
        show_border: bool = True,
        stretch_to_fit: bool = False,
        white_at_bottom: bool = True,
        show_labels: bool = True,
        rotate_labels: bool = False,
        label_side_visibility: tuple[bool, bool, bool, bool] = (False, False, True, True),
    ) -> None:
        """Initialize the view state with its initial configuration.

        Args:
            player: Value used to initialize ``player``.
            restrict_to_player_pieces: Value used to initialize ``restrict_to_player_pieces``.
            restrict_to_select_opponent_pieces: Value used to initialize ``restrict_to_select_opponent_pieces``.
            show_player_hints: Value used to initialize ``show_player_hints``.
            show_opponent_hints: Value used to initialize ``show_opponent_hints``.
            annotations_enabled: Value used to initialize ``annotations_enabled``.
            show_border: Value used to initialize ``show_border``.
            stretch_to_fit: Value used to initialize ``stretch_to_fit``.
            white_at_bottom: Value used to initialize ``white_at_bottom``.
            show_labels: Value used to initialize ``show_labels``.
            rotate_labels: Value used to initialize ``rotate_labels``.
            label_side_visibility: Value used to initialize ``label_side_visibility``.
        """
        self._player = player
        self.restrict_to_player_pieces = restrict_to_player_pieces
        self.restrict_to_select_opponent_pieces = restrict_to_select_opponent_pieces
        self.show_player_hints = show_player_hints
        self.show_opponent_hints = show_opponent_hints
        self.annotations_enabled = annotations_enabled
        self.show_border = show_border
        self.stretch_to_fit = stretch_to_fit
        self.white_at_bottom = white_at_bottom
        self.show_labels = show_labels
        self.rotate_labels = rotate_labels
        self._label_side_visibility = label_side_visibility

        self._sync_board_direction()

    @property
    def player(self) -> PlayerColor:
        """Player color used for board orientation and interaction defaults.

        Returns:
            Player color used by the view state.
        """
        return self._player

    @player.setter
    def player(self, player: PlayerColor) -> None:
        """Set the player color and synchronize board orientation.

        Args:
            player: Player color to store.
        """
        self._player = player
        self._sync_board_direction()

    def _sync_board_direction(self) -> None:
        """Synchronize the board direction with the configured player color."""
        if self._player is PlayerColor.WHITE:
            self.white_at_bottom = True
        else:
            self.white_at_bottom = False

    @property
    def label_side_visibility(self) -> tuple[bool, bool, bool, bool]:
        """Visibility flags for top, right, bottom, and left labels.

        Returns:
            Visibility flags for top, right, bottom, and left labels.
        """
        return self._label_side_visibility

    def set_sides_visibility(
        self, *, top: bool | None, right: bool | None, bottom: bool | None, left: bool | None
    ) -> None:
        """Update label visibility flags for one or more board edges.

        Args:
            top: New visibility for top file labels, or ``None`` to keep the current value.
            right: New visibility for right rank labels, or ``None`` to keep the current value.
            bottom: New visibility for bottom file labels, or ``None`` to keep the current value.
            left: New visibility for left rank labels, or ``None`` to keep the current value.
        """
        self._label_side_visibility = (
            top if top is not None else self._label_side_visibility[0],
            right if right is not None else self._label_side_visibility[1],
            bottom if bottom is not None else self._label_side_visibility[2],
            left if left is not None else self._label_side_visibility[3],
        )

    def set_side_visibility(self, side: FileLabelSide | RankLabelSide, enabled: bool) -> None:
        """Set label visibility for a single board side.

        Args:
            side: Board edge whose label visibility should be updated.
            enabled: Whether labels on ``side`` should be shown.
        """
        self._label_side_visibility = (
            enabled if side == FileLabelSide.TOP else self._label_side_visibility[0],
            enabled if side == RankLabelSide.RIGHT else self._label_side_visibility[1],
            enabled if side == FileLabelSide.BOTTOM else self._label_side_visibility[2],
            enabled if side == RankLabelSide.LEFT else self._label_side_visibility[3],
        )

    def is_label_side_visible(self, side: FileLabelSide | RankLabelSide) -> bool:
        """Return whether labels are visible on the requested board edge.

        Args:
            side: Board edge whose label visibility should be queried.

        Returns:
            ``True`` when labels for ``side`` are currently enabled.
        """
        if side == FileLabelSide.TOP:
            return self._label_side_visibility[0]
        if side == RankLabelSide.RIGHT:
            return self._label_side_visibility[1]
        if side == FileLabelSide.BOTTOM:
            return self._label_side_visibility[2]
        return self._label_side_visibility[3]
