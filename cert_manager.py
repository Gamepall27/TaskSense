"""
Hilfsskript zur Verwaltung von MSIX-Zertifikaten.

Dieses Skript hilft bei:
- Erstellung eines selbstsignierenden Test-Zertifikats
- Verwaltung von Zertifikaten
- Vorbereitung für Microsoft Store-Upload
"""

import subprocess
import sys
import os
from pathlib import Path


def create_test_certificate(output_dir: str = "certs"):
    """Erstellt ein selbstsigniertes Test-Zertifikat."""
    print("🔐 Erstelle selbstsigniertes Test-Zertifikat...")
    
    Path(output_dir).mkdir(exist_ok=True)
    cert_path = Path(output_dir) / "TaskSense_TestCert.pfx"
    cert_cer = Path(output_dir) / "TaskSense_TestCert.cer"
    
    # Prüfe ob bereits vorhanden
    if cert_path.exists():
        print(f"✓ Zertifikat existiert bereits: {cert_path}")
        return str(cert_path)
    
    try:
        # Erstelle selbstsigniertes Zertifikat mit MakeCert
        cmd = [
            "makecert",
            "-r",  # Selbstsigniert
            "-h", "0",  # Hash Algorithmus
            "-o", "TaskSense_TestCert",  # Output Name
            "-eku", "1.3.6.1.5.5.7.3.3",  # Code Signing
            "-n", "CN=Gamepall27, C=DE",  # Subject Name
            "-sv", str(Path(output_dir) / "TaskSense_TestCert.pvk"),
            str(cert_cer)
        ]
        
        print(f"Befehl: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ makecert Fehler: {result.stderr}")
            print("\nAlternativ: Verwende NewCertificateExpress Tool")
            return None
        
        # Konvertiere zu PFX
        cmd_pvk2pfx = [
            "pvk2pfx",
            "-pvk", str(Path(output_dir) / "TaskSense_TestCert.pvk"),
            "-spc", str(cert_cer),
            "-pfx", str(cert_path),
            "-po", "password",  # Passwort
            "-f"
        ]
        
        result = subprocess.run(cmd_pvk2pfx, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Zertifikat erstellt: {cert_path}")
            print(f"  Passwort: password")
            print(f"  CER-Datei: {cert_cer}")
            return str(cert_path)
        else:
            print(f"✗ pvk2pfx Fehler: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("✗ makecert Tool nicht gefunden!")
        print("  Installiere Windows SDK für diese Tools")
        print("\nAlternativ: Verwende PowerShell New-SelfSignedCertificate")
        return None


def create_with_powershell(output_dir: str = "certs"):
    """Erstellt Zertifikat mit PowerShell (Windows 10+)."""
    print("🔐 Erstelle Test-Zertifikat mit PowerShell...")
    
    Path(output_dir).mkdir(exist_ok=True)
    cert_path = Path(output_dir) / "TaskSense_TestCert.pfx"
    
    if cert_path.exists():
        print(f"✓ Zertifikat existiert bereits: {cert_path}")
        return str(cert_path)
    
    ps_script = """
$cert = New-SelfSignedCertificate -Type Custom `
    -Subject "CN=Gamepall27, C=DE" `
    -KeyUsage DigitalSignature `
    -FriendlyName "TaskSense Test Cert" `
    -CertStoreLocation "Cert:\\CurrentUser\\My" `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")

$pwd = ConvertTo-SecureString -String "password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "certs/TaskSense_TestCert.pfx" -Password $pwd

Write-Host "Zertifikat erstellt: certs/TaskSense_TestCert.pfx"
Write-Host "Passwort: password"
"""
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and cert_path.exists():
            print(f"✓ Zertifikat erstellt: {cert_path}")
            print(f"  Passwort: password")
            return str(cert_path)
        else:
            print(f"✗ PowerShell Fehler: {result.stderr}")
            return None
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return None


def list_certificates():
    """Listet installierte Code-Signing Zertifikate auf."""
    print("📋 Installierte Code-Signing Zertifikate:")
    
    try:
        # Auflisten von lokalen Zertifikaten
        ps_cmd = """
Get-ChildItem -Path Cert:\\CurrentUser\\My | 
Where-Object {$_.EnhancedKeyUsageList -like "*Code Signing*"} | 
Select-Object FriendlyName, Thumbprint, NotAfter
"""
        
        result = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        else:
            print("Keine Code-Signing Zertifikate gefunden")
            
    except Exception as e:
        print(f"Fehler: {e}")


def main():
    """Haupteinstiegspunkt."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="TaskSense MSIX Zertifikat Manager"
    )
    parser.add_argument(
        "action",
        choices=["create", "create-ps", "list"],
        help="Aktion: create (makecert), create-ps (PowerShell), oder list"
    )
    parser.add_argument(
        "--output",
        default="certs",
        help="Ausgabeverzeichnis für Zertifikate"
    )
    
    args = parser.parse_args()
    
    if args.action == "create":
        cert_path = create_test_certificate(args.output)
        if cert_path:
            print(f"\nNächster Schritt:")
            print(f"  python build_msix.py --sign --cert {cert_path}")
    elif args.action == "create-ps":
        cert_path = create_with_powershell(args.output)
        if cert_path:
            print(f"\nNächster Schritt:")
            print(f"  python build_msix.py --sign --cert {cert_path}")
    elif args.action == "list":
        list_certificates()


if __name__ == "__main__":
    print("TaskSense MSIX Zertifikat Manager")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\nVerwendung:")
        print("  python cert_manager.py create       # MakeCert verwenden")
        print("  python cert_manager.py create-ps    # PowerShell verwenden")
        print("  python cert_manager.py list         # Zertifikate auflisten")
        sys.exit(1)
    
    main()
