# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for label side enums."""

import pytest

from pychessview.engine.core.label_types import FileLabelSide, RankLabelSide

pytestmark = pytest.mark.unit


def test_label_side_values_match_view_state_visibility_keys() -> None:
    """Keep file and rank label side values stable for view-state visibility.

    Label visibility is configured by side names. These enum values must remain
    the canonical strings used by view settings and board label layout.
    """
    assert FileLabelSide.TOP.value == "top"
    assert FileLabelSide.BOTTOM.value == "bottom"
    assert RankLabelSide.RIGHT.value == "right"
    assert RankLabelSide.LEFT.value == "left"
