# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Mouse button definitions for the pychessview package."""

from enum import Enum


class MouseButton(Enum):
    """Enumeration of supported pointer buttons.

    Attributes:
        LEFT: Primary mouse button used for normal board interaction.
        RIGHT: Secondary mouse button used for annotation deletion.
    """

    LEFT = "left"
    RIGHT = "right"
