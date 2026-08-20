# DDay Controls Tool Suite

A collection of engineering utilities for PLC and robot programmers. Available as a Windows desktop application and a Progressive Web App (PWA) for mobile and browser use.

**Version:** 2.2.0  
**Platform:** Windows 10/11 (desktop) · iOS · Android · any modern browser (PWA)

---

## Tools Included

### Scalar Converter
Convert values between decimal, hexadecimal, binary, and octal. Supports 8, 16, and 32-bit widths with signed/unsigned toggle, endian-aware byte breakdown, and copy formatting presets for Siemens, Allen-Bradley, Mitsubishi, FANUC, Python, C/C++, and more.

### ASCII Chart
Full ASCII reference table (0–127, optional 128–255 extended). Columns: Char, Dec, Hex, Oct, Bin, Name. Live search by character, decimal, hex (prefix `0x` or bare hex digits), or control name. Click any column header to copy that value with your chosen format preset.

### Engineering Calculator
Six calculators for controls work, on their own tabs:

- **Standard** — a plain decimal calculator: the four functions, powers, square root,
  reciprocal, remainder, memory keys, and parentheses. Results are rounded to 12 significant
  digits, so 0.1 + 0.2 reads as 0.3 rather than 0.30000000000000004.
- **Programmer** — a whole-number calculator over DEC, HEX, BIN, and OCT. Full operator set
  (`+ - * / % & | ^ ~ << >>` and parentheses) with C precedence, 8/16/32/64-bit words, and a
  signed/unsigned toggle. Division truncates toward zero and the remainder takes the sign of
  the dividend, so results match structured text rather than Python. Every step wraps to the
  selected word size, and an overflow is called out rather than hidden. The decimal point is
  deliberately disabled here — bases and word sizes have no meaning for 2.5.
- **Analog Scaling** — raw counts to engineering units and back, with presets for Siemens S7
  (0–27648 and bipolar), Allen-Bradley SLC 4–20 mA (3277–16384), plain 12/13/14/15/16-bit
  converters, and raw mA or volt signals. Reports percent of span, units per count, and
  whether the input sits outside the range, with optional clamping.
- **Ohm's Law** — enter any two of voltage, current, resistance, and power; the other two
  are solved.
- **Motor & Drive** — shaft torque in lb-ft and N-m, synchronous speed and slip, three- and
  single-phase real/apparent/reactive power, full-load current, and gearbox output speed and
  torque.
- **Encoder & Motion** — counts per revolution at x1/x2/x4 decode, distance per count through
  a leadscrew, roller, or rotary axis with an optional gear reduction, counts for a given
  travel, and encoder output frequency at speed.

Torque constants are derived from `P = T·ω` rather than the rounded 5252 and 9550, so the
imperial and metric figures agree with each other.

### FANUC I/O Tool
Generate FANUC robot I/O comment templates and KAREL loader scripts from a RoboGuide CSV or DDay XLSX template. Drag-and-drop file input, preview, and CSV/KAREL export.

---

## Installation (Windows)

1. Download the latest installer from the [Releases](../../releases) page
2. Run `DDay Controls Tool Suite Setup 2.2.0.exe`
3. Choose a full or custom installation (individual tools are optional)
4. Launch from the Start Menu or desktop shortcut

**Requirements:** Windows 10 or 11 (64-bit). No Python installation required — all dependencies are bundled.

---

## PWA (Mobile & Browser)

The Scalar Converter, Unit Converter, ASCII Chart, and Engineering Calculator are also available as a Progressive Web App:

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
pyinstaller --noconfirm --clean engineering_calculator.spec
pyinstaller --noconfirm --clean fanuc_io_tool.spec
pyinstaller --noconfirm --clean launcher.spec
```

Build the installer: open `installer.iss` in [Inno Setup 6](https://jrsoftware.org/isinfo.php) and compile.

### Releasing

Pushing a `v*` tag builds everything on a Windows runner and opens a **draft** release with the
installer attached — read the notes, then click Publish:

```bash
git tag v2.2.0
git push origin v2.2.0
```

The job first checks that the tag matches the version in `dday_controls_common.py`,
`installer.iss`, `build_all.bat`, and this README, and fails before building if any of them
disagree. To test a build without tagging, run the workflow by hand from the Actions tab — that
uploads the installer to the run instead of creating a release.

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
