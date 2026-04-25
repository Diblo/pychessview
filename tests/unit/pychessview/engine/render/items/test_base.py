# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the base render item type."""

import pytest

from pychessview.engine.render.items.base import Item

pytestmark = pytest.mark.unit


def test_item_base_can_be_instantiated_by_minimal_render_items() -> None:
    """Keep the base item as a lightweight common marker.

    Concrete render items inherit from this class, so it must remain safe as a
    minimal base without constructor requirements.
    """
    assert isinstance(Item(), Item)
