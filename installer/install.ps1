param(
    [switch]$InstallChromium
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$installRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $installRoot

$wheel = Get-ChildItem -Path $installRoot -Filter "beacon_utilities-*.whl" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $wheel) {
    throw "No wheel file matching 'beacon_utilities-*.whl' was found in $installRoot"
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = "py"
    $pythonPrefix = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = "python"
    $pythonPrefix = @()
} else {
    throw "Python was not found. Install Python 3.11+ and rerun this installer."
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment in .venv"
    $venvCreateCommand = $pythonPrefix + @("-m", "venv", ".venv")
    & $pythonCommand @venvCreateCommand
}

$venvPython = Join-Path $installRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python executable not found: $venvPython"
}

Write-Host "Upgrading pip"
& $venvPython -m pip install --upgrade pip

Write-Host "Installing BeaconUtilities from $($wheel.Name)"
& $venvPython -m pip install --upgrade $wheel.FullName

if ($InstallChromium) {
    Write-Host "Installing Playwright Chromium runtime"
    & $venvPython -m playwright install chromium
}

$configDir = Join-Path $installRoot "config"
$configIni = Join-Path $configDir "config.ini"
$configExampleIni = Join-Path $configDir "config.example.ini"

if ((-not (Test-Path $configIni)) -and (Test-Path $configExampleIni)) {
    Copy-Item -Path $configExampleIni -Destination $configIni
    Write-Host "Created config\\config.ini from config.example.ini"
}

$docsLauncherPs1 = Join-Path $installRoot "start-user-docs.ps1"
$docsLauncherCmd = Join-Path $installRoot "start-user-docs.cmd"
$backupLauncherPs1 = Join-Path $installRoot "start-beacon-backup.ps1"
$backupLauncherCmd = Join-Path $installRoot "start-beacon-backup.cmd"

$ps1Content = @'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$docsIndex = Join-Path $scriptDir "docs\index.html"

if (Test-Path $docsIndex) {
    Start-Process $docsIndex
} else {
    Start-Process "https://petersfieldu3a.github.io/BeaconUtilities/"
}
'@
Set-Content -Path $docsLauncherPs1 -Value $ps1Content -Encoding utf8

$cmdContent = @'
@echo off
set SCRIPT_DIR=%~dp0
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-user-docs.ps1" %*
'@
Set-Content -Path $docsLauncherCmd -Value $cmdContent -Encoding ascii

$backupPs1Content = @'
param(
    [string]$OutputFile = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runScript = Join-Path $scriptDir "run.ps1"

if (-not (Test-Path $runScript)) {
    throw "Launcher script not found: $runScript"
}

if ([string]::IsNullOrWhiteSpace($OutputFile)) {
    & $runScript backup-beacon
}
else {
    & $runScript backup-beacon --output-file $OutputFile
}

exit $LASTEXITCODE
'@
Set-Content -Path $backupLauncherPs1 -Value $backupPs1Content -Encoding utf8

$backupCmdContent = @'
@echo off
set SCRIPT_DIR=%~dp0
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-beacon-backup.ps1" %*
'@
Set-Content -Path $backupLauncherCmd -Value $backupCmdContent -Encoding ascii

Write-Host ""
Write-Host "Installation complete."
Write-Host "Next steps:"
Write-Host "  1. Edit config\\config.ini"
Write-Host "  2. Run: .\\.venv\\Scripts\\python.exe -m beaconutilities.cli sync --dry-run"
Write-Host "  3. Start docs: .\\start-user-docs.ps1 (or double-click start-user-docs.cmd)"
Write-Host "  4. Run backup: .\\start-beacon-backup.ps1 (or double-click start-beacon-backup.cmd)"
