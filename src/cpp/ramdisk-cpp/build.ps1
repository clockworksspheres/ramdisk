# PowerShell build helper for Windows (no GNU make required).
# Usage:
#   .\build.ps1                      # configure + build
#   .\build.ps1 -DistClean           # remove build/ then rebuild
#   .\build.ps1 -Clean
#   .\build.ps1 -Gui:$false          # skip Qt GUI
#   .\build.ps1 -QtPath C:\Qt\6.8.0\msvc2022_64

param(
    [switch]$Clean,
    [switch]$DistClean,
    [switch]$ConfigureOnly,
    [bool]$Gui = $true,
    [string]$BuildDir = "build",
    [string]$Config = "Release",
    [string]$QtPath = ""
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

function Find-QtPrefix {
    param([string]$Explicit)

    if ($Explicit -and (Test-Path $Explicit)) {
        return (Resolve-Path $Explicit).Path
    }
    if ($env:CMAKE_PREFIX_PATH) {
        foreach ($p in ($env:CMAKE_PREFIX_PATH -split ';')) {
            if ($p -and (Test-Path (Join-Path $p "lib\cmake\Qt6"))) {
                return $p
            }
            if ($p -and (Test-Path (Join-Path $p "lib\cmake\Qt6\Qt6Config.cmake"))) {
                return $p
            }
        }
    }
    if ($env:Qt6_DIR -and (Test-Path $env:Qt6_DIR)) {
        # Qt6_DIR is usually .../lib/cmake/Qt6
        $prefix = Split-Path (Split-Path $env:Qt6_DIR -Parent) -Parent
        if (Test-Path $prefix) { return $prefix }
        return $env:Qt6_DIR
    }

    $candidates = @()

    # Official installer / aqtinstall layouts
    foreach ($root in @("C:\Qt", "$env:USERPROFILE\Qt", "C:\Qt\Tools")) {
        if (-not (Test-Path $root)) { continue }
        Get-ChildItem -Path $root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $verDir = $_.FullName
            Get-ChildItem -Path $verDir -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                $kit = $_.FullName
                if (Test-Path (Join-Path $kit "lib\cmake\Qt6\Qt6Config.cmake")) {
                    $candidates += $kit
                }
            }
            # Sometimes version is nested: C:\Qt\6.8.0\msvc2022_64
            if (Test-Path (Join-Path $verDir "lib\cmake\Qt6\Qt6Config.cmake")) {
                $candidates += $verDir
            }
        }
    }

    # Chocolatey qt6-base-dev / aqt default
    foreach ($p in @(
        "C:\Qt\6.4.2\mingw_64",
        "C:\Qt\6.5.3\msvc2019_64",
        "C:\Qt\6.6.3\msvc2019_64",
        "C:\Qt\6.7.3\msvc2019_64",
        "C:\Qt\6.8.0\msvc2022_64",
        "C:\Qt\6.8.1\msvc2022_64",
        "C:\Qt\6.8.2\msvc2022_64",
        "C:\Qt\6.8.3\msvc2022_64",
        "C:\Qt\6.9.0\msvc2022_64",
        "C:\Qt\6.9.1\msvc2022_64",
        "C:\Qt\6.9.2\msvc2022_64",
        "C:\Qt\6.10.0\msvc2022_64"
    )) {
        if (Test-Path (Join-Path $p "lib\cmake\Qt6\Qt6Config.cmake")) {
            $candidates += $p
        }
    }

    # Prefer MSVC kits over MinGW when building with Visual Studio
    $msvc = $candidates | Where-Object { $_ -match 'msvc' } | Select-Object -Last 1
    if ($msvc) { return $msvc }
    if ($candidates.Count -gt 0) { return $candidates[-1] }
    return $null
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
$cmakeArgs = @(
    "-S", ".",
    "-B", $BuildDir,
    "-DRAMDISK_BUILD_EXAMPLES=ON",
    "-DRAMDISK_BUILD_GUI=$guiFlag"
)

if ($Gui) {
    $qt = Find-QtPrefix -Explicit $QtPath
    if ($qt) {
        Write-Host "Using Qt at: $qt"
        $cmakeArgs += "-DCMAKE_PREFIX_PATH=$qt"
        $cmakeArgs += "-DQt6_DIR=$qt\lib\cmake\Qt6"
    } else {
        Write-Host ""
        Write-Host "WARNING: Qt 6 not found. GUI will be skipped."
        Write-Host "Install Qt, then rebuild:"
        Write-Host "  choco install qt6-base-dev -y"
        Write-Host "  # or MSVC kit (recommended with Visual Studio):"
        Write-Host "  pip install aqtinstall"
        Write-Host "  aqt install-qt windows desktop 6.8.0 win64_msvc2022_64 -O C:\Qt"
        Write-Host "  .\build.ps1 -DistClean -QtPath C:\Qt\6.8.0\msvc2022_64"
        Write-Host ""
        Write-Host "Or set:  `$env:CMAKE_PREFIX_PATH = 'C:\Qt\6.8.0\msvc2022_64'"
        Write-Host ""
    }
}

Write-Host "Configuring (GUI=$guiFlag, Config=$Config) ..."
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
& cmake @cmakeArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($ConfigureOnly) { exit 0 }

Write-Host "Building ..."
& cmake --build $BuildDir --config $Config
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Done. Binaries under $BuildDir\ (e.g. $BuildDir\Release\ramdisk_cli.exe)"
if ($Gui) {
    $guiExe = Join-Path $BuildDir "$Config\ramdisk_gui.exe"
    if (Test-Path $guiExe) {
        Write-Host "GUI: $guiExe"
    } else {
        Write-Host "GUI was not built (Qt6 not found during configure)."
    }
}
