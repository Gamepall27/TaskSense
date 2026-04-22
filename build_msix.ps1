# TaskSense MSIX Build Helper - PowerShell Script
# Dieses Skript vereinfacht den MSIX Build-Prozess

param(
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
    Write-Host "  -Help         : Diese Hilfe anzeigen"
    Write-Host "  -Sign         : Digitale Signatur hinzufügen"
    Write-Host "  -CertPath     : Pfad zum Zertifikat (.pfx)"
    Write-Host ""
    Write-Host "Beispiele:"
    Write-Host "  .\build_msix.ps1                              # Normaler Build"
    Write-Host "  .\build_msix.ps1 -Sign -CertPath cert.pfx     # Mit Signatur"
    Write-Host ""
}

function Check-Prerequisites {
    Write-Host "🔍 Prüfe Voraussetzungen..." -ForegroundColor Yellow
    
    # Prüfe Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python gefunden: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Python nicht gefunden!" -ForegroundColor Red
        Write-Host "  Installiere Python 3.8+ von https://www.python.org/" -ForegroundColor Yellow
        exit 1
    }
    
    # Prüfe MakeAppx
    try {
        $makeAppxPath = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\MakeAppx.exe"
        if (Test-Path $makeAppxPath) {
            Write-Host "✓ MakeAppx gefunden" -ForegroundColor Green
            # Füge zu PATH hinzu
            $env:Path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
        }
        else {
            Write-Host "⚠ MakeAppx nicht im Standard-Pfad gefunden" -ForegroundColor Yellow
            Write-Host "  Bitte Windows SDK installieren oder MakeAppx-Pfad prüfen" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠ MakeAppx-Prüfung fehlgeschlagen" -ForegroundColor Yellow
    }
    
    # Prüfe PyInstaller
    try {
        $pyinstallerVersion = pip show pyinstaller | Select-String "Version"
        if ($pyinstallerVersion) {
            Write-Host "✓ PyInstaller gefunden" -ForegroundColor Green
        }
        else {
            Write-Host "⚠ PyInstaller nicht gefunden - installiere: pip install pyinstaller" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠ PyInstaller-Prüfung fehlgeschlagen" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

function Build-MSIX {
    Write-Host "🔨 Starte MSIX Build-Prozess..." -ForegroundColor Cyan
    Write-Host ""
    
    # Baue Kommand
    $cmd = @("python", "build_msix.py")
    
    if ($Sign) {
        $cmd += "--sign"
        if ($CertPath) {
            $cmd += "--cert"
            $cmd += $CertPath
        }
    }
    
    Write-Host "Befehl: $($cmd -join ' ')" -ForegroundColor Gray
    Write-Host ""
    
    # Führe aus
    & $cmd[0] $cmd[1..($cmd.Length-1)]
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ MSIX Build erfolgreich!" -ForegroundColor Green
        
        # Zeige Ausgabedatei
        $msixPath = "dist\TaskSense.msix"
        if (Test-Path $msixPath) {
            $size = (Get-Item $msixPath).Length / 1MB
            Write-Host "  Ausgabe: $msixPath" -ForegroundColor Green
            Write-Host "  Größe: $([math]::Round($size, 2)) MB" -ForegroundColor Green
            
            Write-Host ""
            Write-Host "📚 Nächste Schritte:" -ForegroundColor Cyan
            Write-Host "  1. Öffne MSIX_BUILD_GUIDE.md für Details"
            Write-Host "  2. Registriere dich auf Microsoft Partner Center"
            Write-Host "  3. Lade die MSIX Datei hoch"
        }
    }
    else {
        Write-Host ""
        Write-Host "✗ MSIX Build fehlgeschlagen!" -ForegroundColor Red
        exit 1
    }
}

function Show-InfoPanel {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║         TaskSense - Microsoft Store MSIX Paketierung           ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Mit diesem Tool kannst du TaskSense als MSIX-Paket für den" -ForegroundColor Yellow
    Write-Host "Microsoft Store bauen und hochladen." -ForegroundColor Yellow
    Write-Host ""
}

# Main
Show-InfoPanel

if ($Help) {
    Show-Help
    exit 0
}

Check-Prerequisites
Build-MSIX

Write-Host ""
