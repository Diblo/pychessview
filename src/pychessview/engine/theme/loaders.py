# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Theme setting loaders and validators for the pychessview package."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import yaml
from imagesize import imagesize

from ..core.exceptions import ThemeError, ThemeParseError
from ..layout.primitives import Color
from ..render.image_assets import ImageAsset

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any, TypeGuard

    from ..layout.primitives import ColorMapping


def build_image_asset(path: Path) -> ImageAsset:
    """Build an image asset using the file's intrinsic dimensions.

    Args:
        path: Filesystem path to the image file.

    Returns:
        Image asset built from ``path`` using the file's intrinsic dimensions.
    """
    return ImageAsset(path, *imagesize.get(path))


def validate_instance(value: object, expected_type: type[object] | tuple[type[object], ...], name: str) -> None:
    """Validate that a value matches an expected runtime type.

    Args:
        value: Value to validate or inspect.
        expected_type: Runtime type or types that the value must match.
        name: Name used by the operation or in error messages.
    """
    if not isinstance(value, expected_type):
        if isinstance(expected_type, tuple):
            expected_name = ", ".join(type_.__name__ for type_ in expected_type)
        else:
            expected_name = expected_type.__name__
        raise ThemeError(f"Expected {name} to be {expected_name}, got {type(value).__name__}")


def validate_factor(name: str, factor: float | int, min_val: float, max_val: float) -> float:
    """Normalize and validate a numeric factor within bounds.

    Args:
        name: Name used by the operation or in error messages.
        factor: Numeric factor to validate.
        min_val: Exclusive lower bound for the accepted value.
        max_val: Inclusive upper bound for the accepted value.

    Returns:
        Numeric factor converted to ``float`` and validated against the accepted bounds.
    """
    if not isinstance(factor, float):
        factor = float(factor)

    if not min_val < factor <= max_val:
        raise ThemeError(f"The {name} must be within ({min_val}, {max_val}], got {factor}")

    return factor


def is_int(value: Any) -> TypeGuard[int]:
    """Return whether a value is a non-boolean integer.

    Args:
        value: Value to validate or inspect.

    Returns:
        ``True`` when a value is a non-boolean integer; otherwise, ``False``.
    """
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value: Any) -> TypeGuard[int | float]:
    """Return whether a value is a non-boolean number.

    Args:
        value: Value to validate or inspect.

    Returns:
        ``True`` when a value is a non-boolean number; otherwise, ``False``.
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_mapping(value: Any) -> TypeGuard[Mapping[Any, Any]]:
    """Return whether a value implements the mapping protocol.

    Args:
        value: Value to validate or inspect.

    Returns:
        ``True`` when a value implements the mapping protocol; otherwise, ``False``.
    """
    if not isinstance(value, Mapping):
        return False
    return True


def is_str_key_mapping(value: Any) -> TypeGuard[Mapping[str, Any]]:
    """Return whether a value is a mapping with string keys.

    Args:
        value: Value to validate or inspect.

    Returns:
        ``True`` when a value is a mapping with string keys; otherwise, ``False``.
    """
    if not is_mapping(value) or any(not isinstance(key, str) for key in value.keys()):
        return False
    return True


def is_color_mapping(value: Any) -> TypeGuard[ColorMapping]:
    """Return whether a value is a valid RGBA mapping.

    Args:
        value: Value to validate or inspect.

    Returns:
        ``True`` when a value is a valid RGBA mapping; otherwise, ``False``.
    """
    if not is_str_key_mapping(value):
        return False

    for key in ("r", "g", "b"):
        if key not in value or not is_int(value[key]) or not 0 <= value[key] <= 255:
            return False

    if "a" in value and (not is_int(value["a"]) or not 0 <= value["a"] <= 255):
        return False

    return True


def load_setting_data(path: Path) -> Mapping[str, Any]:
    """Load and validate theme setting data from disk.

    Args:
        path: Filesystem path to the theme settings file.

    Returns:
        Top-level theme settings mapping loaded from ``path``.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ThemeParseError(f"invalid YAML in '{path}': {exc}") from exc

    if not is_str_key_mapping(data):
        raise ThemeParseError("theme YAML must be a mapping at the top level")

    return data


def get_theme_setting(data: Mapping[str, Any], path: str) -> object | None:
    """Return a nested theme setting by dotted path.

    Args:
        data: Theme settings mapping to read from.
        path: Dotted path to the requested theme setting.

    Returns:
        Theme setting value stored at ``path``, or ``None`` when the path is missing.
    """
    current: object = data
    for key in path.split("."):
        if not is_str_key_mapping(current) or key not in current:
            return None
        current = current[key]
    return current


def get_theme_setting_str(data: Mapping[str, Any], path: str) -> str:
    """Return a required string theme setting.

    Args:
        data: Theme settings mapping to read from.
        path: Dotted path to the requested theme setting.

    Returns:
        String theme setting stored at ``path``.
    """
    value = get_theme_setting(data, path)
    if value is None:
        raise ThemeParseError(f"missing key '{path}'")
    if not isinstance(value, str):
        raise ThemeParseError(f"'{path}' must be a string")
    return value


def get_theme_setting_float(data: Mapping[str, Any], path: str) -> float:
    """Return a required numeric theme setting as a float.

    Args:
        data: Theme settings mapping to read from.
        path: Dotted path to the requested theme setting.

    Returns:
        Numeric theme setting stored at ``path`` as a float.
    """
    value = get_theme_setting(data, path)
    if value is None:
        raise ThemeParseError(f"missing key '{path}'")
    if not is_number(value):
        raise ThemeParseError(f"'{path}' must be a number")
    return float(value)


def get_theme_setting_color(data: Mapping[str, Any], path: str) -> Color:
    """Return a required color theme setting.

    Args:
        data: Theme settings mapping to read from.
        path: Dotted path to the requested theme setting.

    Returns:
        Color theme setting stored at ``path``.
    """
    value = get_theme_setting(data, path)
    if value is None:
        raise ThemeParseError(f"missing key '{path}'")
    if not is_color_mapping(value):
        raise ThemeParseError(f"'{path}' must be a mapping representing a color")
    return Color.from_mapping(value)


def get_theme_setting_path(data: Mapping[str, Any], path: str, root: Path) -> Path:
    """Return a required theme file path resolved against a root directory.

    Args:
        data: Theme settings mapping to read from.
        path: Dotted path to the requested theme setting.
        root: Root directory used to resolve relative paths.

    Returns:
        Resolved filesystem path stored at ``path``.
    """
    path_value = get_theme_setting_str(data, path)
    if not path_value:
        raise ThemeParseError(f"'{path}' cannot be empty")

    resolved = (root / path_value).resolve()
    if not resolved.is_file():
        raise ThemeParseError(f"'{path}' points to missing file '{resolved}'")

    return resolved
