# PowerShell build helper for Windows (no GNU make required).
# Usage:
#   .\build.ps1              # configure + build
#   .\build.ps1 -DistClean   # remove build/ then rebuild
#   .\build.ps1 -Clean
#   .\build.ps1 -Gui:$false

param(
    [switch]$Clean,
    [switch]$DistClean,
    [switch]$ConfigureOnly,
    [bool]$Gui = $true,
    [string]$BuildDir = "build",
    [string]$Config = "Release"
)

$ErrorActionPreference = "Stop"

function Require-CMake {
    if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "ERROR: cmake not found on PATH."
        Write-Host "Install with:  winget install Kitware.CMake"
        Write-Host "Or:            choco install cmake"
        Write-Host ""
        exit 1
    }
}

Require-CMake

if ($DistClean) {
    Write-Host "Removing $BuildDir ..."
    if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
}

if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host "Cleaning $BuildDir ..."
    cmake --build $BuildDir --config $Config --target clean
    if (-not $DistClean) { exit 0 }
}

$guiFlag = if ($Gui) { "ON" } else { "OFF" }

Write-Host "Configuring (GUI=$guiFlag, Config=$Config) ..."
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
cmake -S . -B $BuildDir `
    -DCMAKE_BUILD_TYPE=$Config `
    -DRAMDISK_BUILD_EXAMPLES=ON `
    -DRAMDISK_BUILD_GUI=$guiFlag

if ($ConfigureOnly) { exit 0 }

Write-Host "Building ..."
cmake --build $BuildDir --config $Config

Write-Host ""
Write-Host "Done. Binaries under $BuildDir\ (e.g. $BuildDir\Release\ramdisk_cli.exe)"
