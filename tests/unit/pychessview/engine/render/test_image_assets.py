# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for render image assets."""

import os
from copy import copy
from pathlib import Path

import pytest

from pychessview.engine.render.image_assets import ImageAsset

pytestmark = pytest.mark.unit


def test_image_asset_behaves_as_path_with_dimensions() -> None:
    """Store asset path and dimensions while remaining path-like.

    Theme loading creates image assets that renderers can pass to filesystem
    APIs through ``os.fspath`` without losing the measured image dimensions.
    """
    asset = ImageAsset(Path("pieces/king.svg"), 64, 32)

    assert asset.path == Path("pieces/king.svg")
    assert asset.width == 64
    assert asset.height == 32
    assert str(asset) == "pieces/king.svg"
    assert os.fspath(asset) == os.fspath(Path("pieces/king.svg"))
    assert repr(asset) == "ImageAsset(path='pieces/king.svg', width=64, height=32)"
    assert copy(asset) == asset
