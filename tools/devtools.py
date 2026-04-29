# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Development command helpers for the pychessview workspace."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeGuard

if TYPE_CHECKING:
    from packaging.version import Version as PackagingVersion

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
"""Repository root directory used as the default command working directory."""

PACKAGE_NAME: str = "pychessview"
"""Published PyPI package name."""


class ModuleInfo:
    """Workspace module metadata."""

    def __init__(self, name: str, extra: str | None = None) -> None:
        """Initialize module metadata.

        Args:
            name: Module name used in the test directory layout.
            extra: Optional package extra used to install module-specific dependencies.
        """
        self.name = name
        self._extra = extra or ""

    @property
    def extra(self) -> str:
        """Return the extras selector for this module."""
        return self._extra

    @property
    def unit_test_path(self) -> Path:
        """Return the module unit test directory."""
        return PROJECT_ROOT / "tests" / "unit" / "pychessview" / self.name

    @property
    def integration_test_path(self) -> Path:
        """Return the module integration test directory."""
        return PROJECT_ROOT / "tests" / "integration" / "pychessview" / self.name


ENGINE = ModuleInfo("engine")
"""Engine module metadata."""

QT_WIDGET = ModuleInfo("qt", "qt")
"""Qt widget module metadata."""

PYTHON_TEMP_DIR_NAMES: set[str | re.Pattern[str]] = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    re.compile(r".*\.egg-info$"),
    re.compile(r"^pytest-cache-files.*"),
}
"""Literal names and compiled patterns identifying removable Python temporary directories."""

### Support functions ###


def _is_dict(value: object) -> TypeGuard[dict[Any, Any]]:
    """Return whether a value is a dictionary.

    Args:
        value: Value to inspect.

    Returns:
        ``True`` when ``value`` is a dictionary.
    """
    return isinstance(value, dict)


def _load_pyproject_data(project_dir: Path) -> dict[Any, Any]:
    """Load the pyproject data from a directory.

    Args:
        dir: Directory containing the pyproject.toml file.

    Returns:
        Parsed TOML data from the pyproject.toml file.

    Raises:
        RuntimeError: If the pyproject file is missing, invalid, or does not contain a top-level table.
    """
    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.is_file():
        raise RuntimeError(f"pyproject.toml was not found at {pyproject_path}")

    try:
        with pyproject_path.open("rb") as file_obj:
            data = tomllib.load(file_obj)
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"Invalid pyproject.toml: {exc}") from exc

    if not _is_dict(data):
        raise RuntimeError("pyproject.toml must contain a TOML table at the top level.")

    return data


def _run(command: Sequence[str], *, cwd: Path | None = None) -> int:
    """Run a subprocess command and return its exit code.

    Args:
        command: Command and arguments to execute.
        cwd: Optional working directory for the subprocess.

    Returns:
        Process exit code.
    """
    print("$", " ".join(command))
    return subprocess.run(command, check=False, cwd=cwd).returncode


def _error(message: str, exit_code: int = 1) -> int:
    """Print an error message to standard error.

    Args:
        message: Error text to display.
        exit_code: Exit code to return.
    """
    print(f"ERROR: {message}", file=sys.stderr)
    return exit_code


def _ask_yes_no(prompt: str, *, default: bool = False) -> bool:
    """Prompt for a yes-or-no answer.

    Args:
        prompt: Prompt text shown before the answer suffix.
        default: Answer returned when the user submits an empty response.

    Returns:
        ``True`` for yes and ``False`` for no.
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        answer = input(prompt + suffix).strip()
        if not answer:
            return default

        lower_case_answer = answer.lower()
        if lower_case_answer in {"y", "yes"}:
            return True
        if lower_case_answer in {"n", "no"}:
            return False

        print("Please answer with y or n.")


def _install_dep(python_executable: str, extra: str = "") -> int:
    """Install a package directory in editable mode.

    Args:
        python_executable: Python executable used to run pip.
        extra: Optional extras selector appended to the install target.

    Returns:
        Pip process exit code.
    """
    target = str(PROJECT_ROOT)
    if extra:
        target = f"{target}[{extra}]"
    return _run((python_executable, "-m", "pip", "install", "-e", target), cwd=PROJECT_ROOT)


def _run_pytest(python_executable: str, *args: str) -> int:
    """Run pytest with the provided command-line arguments.

    Args:
        python_executable: Python executable to use for running pytest.
        *args: Arguments forwarded to pytest.

    Returns:
        Pytest process exit code.
    """
    return _run((python_executable, "-m", "pytest", *args))


def _run_test_paths(python_executable: str, *paths: Path) -> int:
    """Run pytest for existing target paths.

    Args:
        python_executable: Python executable to use for running pytest.
        *paths: Candidate test directories or files.

    Returns:
        Pytest exit code, or success when no matching tests are present.
    """
    existing_paths = [str(path) for path in paths if path.exists()]
    if not existing_paths:
        print("No matching test directories found. Treating as success.")
        return 0

    exit_code = _run_pytest(python_executable, *existing_paths)
    if exit_code == 5:
        print("No tests were collected. Treating as success.")
        return 0
    return exit_code


def _is_python_temp_dir_name(path_name: str) -> bool:
    """Return whether a directory should be treated as removable Python tooling output.

    Args:
        path_name: Directory name to compare against known Python temporary directories.

    Returns:
        ``True`` if the directory name matches a known Python temporary directory.
    """
    for temp_dir_name in PYTHON_TEMP_DIR_NAMES:
        if isinstance(temp_dir_name, str):
            if path_name == temp_dir_name:
                return True
            continue
        if temp_dir_name.fullmatch(path_name):
            return True
    return False


def _get_development_extras() -> str:
    """Return extras needed for development and CI commands.

    Returns:
        Extras selector for development dependencies.
    """
    return ",".join(["dev", QT_WIDGET.extra])


### Python functions ###


def _python_matches_requirements(python_executable: str, required_python: str) -> tuple[int, int, int] | None:
    """Return a Python version tuple when an executable satisfies the requirement.

    Args:
        python_executable: Python executable to inspect.
        required_python: Version specifier that must be satisfied.

    Returns:
        Version tuple for matching executables, or ``None`` when the executable is unusable or unsupported.
    """
    check_script = """
try:
    import sys

    req = sys.argv[1]

    try:
        __import__("venv")
    except ModuleNotFoundError as exc:
        raise SystemExit(2) from exc

    try:
        from packaging.specifiers import SpecifierSet, InvalidSpecifier
        from packaging.version import Version
    except ModuleNotFoundError as exc:
        try:
            from pip._vendor.packaging.specifiers import SpecifierSet, InvalidSpecifier
            from pip._vendor.packaging.version import Version
        except ModuleNotFoundError:
            raise SystemExit(3) from exc

    try:
        spec = SpecifierSet(req)
    except InvalidSpecifier as exc:
        raise SystemExit(4) from exc

    cur = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if cur in spec: # pyright: ignore[reportOperatorIssue]
        print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        raise SystemExit(0)
    raise SystemExit(1)
except Exception as exc:
    raise SystemExit(5) from exc
"""
    result = subprocess.run(
        (python_executable, "-c", check_script, required_python), check=False, capture_output=True, text=True
    )
    if result.returncode != 0:
        return None

    version_text = result.stdout.strip()
    try:
        major_str, minor_str, micro_str = version_text.split(".")
        return (int(major_str), int(minor_str), int(micro_str))
    except ValueError:
        return None


def _get_required_python_version() -> str:
    """Read the required Python specifier from the workspace pyproject.

    Returns:
        Python version specifier from ``project.requires-python``.

    Raises:
        RuntimeError: If the project table or required version field is missing.
    """
    data = _load_pyproject_data(PROJECT_ROOT)
    project = data.get("project")
    if not _is_dict(project):
        raise RuntimeError("Missing [project] table in pyproject.toml.")

    requires_python = project.get("requires-python")
    if not isinstance(requires_python, str) or not requires_python.strip():
        raise RuntimeError("requires-python is missing or empty in pyproject.toml.")

    return requires_python.strip()


def _discover_required_python() -> tuple[str, str]:
    """Find the newest available Python executable matching the workspace requirement.

    Returns:
        Required Python version string and executable path.

    Raises:
        RuntimeError: If no matching Python executable can be found.
    """

    def _discover_python_candidates() -> list[str]:
        """Collect Python executable candidates from PATH and platform-specific launchers.

        Returns:
            Python executable candidates without duplicates.
        """
        candidates: list[str] = []

        def add_candidate(candidate: str | None) -> None:
            """Add a non-empty executable candidate once.

            Args:
                candidate: Candidate executable path or command name.
            """
            if not candidate:
                return
            if candidate not in candidates:
                candidates.append(candidate)

        add_candidate(sys.executable)
        add_candidate(shutil.which("python"))
        add_candidate(shutil.which("python3"))

        if not sys.platform.startswith("win"):
            for minor in range(50):
                add_candidate(shutil.which(f"python3.{minor}"))

        if sys.platform.startswith("win"):
            py_launcher = shutil.which("py")
            if py_launcher:
                result = subprocess.run((py_launcher, "-0p"), check=False, capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        match = re.match(r"^\s*-[Vv]:[^\s]+\s+\*?\s*(.+?)\s*$", line)
                        if match:
                            add_candidate(match.group(1))

        return candidates

    candidates = _discover_python_candidates()
    if not candidates:
        raise RuntimeError("No Python executable candidates found.")

    required_python_version = _get_required_python_version()

    matching_candidates: list[tuple[tuple[int, int, int], str]] = []
    for candidate in candidates:
        version_tuple = _python_matches_requirements(candidate, required_python_version)
        if version_tuple is not None:
            matching_candidates.append((version_tuple, candidate))

    if not matching_candidates:
        tried = ", ".join(candidates)
        raise RuntimeError(
            f"No Python executable found that matches the required version '{required_python_version}'. Tried: {tried}"
        )

    matching_candidates.sort(key=lambda item: (item[0][0], item[0][1], item[0][2], item[1]), reverse=True)
    final_candidate = matching_candidates[0]
    return ".".join(map(str, final_candidate[0])), final_candidate[1]


def _has_python_module(python_executable: str, module_name: str) -> bool:
    """Return whether a Python module is importable by an executable.

    Args:
        python_executable: Python executable used to inspect module availability.
        module_name: Module name to inspect.

    Returns:
        ``True`` if the module is importable by ``python_executable``.
    """
    result = subprocess.run(
        (
            python_executable,
            "-c",
            "import importlib.util, sys; raise SystemExit(0 if importlib.util.find_spec(sys.argv[1]) else 1)",
            module_name,
        ),
        check=False,
    )
    return result.returncode == 0


def _create_venv(python: str, venv_dir: Path) -> int:
    """Create the workspace virtual environment.

    Args:
        python: Python executable used to create the virtual environment.
        venv_dir: Target virtual environment directory.

    Returns:
        Virtual environment creation exit code.
    """
    # Check if virtual environment already exists
    if venv_dir.exists():
        print('Virtual environment ".venv" already exists.')
        if sys.stdin.isatty() and _ask_yes_no("Do you want to delete and recreate it?"):
            shutil.rmtree(venv_dir, ignore_errors=False)

    # Create virtual environment
    exit_code = _run((python, "-m", "venv", str(venv_dir)), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("Failed to create virtual environment.", exit_code)
    return exit_code


def _get_venv_python_executable(venv_dir: Path) -> str | None:
    """Return the Python executable path inside a virtual environment.

    Args:
        venv_dir: Virtual environment directory.

    Returns:
        Path to the Python executable inside the virtual environment, or ``None`` if it cannot be found.
    """
    if sys.platform.startswith("win"):
        path = venv_dir / "Scripts" / "python.exe"
    else:
        path = venv_dir / "bin" / "python"

    return str(path) if path.is_file() else None


def _get_python_executable() -> str:
    """Return the Python executable to use for development commands.

    Returns:
        Path to the Python executable inside the virtual environment if it exists;
        otherwise the current Python executable.
    """
    return _get_venv_python_executable(PROJECT_ROOT / ".venv") or sys.executable


### Git and pre-commit setup functions ###


def _ensure_shellcheck_available() -> int:
    """Return success only when the shellcheck executable is available.

    Returns:
        ``0`` when shellcheck is available; otherwise ``1`` after printing installation guidance.
    """
    if shutil.which("shellcheck") is not None:
        return 0

    return _error(
        """shellcheck is required but was not found in PATH.
Install it:
    Windows (winget): koalaman.shellcheck, (choco/scoop):  shellcheck
    Linux: install the 'shellcheck' package for your distro"""
    )


def _ensure_psscriptanalyzer_available() -> int:
    """Ensure PSScriptAnalyzer is available for PowerShell script checks.

    Returns:
        ``0`` when PowerShell and PSScriptAnalyzer are available or installed; otherwise ``1``.
    """
    pwsh = shutil.which("pwsh")
    powershell = shutil.which("powershell")

    if sys.platform.startswith("win"):
        ps_exe = pwsh or powershell
        ps_args = ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command"]
    else:
        ps_exe = pwsh
        ps_args = ["-NoProfile", "-NonInteractive", "-Command"]

    if ps_exe is None:
        return _error(
            """PowerShell 7+ (pwsh) is required for PSScriptAnalyzer but was not found in PATH.
Install PowerShell:
  Windows (winget): Microsoft.PowerShell
  Linux: install the 'powershell' package for your distro"""
        )

    ps_script = r"""
$ErrorActionPreference = 'Stop'

try {
  if (-not (Get-Module -ListAvailable -Name PowerShellGet)) {
    Write-Error "PowerShellGet module not found."
    exit 1
  }

  $prov = Get-PackageProvider -Name NuGet -ListAvailable -ErrorAction SilentlyContinue
  if (-not $prov -or ($prov.Version -lt [version]'2.8.5.201')) {
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force | Out-Null
  }

  try {
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction Stop
  } catch {
  }

  $module = Get-Module -ListAvailable -Name PSScriptAnalyzer | Select-Object -First 1
  if (-not $module) {
    Install-Module PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber | Out-Null
  }
} catch {
  Write-Error $_
  exit 1
}
"""

    exit_code = _run((ps_exe, *ps_args, ps_script), cwd=PROJECT_ROOT)

    if exit_code != 0:
        return _error("Failed to install/configure PSScriptAnalyzer.", exit_code)

    return 0


def _setup_git(venv_python: str) -> int:
    """Install git-related development hooks and Git LFS assets.

    Args:
        venv_python: Python executable inside the virtual environment.

    Returns:
        Setup command exit code.
    """
    git = shutil.which("git")
    if git is None:
        return _error(".git directory found, but git executable not found in PATH. Cannot install pre-commit hooks.")

    exit_code = _run((git, "lfs", "version"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("git-lfs is required but not available in PATH. Install Git LFS before bootstrapping.", exit_code)

    gitattributes = PROJECT_ROOT / ".gitattributes"
    if not gitattributes.is_file():
        return _error(".gitattributes is required.")

    exit_code = _run((git, "lfs", "install"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("git lfs install failed.", exit_code)

    exit_code = _run((git, "lfs", "pull"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("git lfs pull failed.", exit_code)

    exit_code = _run((git, "lfs", "checkout"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("git lfs checkout failed.", exit_code)

    exit_code = _run((venv_python, "-m", "pip", "install", "pre_commit"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("failed to install pre-commit.", exit_code)

    exit_code = _ensure_shellcheck_available()
    if exit_code != 0:
        return exit_code

    exit_code = _ensure_psscriptanalyzer_available()
    if exit_code != 0:
        return exit_code

    exit_code = _run((venv_python, "-m", "pre_commit", "install"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("pre-commit install failed.", exit_code)

    return 0


### Publish functions ###


def _get_git_tag_version() -> PackagingVersion | None:
    """Return the latest version from repository release tags.

    Returns:
        Latest version from release tags, or ``None`` if no valid release tags are found.

    Raises:
        RuntimeError: If reading git tags fails or if any release tag contains an invalid version.
    """

    # Import lazily so development commands can run before optional tooling dependencies are installed.
    from packaging.version import InvalidVersion, Version

    result = subprocess.run(
        ("git", "tag", "--list", "v*"),
        check=False,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to read git tags.")

    versions: list[PackagingVersion] = []
    for raw_tag in result.stdout.splitlines():
        tag = raw_tag.strip()
        if not tag:
            continue

        match = re.fullmatch(r"v(?P<version>[A-Za-z0-9_.!+-]+)", tag)
        if match is None:
            continue

        try:
            versions.append(Version(match.group("version")))
        except InvalidVersion:
            raise RuntimeError(f"Invalid version found in tag '{tag}'.")

    if not versions:
        return None

    return max(versions)


def _get_project_version() -> PackagingVersion:
    """Return the version declared in the workspace pyproject.

    Returns:
        Version from the pyproject.
    """

    # Import lazily so development commands can run before optional tooling dependencies are installed.
    from packaging.version import Version

    pyproject_data = _load_pyproject_data(PROJECT_ROOT)
    project = pyproject_data.get("project")
    if not _is_dict(project):
        raise RuntimeError("pyproject.toml is missing the [project] table.")

    return Version(str(project.get("version", "")).strip())


def _get_changelog_latest_release_entry() -> PackagingVersion | None:
    """Return the latest dated release entry from the changelog.

    Returns:
        Latest version found in the changelog, or ``None`` if no valid entries are found.
    """

    # Import lazily so development commands can run before optional tooling dependencies are installed.
    from packaging.version import InvalidVersion, Version

    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    if not changelog_path.is_file():
        raise RuntimeError("CHANGELOG.md was not found.")

    try:
        changelog_text = changelog_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to read CHANGELOG.md: {exc}") from exc

    versions: list[PackagingVersion] = []
    heading_pattern = re.compile(r"^## \[(?P<version>[^\]]+)\] - (?P<date>\S+)\s*$")
    for line in changelog_text.splitlines():
        match = heading_pattern.fullmatch(line.strip())
        if match is None:
            continue

        raw_version = match.group("version").strip()
        try:
            versions.append(Version(raw_version))
        except InvalidVersion:
            continue

    if not versions:
        return None

    return max(versions)


def _fetch_pypi_latest_version() -> PackagingVersion | None:
    """Fetch the latest released version of a package from PyPI.

    Returns:
        Latest released version from PyPI, or ``None`` if the package is not found.
    """

    # Import lazily so development commands can run before optional tooling dependencies are installed.
    from packaging.version import InvalidVersion, Version

    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"

    try:
        with urllib.request.urlopen(url) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise RuntimeError(f"Failed to query PyPI for package '{PACKAGE_NAME}': {exc}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to query PyPI for package '{PACKAGE_NAME}': {exc}") from exc

    if not _is_dict(payload):
        raise RuntimeError(f"Invalid PyPI response for package '{PACKAGE_NAME}'.")

    releases = payload.get("releases")
    if not _is_dict(releases):
        raise RuntimeError(f"Invalid PyPI response for package '{PACKAGE_NAME}'.")

    versions: list[PackagingVersion] = []
    for release_version in releases:
        if not isinstance(release_version, str) or not release_version.strip():
            continue
        try:
            versions.append(Version(release_version))
        except InvalidVersion:
            continue

    if not versions:
        return None

    return max(versions)


### Main functions ###


def bootstrap_dev() -> int:
    """Create and configure the local development environment.

    Returns:
        Bootstrap command exit code.
    """
    # Discover required Python version and executable
    try:
        selected_python_version, selected_python = _discover_required_python()
    except RuntimeError as exc:
        return _error(str(exc))

    print(f"Using python: {selected_python_version} ({selected_python})")

    # Define virtual environment directory
    venv_dir = PROJECT_ROOT / ".venv"

    # Create virtual environment
    exit_code = _create_venv(selected_python, venv_dir)
    if exit_code != 0:
        return exit_code

    # Get path to virtual environment python
    venv_python = _get_venv_python_executable(venv_dir)
    if venv_python is None:
        return _error(f"Failed to locate Python executable in virtual environment at {venv_dir}.")

    # Verify virtual environment python exists
    if not Path(venv_python).is_file():
        return _error(f"No python found in virtual environment at {venv_python}.")

    # Upgrade essential tools in the virtual environment
    exit_code = _run((venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("Failed to upgrade pip in the virtual environment.", exit_code)

    # Install dependencies
    exit_code = _install_dep(venv_python, _get_development_extras())
    if exit_code != 0:
        return _error("Failed to install workspace development dependencies.", exit_code)

    # Install pre-commit hooks if .git directory is present
    if (PROJECT_ROOT / ".git").is_dir():
        exit_code = _setup_git(venv_python)
        if exit_code != 0:
            return _error("Failed to setup Git hooks.", exit_code)

    # Clean up any existing Python temp directories
    exit_code = _run((venv_python, "-m", "tools.devtools", "clean"), cwd=PROJECT_ROOT)
    if exit_code != 0:
        return _error("Failed to clean Python cache directories.", exit_code)

    print("OK: Development environment is ready.")
    if sys.platform.startswith("win"):
        if (venv_dir / "Scripts" / "Activate.ps1").is_file():
            print(r" - Activate venv with (PowerShell): .\.venv\Scripts\Activate.ps1")
        if (venv_dir / "Scripts" / "activate.bat").is_file():
            print(r" - Activate venv with (cmd): .venv\Scripts\activate.bat")
    else:
        if (venv_dir / "bin" / "activate").is_file():
            print(" - Activate venv with (bash/zsh): source .venv/bin/activate")
    return 0


def bootstrap_ci() -> int:
    """Install dependencies needed by CI without creating a virtual environment.

    Returns:
        Bootstrap command exit code.
    """
    required_python_version = _get_required_python_version()
    if _python_matches_requirements(sys.executable, required_python_version) is None:
        return _error(
            f"Current Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} does not match "
            f"the required version '{required_python_version}'."
        )

    # Upgrade essential tools in the virtual environment
    exit_code = _run(
        (sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"), cwd=PROJECT_ROOT
    )
    if exit_code != 0:
        return _error("Failed to upgrade.", exit_code)

    exit_code = _install_dep(sys.executable, _get_development_extras())
    if exit_code != 0:
        return _error("Failed to install workspace development dependencies.", exit_code)

    print("OK: CI environment is ready.")
    return 0


def install_engine_dep() -> int:
    """Install the engine dependency.

    Returns:
        Pip process exit code.
    """
    return _install_dep(_get_python_executable())


def install_qt_widget_dep() -> int:
    """Install the Qt dependency.

    Returns:
        Pip process exit code.
    """
    return _install_dep(_get_python_executable(), QT_WIDGET.extra)


def install_dev_dep() -> int:
    """Install the development dependencies.

    Returns:
        Pip process exit code.
    """
    return _install_dep(_get_python_executable(), _get_development_extras())


def run_pre_commit(*args: str) -> int:
    """Run pre-commit hooks.

    Args:
        *args: Arguments forwarded to pre-commit.

    Returns:
        Pre-commit process exit code.
    """
    start_time = time.perf_counter()
    exit_code = _run((_get_python_executable(), "-m", "pre_commit", "run", *args), cwd=PROJECT_ROOT)
    elapsed_time = time.perf_counter() - start_time
    print(f"\nPre-commit finished in {elapsed_time:.2f}s")
    return exit_code


def test_all() -> int:
    """Run all tests in the repository.

    Returns:
        Pytest exit code, treating no collected tests as success.
    """
    exit_code = _run_test_paths(
        _get_python_executable(),
        ENGINE.unit_test_path,
        ENGINE.integration_test_path,
        QT_WIDGET.unit_test_path,
        QT_WIDGET.integration_test_path,
    )
    if exit_code == 5:
        print("No tests were collected. Treating as success.")
        return 0
    return exit_code


def test_engine_all() -> int:
    """Run all core pychessview tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), ENGINE.unit_test_path, ENGINE.integration_test_path)


def test_engine_unit() -> int:
    """Run core pychessview unit tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), ENGINE.unit_test_path)


def test_engine_integration() -> int:
    """Run core pychessview integration tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), ENGINE.integration_test_path)


def test_qt_widget_all() -> int:
    """Run all Qt widget tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), QT_WIDGET.unit_test_path, QT_WIDGET.integration_test_path)


def test_qt_widget_unit() -> int:
    """Run Qt widget unit tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), QT_WIDGET.unit_test_path)


def test_qt_widget_integration() -> int:
    """Run Qt widget integration tests.

    Returns:
        Pytest exit code.
    """
    return _run_test_paths(_get_python_executable(), QT_WIDGET.integration_test_path)


def validate_publish_readiness() -> int:
    """Validate the latest release tag against package metadata, changelog, and PyPI.

    Returns:
        ``0`` when the latest release tag is valid; otherwise a non-zero exit code.
    """
    try:
        tag_version = _get_git_tag_version()
    except RuntimeError as exc:
        return _error(str(exc))

    if tag_version is None:
        return _error(
            "No valid release git tags found in the repository. A release tag must exist to validate publish readiness."
        )

    # Validate that the package version matches the release tag.
    try:
        package_version = _get_project_version()
    except RuntimeError as exc:
        return _error(str(exc))

    if tag_version != package_version:
        return _error(
            f"Package metadata version '{package_version}' does not match the Git tag version '{tag_version}'."
        )

    # Validate that CHANGELOG.md contains the tagged release version with a concrete date.
    try:
        changelog_latest_version = _get_changelog_latest_release_entry()
    except RuntimeError as exc:
        return _error(str(exc))

    if tag_version != changelog_latest_version:
        return _error(
            f"CHANGELOG.md version '{changelog_latest_version}' does not match the Git tag version '{tag_version}'."
        )

    # Validate that the release tag version is newer than the latest published version on PyPI,
    # if the package exists.
    try:
        pypi_latest_version = _fetch_pypi_latest_version()
    except RuntimeError as exc:
        return _error(str(exc))

    if pypi_latest_version is not None and tag_version <= pypi_latest_version:
        return _error(
            f"the Git tag version '{tag_version}' is not newer than the latest version on PyPI '{pypi_latest_version}'."
        )

    print("OK: The package is ready for publishing.")

    return 0


def build_package() -> int:
    """Build and verify source and wheel distributions for the pychessview package.

    Returns:
        Build or verification process exit code, or ``1`` when prerequisites are missing.
    """
    python_executable = _get_python_executable()

    if not _has_python_module(python_executable, "build"):
        return _error("Python package 'build' is not installed.")

    if not _has_python_module(python_executable, "twine"):
        return _error("Python package 'twine' is not installed.")

    dist_dir = PROJECT_ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        exit_code = _run(
            (python_executable, "-m", "build", str(PROJECT_ROOT), "--outdir", str(tmp_dir)),
            cwd=PROJECT_ROOT,
        )
        if exit_code != 0:
            return exit_code

        built_files = tuple(sorted(path for path in tmp_dir.iterdir() if path.is_file()))
        if not built_files:
            return _error("No distribution files were produced by the build.")

        exit_code = _run((python_executable, "-m", "twine", "check", *map(str, built_files)), cwd=PROJECT_ROOT)
        if exit_code != 0:
            return exit_code

        for src in built_files:
            dst = dist_dir / src.name
            if dst.exists():
                return _error(f"Distribution file already exists: {dst}")
            shutil.move(str(src), str(dst))

    return 0


def test_built_package(wheel_path: Path) -> int:
    """Install and smoke-test a built wheel.

    Args:
        wheel_path: Path to the wheel file to test.

    Returns:
        Exit code indicating success or failure.
    """
    python_executable = _get_python_executable()

    if not wheel_path.is_file():
        return _error(f"Wheel file not found: {wheel_path}")

    if wheel_path.suffix != ".whl":
        return _error(f"Expected a .whl file, got: {wheel_path}")

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        # Create isolated virtual environment
        venv_dir = tmp_dir / "venv"
        exit_code = _run((python_executable, "-m", "venv", str(venv_dir)), cwd=PROJECT_ROOT)
        if exit_code != 0:
            return _error("Failed to create test virtual environment.", exit_code)

        venv_python = _get_venv_python_executable(venv_dir)
        if venv_python is None:
            return _error("Failed to locate python in test virtual environment.")

        # Install wheel
        exit_code = _run((venv_python, "-m", "pip", "install", str(wheel_path)), cwd=PROJECT_ROOT)
        if exit_code != 0:
            return _error("Failed to install built wheel.", exit_code)

        # Smoke test: import package
        exit_code = _run(
            (venv_python, "-c", f"import {PACKAGE_NAME}; print({PACKAGE_NAME}.__version__)"),
            cwd=PROJECT_ROOT,
        )
        if exit_code != 0:
            return _error("Import test failed for built package.", exit_code)

    print("OK: Built package installs and imports correctly.")
    return 0


def clean_cache() -> int:
    """Clean up Python cache and temporary directories.

    Returns:
        ``0`` after cleanup completes.
    """
    removed_dirs: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_dir():
            continue
        if _is_python_temp_dir_name(path.name):
            shutil.rmtree(path, ignore_errors=True)
            if not path.exists():
                removed_dirs.append(path)

    if not removed_dirs:
        print("No Python temp or egg-info directories found.")
        return 0

    for removed in sorted(removed_dirs):
        print(f"removed: {removed.relative_to(PROJECT_ROOT)}")
    print(f"Removed {len(removed_dirs)} Python temp/egg-info directories.")
    return 0


def run_pyright(*args: str) -> int:
    """Run Pyright type checking.

    Args:
        *args: Arguments forwarded to Pyright.

    Returns:
        Pyright process exit code.
    """
    return _run((_get_python_executable(), "-m", "pyright", *args), cwd=PROJECT_ROOT)


def main() -> int:
    """Run the selected development command from command-line arguments.

    Returns:
        Process exit code from the selected command.
    """
    parser = argparse.ArgumentParser(
        description="Development helper commands.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="group", required=True)

    # bootstrap
    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="Set up environment",
        description="Create and configure development or CI environment.",
    )
    bootstrap_parser.add_argument(
        "target",
        choices=("dev", "ci"),
        help="dev: create venv setup, ci: install basic dependencies for CI",
    )

    def _dispatch_bootstrap(args: argparse.Namespace) -> int:
        """Dispatch the selected bootstrap target.

        Args:
            args: Parsed command-line arguments containing the bootstrap target.

        Returns:
            Bootstrap command exit code.
        """
        return bootstrap_dev() if args.target == "dev" else bootstrap_ci()

    bootstrap_parser.set_defaults(func=_dispatch_bootstrap)

    # install
    install_parser = subparsers.add_parser(
        "install",
        help="Install dependencies",
        description="Install dependencies in editable mode.",
    )
    install_parser.add_argument(
        "target",
        choices=("engine", "dev", "qt-widget"),
        help="engine: install engine dependencies, dev: install development dependencies, "
        "qt-widget: install Qt widget dependencies",
    )

    def _dispatch_install(args: argparse.Namespace) -> int:
        """Dispatch the selected dependency installation target.

        Args:
            args: Parsed command-line arguments containing the install target.

        Returns:
            Installation command exit code.
        """
        return {
            "engine": install_engine_dep,
            "dev": install_dev_dep,
            "qt-widget": install_qt_widget_dep,
        }[args.target]()

    install_parser.set_defaults(func=_dispatch_install)

    # test
    test_parser = subparsers.add_parser(
        "test",
        help="Run tests",
        description="Execute tests for selected scope.",
    )
    test_parser.add_argument(
        "target",
        choices=(
            "all",
            "engine-all",
            "engine-unit",
            "engine-integration",
            "qt-widget-all",
            "qt-widget-unit",
            "qt-widget-integration",
        ),
        help="all: everything, engine-*: engine module tests, qt-widget-*: Qt widget tests",
    )

    def _dispatch_test(args: argparse.Namespace) -> int:
        """Dispatch the selected test target.

        Args:
            args: Parsed command-line arguments containing the test target.

        Returns:
            Test command exit code.
        """
        return {
            "all": test_all,
            "engine-all": test_engine_all,
            "engine-unit": test_engine_unit,
            "engine-integration": test_engine_integration,
            "qt-widget-all": test_qt_widget_all,
            "qt-widget-unit": test_qt_widget_unit,
            "qt-widget-integration": test_qt_widget_integration,
        }[args.target]()

    test_parser.set_defaults(func=_dispatch_test)

    # run
    run_parser = subparsers.add_parser(
        "run",
        help="Run tools",
        description="Execute development tools.",
    )
    run_parser.add_argument("target", choices=("pre-commit", "pre-commit-all", "pyright"))
    run_parser.add_argument("args", nargs=argparse.REMAINDER)

    def _dispatch_run(args: argparse.Namespace) -> int:
        """Dispatch the selected development tool target.

        Args:
            args: Parsed command-line arguments containing the run target.

        Returns:
            Tool command exit code.
        """
        if args.target == "pre-commit":
            return run_pre_commit(*args.args)

        if args.target == "pre-commit-all":
            return run_pre_commit("--all-files", *args.args)

        return run_pyright(*args.args)

    run_parser.set_defaults(func=_dispatch_run)

    # build
    build_parser = subparsers.add_parser(
        "build",
        help="Build package",
        description="Build and validate distribution artifacts.",
    )

    def _dispatch_build(args: argparse.Namespace) -> int:
        """Dispatch the package build command.

        Args:
            args: Parsed command-line arguments for the build command.

        Returns:
            Build command exit code.
        """
        _ = args
        return build_package()

    build_parser.set_defaults(func=_dispatch_build)

    # validate
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate project",
        description="Perform project validation.",
    )
    validate_parser.add_argument(
        "target",
        choices=("readiness", "build"),
        help="readiness: validate package readiness for publication, "
        "build: validate built distribution artifacts (install and import)",
    )
    validate_parser.add_argument(
        "wheel",
        nargs="?",
        help="Path to wheel file (required for 'build')",
    )

    def _dispatch_validate(args: argparse.Namespace) -> int:
        """Dispatch the selected validation target.

        Args:
            args: Parsed command-line arguments for the validate command.

        Returns:
            Validation command exit code.
        """
        if args.target == "readiness":
            if args.wheel is not None:
                parser.error("unrecognized arguments: wheel")
            return validate_publish_readiness()

        if args.wheel is None:
            parser.error("the following arguments are required for 'build': wheel")

        return test_built_package(Path(args.wheel))

    validate_parser.set_defaults(func=_dispatch_validate)

    # clean
    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean cache",
        description="Remove Python cache and temp directories.",
    )

    def _dispatch_clean(args: argparse.Namespace) -> int:
        """Dispatch the Python cache cleanup command.

        Args:
            args: Parsed command-line arguments for the clean command.

        Returns:
            Cleanup command exit code.
        """
        _ = args
        return clean_cache()

    clean_parser.set_defaults(func=_dispatch_clean)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
