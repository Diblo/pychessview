# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the null game factory."""

import pytest

from pychessview.engine.core.domain.adapters.null_game_adapter import NullGameAdapter
from pychessview.engine.factory.null_game import (
    NullControllerFactory,
    NullGameAdapterFactory,
    NullGameFactory,
    NullThemeProvider,
)

pytestmark = pytest.mark.unit


def test_null_game_factory_builds_spec_with_null_runtime_parts() -> None:
    """Create a game spec that keeps rules and controller behavior inert.

    The null factory is useful for lightweight rendering and tests because it
    wires a null adapter and null controller without promotion options.
    """
    spec = NullGameFactory.create_game_spec("custom fen")

    assert spec.definition.default_fen == "custom fen"
    assert spec.definition.white_promotion_pieces == ()
    assert spec.definition.black_promotion_pieces == ()
    assert isinstance(spec.theme_provider, NullThemeProvider)
    assert isinstance(spec.adapter_factory, NullGameAdapterFactory)
    assert isinstance(spec.controller_factory, NullControllerFactory)
    adapter = spec.adapter_factory.create_game_adapter()
    assert isinstance(adapter, NullGameAdapter)
    assert adapter.default_fen == "custom fen"
