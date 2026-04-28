# TaskSense MSIX Build Helper - PowerShell Script

param(
    [ValidateSet("lite", "pro")]
    [string]$Edition = "pro",
    [string]$Version,
    [switch]$Sign,
    [string]$CertPath,
    [switch]$Help
)

function Show-Help {
    Write-Host "TaskSense MSIX Build Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Verwendung: .\build_msix.ps1 [Options]" -ForegroundColor Green
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Edition      : lite oder pro"
    Write-Host "  -Version      : Versionsnummer"
    Write-Host "  -Sign         : Digitale Signatur hinzufügen"
    Write-Host "  -CertPath     : Pfad zum Zertifikat (.pfx)"
    Write-Host ""
    Write-Host "Beispiele:"
    Write-Host "  .\build_msix.ps1 -Edition lite"
    Write-Host "  .\build_msix.ps1 -Edition pro -Version 1.0.4"
    Write-Host "  .\build_msix.ps1 -Edition pro -Sign -CertPath cert.pfx"
    Write-Host ""
}

function Check-Prerequisites {
    Write-Host "🔍 Prüfe Voraussetzungen..." -ForegroundColor Yellow

    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python gefunden: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Python nicht gefunden!" -ForegroundColor Red
        exit 1
    }

    try {
        $makeAppxPath = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\MakeAppx.exe"
        if (Test-Path $makeAppxPath) {
            Write-Host "✓ MakeAppx gefunden" -ForegroundColor Green
            $env:Path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
        }
        else {
            Write-Host "⚠ MakeAppx nicht im Standard-Pfad gefunden" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠ MakeAppx-Prüfung fehlgeschlagen" -ForegroundColor Yellow
    }

    Write-Host ""
}

function Build-MSIX {
    Write-Host "🔨 Starte MSIX Build-Prozess..." -ForegroundColor Cyan
    Write-Host ""

    $cmd = @("python", "build_msix.py", "--edition", $Edition)

    if ($Version) {
        $cmd += "--version"
        $cmd += $Version
    }

    if ($Sign) {
        $cmd += "--sign"
        if ($CertPath) {
            $cmd += "--cert"
            $cmd += $CertPath
        }
    }

    Write-Host "Befehl: $($cmd -join ' ')" -ForegroundColor Gray
    Write-Host ""

    & $cmd[0] $cmd[1..($cmd.Length-1)]

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "✗ MSIX Build fehlgeschlagen!" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "✓ MSIX Build erfolgreich!" -ForegroundColor Green
}

if ($Help) {
    Show-Help
    exit 0
}

Check-Prerequisites
Build-MSIX
