# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Annotation type definitions for the pychessview package."""

from enum import StrEnum


class CircleType(StrEnum):
    """Enumeration of supported circle annotation styles.

    Attributes:
        PRIMARY: Primary annotation variant.
        SECONDARY: Secondary annotation variant.
        ALTERNATIVE: Alternative annotation variant.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
    ALTERNATIVE = "alternative"


class ArrowType(StrEnum):
    """Enumeration of supported arrow annotation styles.

    Attributes:
        PRIMARY: Primary annotation variant.
        SECONDARY: Secondary annotation variant.
        ALTERNATIVE: Alternative annotation variant.
    """

    PRIMARY = "primary"
    SECONDARY = "secondary"
    ALTERNATIVE = "alternative"


class HintArrowType(StrEnum):
    """Enumeration of supported hint arrow styles.

    Attributes:
        PRIMARY: Primary annotation variant.
        SECONDARY: Secondary annotation variant.
        ALTERNATIVE: Alternative annotation variant.
    """

    PRIMARY = "hint primary"
    SECONDARY = "hint secondary"
    ALTERNATIVE = "hint alternative"
