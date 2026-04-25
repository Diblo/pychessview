#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "ERROR: python was not found in PATH."
    exit 1
}

Push-Location $ProjectRoot
try {
    & python -m tools.devtools bootstrap dev
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
