# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for theme setting loaders."""

from pathlib import Path

import pytest

from pychessview.engine.core.exceptions import ThemeError, ThemeParseError
from pychessview.engine.layout.primitives import Color
from pychessview.engine.theme.loaders import (
    get_theme_setting,
    get_theme_setting_color,
    get_theme_setting_float,
    get_theme_setting_path,
    get_theme_setting_str,
    is_color_mapping,
    is_int,
    is_mapping,
    is_number,
    is_str_key_mapping,
    load_setting_data,
    validate_factor,
    validate_instance,
)

pytestmark = pytest.mark.unit


def test_theme_type_guards_reject_bool_values_for_numbers() -> None:
    """Keep YAML bool values from being accepted as numeric theme settings.

    Python treats ``bool`` as a subclass of ``int``. Theme validation must not
    allow that shortcut for sizes, factors, or color channels.
    """
    assert is_int(1) is True
    assert is_int(True) is False
    assert is_number(1.25) is True
    assert is_number(False) is False
    assert is_mapping({"a": 1}) is True
    assert is_str_key_mapping({"a": 1}) is True
    assert is_str_key_mapping({1: "a"}) is False


def test_theme_color_mapping_requires_rgb_channels_in_range() -> None:
    """Accept only complete RGB or RGBA mappings with byte-range channels.

    Theme colors are converted directly to ``Color`` objects, so partial or
    out-of-range mappings must fail before rendering uses them.
    """
    assert is_color_mapping({"r": 1, "g": 2, "b": 3}) is True
    assert is_color_mapping({"r": 1, "g": 2, "b": 3, "a": 4}) is True
    assert is_color_mapping({"r": 1, "g": 2}) is False
    assert is_color_mapping({"r": 1, "g": 2, "b": 999}) is False
    assert is_color_mapping({"r": 1, "g": 2, "b": True}) is False


def test_theme_setting_getters_return_typed_nested_values() -> None:
    """Resolve dotted theme paths and convert values through strict getters.

    Loader functions are the boundary between YAML mappings and typed theme
    objects, so they must fail on missing or wrongly typed values.
    """
    data = {
        "board": {
            "factor": 0.5,
            "name": "default",
            "asset": "pyproject.toml",
            "fill": {"r": 1, "g": 2, "b": 3, "a": 4},
        }
    }

    assert get_theme_setting(data, "board.name") == "default"
    assert get_theme_setting(data, "board.missing") is None
    assert get_theme_setting_str(data, "board.name") == "default"
    assert get_theme_setting_float(data, "board.factor") == 0.5
    assert get_theme_setting_color(data, "board.fill") == Color(1, 2, 3, 4)
    assert get_theme_setting_path(data, "board.asset", Path(".")) == Path("pyproject.toml").resolve()


def test_theme_setting_getters_raise_parse_errors_for_invalid_values() -> None:
    """Report parse errors close to the invalid setting path.

    Invalid theme input should identify the missing or malformed key before any
    theme object is partially constructed.
    """
    data = {"board": {"name": 42, "factor": "wide", "fill": {"r": 1}, "asset": "missing.svg"}}

    with pytest.raises(ThemeParseError, match="missing key 'board.missing'"):
        get_theme_setting_str(data, "board.missing")
    with pytest.raises(ThemeParseError, match="'board.name' must be a string"):
        get_theme_setting_str(data, "board.name")
    with pytest.raises(ThemeParseError, match="'board.factor' must be a number"):
        get_theme_setting_float(data, "board.factor")
    with pytest.raises(ThemeParseError, match="'board.fill' must be a mapping representing a color"):
        get_theme_setting_color(data, "board.fill")
    with pytest.raises(ThemeParseError, match="points to missing file"):
        get_theme_setting_path(data, "board.asset", Path("."))


def test_theme_file_loading_returns_mapping_for_builtin_settings() -> None:
    """Load built-in YAML settings as a top-level mapping.

    Theme loading expects dotted path lookup against a dictionary-like object;
    this protects the package settings file used by the default theme.
    """
    settings = Path("src/pychessview/assets/themes/default/settings.yaml")

    data = load_setting_data(settings)

    assert "board" in data


def test_theme_validation_helpers_raise_clear_errors() -> None:
    """Reject values that violate runtime type or factor bounds.

    Theme object constructors use these helpers to keep all factors inside the
    ranges supported by layout and rendering code.
    """
    assert validate_factor("piece factor", 1, 0.5, 1.2) == 1.0
    validate_instance("font.ttf", str, "font path")

    with pytest.raises(ThemeError, match="within"):
        validate_factor("piece factor", 2.0, 0.5, 1.2)
    with pytest.raises(ThemeError, match="Expected font path"):
        validate_instance(42, str, "font path")
