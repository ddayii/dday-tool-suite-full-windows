# DDay Controls Tool Suite

A collection of engineering utilities for PLC and robot programmers. Available as a Windows desktop application and a Progressive Web App (PWA) for mobile and browser use.

**Version:** 2.1.1  
**Platform:** Windows 10/11 (desktop) · iOS · Android · any modern browser (PWA)

---

## Tools Included

### Scalar Converter
Convert values between decimal, hexadecimal, binary, and octal. Supports 8, 16, and 32-bit widths with signed/unsigned toggle, endian-aware byte breakdown, and copy formatting presets for Siemens, Allen-Bradley, Mitsubishi, FANUC, Python, C/C++, and more.

### ASCII Chart
Full ASCII reference table (0–127, optional 128–255 extended). Columns: Char, Dec, Hex, Oct, Bin, Name. Live search by character, decimal, hex (prefix `0x` or bare hex digits), or control name. Click any column header to copy that value with your chosen format preset.

### FANUC I/O Tool
Generate FANUC robot I/O comment templates and KAREL loader scripts from a RoboGuide CSV or DDay XLSX template. Drag-and-drop file input, preview, and CSV/KAREL export.

---

## Installation (Windows)

1. Download the latest installer from the [Releases](../../releases) page
2. Run `DDay Controls Tool Suite Setup 2.1.1.exe`
3. Choose a full or custom installation (individual tools are optional)
4. Launch from the Start Menu or desktop shortcut

**Requirements:** Windows 10 or 11 (64-bit). No Python installation required — all dependencies are bundled.

---

## PWA (Mobile & Browser)

The Scalar Converter, Unit Converter, and ASCII Chart are also available as a Progressive Web App:

**[https://ddayii.github.io/dday_tool_suite_pwa](https://ddayii.github.io/dday_tool_suite_pwa)**

Works offline after first load. Install to your home screen for a native app experience:
- **iOS:** Safari → Share → Add to Home Screen
- **Android:** Chrome → menu → Add to Home Screen
- **Desktop:** address bar install icon in Chrome or Edge

---

## Building from Source

**Requirements:** Python 3.11+, PySide6, PyInstaller, openpyxl

```bash
pip install pyside6 pyinstaller openpyxl
```

Build all executables:
```bash
pyinstaller --noconfirm --clean converter_tool.spec
pyinstaller --noconfirm --clean ascii_chart.spec
pyinstaller --noconfirm --clean fanuc_io_tool.spec
pyinstaller --noconfirm --clean launcher.spec
```

Build the installer: open `installer.iss` in [Inno Setup 6](https://jrsoftware.org/isinfo.php) and compile.

---

## Copy Format Presets

The converter and ASCII chart include copy formatting for:

| Platform | Examples |
|----------|---------|
| Siemens | `L#`, `16#`, `2#`, `T#` |
| Allen-Bradley | `16#` |
| Mitsubishi | `H`, `B` |
| FANUC Robot | `B`, `H` |
| Python | `0x`, `0b`, `0o` |
| C / C++ | `0x`, `0b` |
| Java / JavaScript | `0x` |

Custom prefix/suffix fields allow any format not covered by the presets. Format groups can be reordered and toggled in the Copy Format Editor (Options menu).

---

## License

This software is provided as-is for personal and commercial use. Redistribution of modified versions requires attribution.

---

*DDay Controls · ddaycontrols@gmail.com*
