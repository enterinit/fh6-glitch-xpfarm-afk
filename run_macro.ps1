$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $projectRoot ".venv"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    python -m venv $venvPath
}

& $pythonPath -m pip install --disable-pip-version-check -r (Join-Path $projectRoot "requirements.txt")
& $pythonPath (Join-Path $projectRoot "horizon_gamepad_macro.py") @args
