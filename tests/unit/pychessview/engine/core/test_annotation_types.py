# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for annotation type enums."""

import pytest

from pychessview.engine.core.annotation_types import ArrowType, CircleType, HintArrowType

pytestmark = pytest.mark.unit


def test_annotation_type_values_match_theme_keys() -> None:
    """Keep annotation enum values aligned with theme configuration keys.

    Annotation state and theme lookup both use these string values. Changing a
    value would disconnect stored annotations from their configured colors.
    """
    assert [member.value for member in CircleType] == ["primary", "secondary", "alternative"]
    assert [member.value for member in ArrowType] == ["primary", "secondary", "alternative"]
    assert [member.value for member in HintArrowType] == ["hint primary", "hint secondary", "hint alternative"]
