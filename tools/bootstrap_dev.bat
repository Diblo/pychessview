@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

where python >nul 2>&1
if %errorlevel% neq 0 (
  echo ERROR: python was not found in PATH.
  exit /b 1
)

pushd "%PROJECT_ROOT%"
python -m tools.devtools bootstrap dev
set "EXIT_CODE=%errorlevel%"
popd

exit /b %EXIT_CODE%
