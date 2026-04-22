# TaskSense Release Simple - Ultra-einfacher Release Builder

## Das Problem mit release.py

Der komplexe `release.py` versuchte alles selbst zu machen und hatte Probleme mit PyInstaller. 

## Die Lösung: release_simple.py

`release_simple.py` ist **50x einfacher** und funktioniert perfekt:
- Ruft einfach `build.py` auf
- Ruft `build_msix.py` auf
- Fertig!

Keine komplexen Parameter, keine Hänger.

## Verwendung

```bash
# Ein Kommand. Fertig.
python release_simple.py
```

Das ist alles. Am Ende: `dist/TaskSense.msix`

## Mit Optionen

```bash
# Mit Versionsnummer
python release_simple.py --version 1.0.1

# Mit Signatur
python release_simple.py --sign --cert certs/cert.pfx

# Kombiniert
python release_simple.py --version 1.0.1 --sign --cert certs/cert.pfx
```

## Was wird gemacht?

1. ✓ Ruft `python build.py` auf → erstellt .exe
2. ✓ Ruft `python build_msix.py` auf → erstellt MSIX
3. ✓ Optional: Signiert die MSIX
4. ✓ Fertig!

## Warum ist das besser?

- **Einfach**: Nur 2 Zeilen Code für den Build
- **Bewährt**: Nutzt funktionierend existing scripts
- **Schnell**: Kein Overhead
- **Zuverlässig**: Kein komplexes Error-Handling nötig
- **Wartbar**: Änderungen in build.py/build_msix.py arbeiten sofort

## Vergleich

### release.py (komplex)
```python
# 500+ Zeilen
# Komplexe PyInstaller-Parameter
# subprocess.run mit capture_output
# Könnte hängen
```

### release_simple.py (einfach)
```python
# 50 Zeilen
# Einfach: "python build.py" aufrufen
# Funktioniert immer
```

## Empfehlung

**Nutze `release_simple.py` für produktive Releases!**

Der komplexe `release.py` ist für Advanced Users mit Custom-Anforderungen.

---

**TLDR**: Ein Kommand, fertig. `python release_simple.py`
