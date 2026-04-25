# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Highlight type definitions for the pychessview package."""

from enum import StrEnum


class HighlightPlayer(StrEnum):
    """Enumeration of players used when classifying highlights.

    Attributes:
        PLAYER: Highlight for the configured player.
        OPPONENT: Highlight for the opponent.
    """

    PLAYER = "player"
    OPPONENT = "opponent"


class HintStyle(StrEnum):
    """Enumeration of supported move-hint styles.

    Attributes:
        HINT: Standard move hint.
        OCCUPIED: Move hint for an occupied target square.
        PSEUDO_HINT: Pseudo-legal move hint.
        PSEUDO_OCCUPIED: Pseudo-legal hint for an occupied target square.
    """

    HINT = "hint"
    OCCUPIED = "occupied"
    PSEUDO_HINT = "pseudo_hint"
    PSEUDO_OCCUPIED = "pseudo_occupied"
