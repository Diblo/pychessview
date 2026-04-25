# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0
# pyright: reportPrivateUsage=false

"""Unit tests for development command helpers."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest
from packaging.version import Version
from tools import devtools

pytestmark = pytest.mark.unit


def _patch_git_tags(monkeypatch: pytest.MonkeyPatch, stdout: str, *, returncode: int = 0) -> None:
    """Replace the git tag subprocess call with deterministic output."""

    def fake_run(
        command: Sequence[str], *, check: bool, capture_output: bool, text: bool, cwd: Path
    ) -> subprocess.CompletedProcess[str]:
        assert tuple(command) == ("git", "tag", "--list", "v*")
        assert check is False
        assert capture_output is True
        assert text is True
        assert cwd == devtools.PROJECT_ROOT
        return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(devtools.subprocess, "run", fake_run)


def test_get_git_tag_version_returns_latest_release_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Select the highest parsed release version from all repository tags.

    Publish validation must compare package metadata against the latest release
    tag rather than whichever tag happens to be attached to ``HEAD``.
    """
    _patch_git_tags(monkeypatch, "v1.0.0\nv1.2.0rc1\nv1.1.0\nv1.2.0\n")

    assert devtools._get_git_tag_version() == Version("1.2.0")


def test_get_git_tag_version_returns_none_without_release_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return no version when the repository has no release tags.

    Publish validation handles the missing-tag error separately, so the tag
    lookup should keep the absence of matching tags distinct from git failures.
    """
    _patch_git_tags(monkeypatch, "")

    assert devtools._get_git_tag_version() is None


def test_get_git_tag_version_rejects_invalid_release_tags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject tags that look like release tags but contain invalid versions.

    Invalid release-style tags should fail loudly because silently ignoring them
    can make the latest publish candidate ambiguous.
    """
    _patch_git_tags(monkeypatch, "v1.0.0\nvnot-a-version\n")

    with pytest.raises(RuntimeError, match="Invalid version"):
        devtools._get_git_tag_version()
