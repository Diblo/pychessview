# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Highlight theme name definitions for the pychessview package."""

from enum import StrEnum


class HighlightThemeName(StrEnum):
    """Enumeration of highlight asset names.

    Attributes:
        LAST_MOVE: Highlight asset for the last move.
        CHECK: Highlight asset for a checked king.
        SELECTED: Highlight asset for the selected square.
        OPPONENT_SELECTED: Highlight asset for an opponent-selected square.
        HINT: Standard move hint.
        PSEUDO_HINT: Pseudo-legal move hint.
        OPPONENT_HINT: Highlight asset for an opponent hint.
        OPPONENT_PSEUDO_HINT: Highlight asset for an opponent pseudo hint.
        HINT_OCCUPIED: Highlight asset for an occupied hint target.
        PSEUDO_HINT_OCCUPIED: Highlight asset for an occupied pseudo hint target.
        OPPONENT_HINT_OCCUPIED: Highlight asset for an occupied opponent hint target.
        OPPONENT_PSEUDO_HINT_OCCUPIED: Highlight asset for an occupied opponent pseudo hint target.
    """

    LAST_MOVE = "last_move"
    CHECK = "check"
    SELECTED = "selected"
    OPPONENT_SELECTED = "opponent_selected"
    HINT = "hint"
    PSEUDO_HINT = "pseudo_hint"
    OPPONENT_HINT = "opponent_hint"
    OPPONENT_PSEUDO_HINT = "opponent_pseudo_hint"
    HINT_OCCUPIED = "hint_occupied"
    PSEUDO_HINT_OCCUPIED = "pseudo_hint_occupied"
    OPPONENT_HINT_OCCUPIED = "opponent_hint_occupied"
    OPPONENT_PSEUDO_HINT_OCCUPIED = "opponent_pseudo_hint_occupied"
