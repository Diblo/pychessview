# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Modifiers definitions for the pychessview package."""

from enum import Enum


class Modifier(Enum):
    """Enumeration of supported keyboard modifiers.

    Attributes:
        SHIFT: Shift keyboard modifier.
        CTRL: Control keyboard modifier.
        ALT: Alt keyboard modifier.
    """

    SHIFT = "shift"
    CTRL = "ctrl"
    ALT = "alt"
