[CmdletBinding()]
param(
    [switch]$Clean,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$SpecPath = Join-Path $RepoRoot "PeriodicTableApp.spec"
$BuildDir = Join-Path $RepoRoot "build"
$DistDir = Join-Path $RepoRoot "dist"
$ReleaseRoot = Join-Path $DistDir "release"
$ReleaseReadmeSource = Join-Path $RepoRoot "docs\README_release_windows.txt"
$LicenseSource = Join-Path $RepoRoot "LICENSE"
$ReleaseNotesSource = Join-Path $RepoRoot "RELEASE_NOTES.md"

function Resolve-PythonCommand {
    param([string]$CommandValue)

    if ([System.IO.Path]::IsPathRooted($CommandValue)) {
        return [System.IO.Path]::GetFullPath($CommandValue)
    }

    $RepoRelativeCandidate = Join-Path $RepoRoot $CommandValue
    if (Test-Path -LiteralPath $RepoRelativeCandidate) {
        return [System.IO.Path]::GetFullPath($RepoRelativeCandidate)
    }

    return $CommandValue
}

function Assert-RepoPath {
    param([string]$PathValue)

    $FullPath = [System.IO.Path]::GetFullPath($PathValue)
    if (-not $FullPath.StartsWith($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside the repository: $FullPath"
    }

    return $FullPath
}

function Remove-RepoItem {
    param([string]$PathValue)

    $FullPath = Assert-RepoPath $PathValue
    if (Test-Path -LiteralPath $FullPath) {
        Remove-Item -LiteralPath $FullPath -Recurse -Force
    }
}

function Assert-ExistingRepoItem {
    param(
        [string]$PathValue,
        [string]$Description
    )

    $FullPath = Assert-RepoPath $PathValue
    if (-not (Test-Path -LiteralPath $FullPath)) {
        throw "Missing ${Description}: $FullPath"
    }

    return $FullPath
}

function New-ReleaseArchive {
    param(
        [string]$SourceFolder,
        [string]$DestinationZip,
        [int]$MaxAttempts = 5,
        [int]$DelaySeconds = 2
    )

    $SourceFolder = Assert-RepoPath $SourceFolder
    $DestinationZip = Assert-RepoPath $DestinationZip

    for ($Attempt = 1; $Attempt -le $MaxAttempts; $Attempt++) {
        try {
            if (Test-Path -LiteralPath $DestinationZip) {
                Remove-Item -LiteralPath $DestinationZip -Force
            }

            Compress-Archive -LiteralPath $SourceFolder -DestinationPath $DestinationZip -Force
            return
        }
        catch {
            if ($Attempt -eq $MaxAttempts) {
                throw
            }

            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

$PythonCommand = Resolve-PythonCommand $PythonExe

function Invoke-FrozenSmokeTest {
    param(
        [pscustomobject]$Metadata,
        [string]$ReleaseFolder,
        [int]$ExitDelayMilliseconds = 1500,
        [int]$TimeoutSeconds = 20
    )

    $ReleaseFolder = Assert-RepoPath $ReleaseFolder
    $ExecutablePath = Assert-ExistingRepoItem (
        Join-Path $ReleaseFolder ($Metadata.executable_name + ".exe")
    ) "release executable"
    $null = Assert-ExistingRepoItem (Join-Path $ReleaseFolder "_internal\data\raw\elements.json") "elements dataset"
    $null = Assert-ExistingRepoItem (
        Join-Path $ReleaseFolder "_internal\data\reference\nomenclature_data.json"
    ) "nomenclature dataset"

    if ($Metadata.icon_present) {
        $null = Assert-ExistingRepoItem (Join-Path $ReleaseFolder "_internal\assets\app.ico") "release icon"
    }

    $SmokeRoot = Join-Path $RepoRoot ".test_runtime\frozen_smoke"
    Remove-RepoItem $SmokeRoot
    New-Item -ItemType Directory -Force -Path (Assert-RepoPath $SmokeRoot) | Out-Null

    $StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $StartInfo.FileName = $ExecutablePath
    $StartInfo.WorkingDirectory = $ReleaseFolder
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.EnvironmentVariables["QT_QPA_PLATFORM"] = "offscreen"
    $StartInfo.EnvironmentVariables["PERIODIC_TABLE_SMOKE_EXIT_MS"] = [string]$ExitDelayMilliseconds
    $StartInfo.EnvironmentVariables["PERIODIC_TABLE_LOG_ROOT"] = $SmokeRoot

    $Process = [System.Diagnostics.Process]::Start($StartInfo)
    if ($null -eq $Process) {
        throw "Unable to start frozen smoke test process: $ExecutablePath"
    }

    try {
        if (-not $Process.WaitForExit($TimeoutSeconds * 1000)) {
            try {
                $Process.Kill()
            }
            catch {
            }

            throw "Frozen smoke test timed out after $TimeoutSeconds seconds: $ExecutablePath"
        }

        if ($Process.ExitCode -ne 0) {
            throw "Frozen smoke test failed with exit code $($Process.ExitCode): $ExecutablePath"
        }
    }
    finally {
        $Process.Dispose()
    }

    $SmokeLogPath = Join-Path (
        Join-Path (
            Join-Path (
                Join-Path $SmokeRoot $Metadata.vendor
            ) $Metadata.executable_name
        ) "logs"
    ) ($Metadata.executable_name + ".log")
    $null = Assert-ExistingRepoItem $SmokeLogPath "frozen smoke log"

    Write-Host "Frozen smoke test passed: $ExecutablePath"
}

$MetadataJson = & $PythonCommand -c "from src.app_metadata import get_build_metadata; import json; print(json.dumps(get_build_metadata()))"
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read build metadata from src.app_metadata."
}

$Metadata = $MetadataJson | ConvertFrom-Json
$ExecutableOutput = Join-Path $DistDir $Metadata.executable_name
$ReleaseFolder = Join-Path $ReleaseRoot $Metadata.release_bundle_name
$ReleaseZip = Join-Path $ReleaseRoot ($Metadata.release_bundle_name + ".zip")
$ReleaseReadmeTemplate = Assert-ExistingRepoItem $ReleaseReadmeSource "release README template"
$LicenseTemplate = Assert-ExistingRepoItem $LicenseSource "license file"
$ReleaseNotesTemplate = Assert-ExistingRepoItem $ReleaseNotesSource "release notes file"

if (-not (Test-Path -LiteralPath $SpecPath)) {
    throw "Missing PyInstaller spec file: $SpecPath"
}

& $PythonCommand -m PyInstaller --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller is not installed. Install build dependencies with: python -m pip install -r requirements-build.txt"
}

if ($Clean) {
    Remove-RepoItem $BuildDir
    Remove-RepoItem $ExecutableOutput
    Remove-RepoItem $ReleaseFolder
    Remove-RepoItem $ReleaseZip
}

New-Item -ItemType Directory -Force -Path (Assert-RepoPath $ReleaseRoot) | Out-Null

Push-Location $RepoRoot
try {
    Write-Host "Building $($Metadata.display_name) $($Metadata.release_display_name)"
    & $PythonCommand -m PyInstaller --clean --noconfirm $SpecPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    $BuiltFolder = Assert-RepoPath $ExecutableOutput
    if (-not (Test-Path -LiteralPath $BuiltFolder)) {
        throw "Expected build output folder not found: $BuiltFolder"
    }

    Remove-RepoItem $ReleaseFolder
    Remove-RepoItem $ReleaseZip

    Copy-Item -LiteralPath $BuiltFolder -Destination $ReleaseFolder -Recurse
    Copy-Item -LiteralPath $ReleaseReadmeTemplate -Destination (Join-Path $ReleaseFolder "README.txt") -Force
    Copy-Item -LiteralPath $LicenseTemplate -Destination (Join-Path $ReleaseFolder "LICENSE.txt") -Force
    Copy-Item -LiteralPath $ReleaseNotesTemplate -Destination (Join-Path $ReleaseFolder "RELEASE_NOTES.md") -Force
    Invoke-FrozenSmokeTest -Metadata $Metadata -ReleaseFolder $ReleaseFolder
    New-ReleaseArchive -SourceFolder $ReleaseFolder -DestinationZip $ReleaseZip

    Write-Host "Build folder: $BuiltFolder"
    Write-Host "Release folder: $ReleaseFolder"
    Write-Host "Release zip: $ReleaseZip"

    if (-not $Metadata.icon_present) {
        Write-Warning "Optional icon not found at $($Metadata.optional_icon_path). Default PyInstaller icon was used."
    }
}
finally {
    Pop-Location
}
