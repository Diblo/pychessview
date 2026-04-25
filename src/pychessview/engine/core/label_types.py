# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Label placement and visibility definitions for the pychessview package."""

from enum import StrEnum


class FileLabelSide(StrEnum):
    """Enumeration of supported file label positions.

    Attributes:
        TOP: Top alignment or label side.
        BOTTOM: Bottom alignment or label side.
    """

    TOP = "top"
    BOTTOM = "bottom"


class RankLabelSide(StrEnum):
    """Enumeration of supported rank label positions.

    Attributes:
        RIGHT: Right alignment or label side.
        LEFT: Left alignment or label side.
    """

    RIGHT = "right"
    LEFT = "left"
