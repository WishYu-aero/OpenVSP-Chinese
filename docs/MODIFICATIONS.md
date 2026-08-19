# Modification Map

This file maps the VSP-Chinese changes against the upstream OpenVSP source so
future contributors can see where the localization layer lives and how the
release is assembled.

## Scope

VSP-Chinese is a modified redistribution of OpenVSP 3.51.2. The upstream
source remains in `source/OpenVSP/`; the Chinese localization layer and release
support files are added on top of it.

## Source changes

### `source/OpenVSP/src/gui_and_draw/Localization.cpp`

This is the core runtime localization loader. It now:

- Loads translations from `translations/zh-CN.json`
- Supports an `OPENVSP_TRANSLATIONS` override
- Uses UTF-8 / Windows file loading paths
- Provides lookup helpers used by GUI text, menus, browser headers, and
  translated status strings

### `source/OpenVSP/src/vsp_aero/Viewer/ViewerLocalization.C`

This adds localization support to the standalone VSPAERO Viewer. It walks the
live FLTK widget tree and applies translations to:

- Window titles
- Menu items
- Widget labels

## Translation data

### `translations/zh-CN.json`

The Simplified Chinese translation dictionary. This is the main user-facing
payload of the localization work.

## Validation tools

### `tools/scan_gui_strings.py`

Scans GUI strings and generates candidate translation data for review.

### `tools/audit_gui_translation.py`

Checks translation completeness and produces audit outputs for untranslated and
preserved strings.

## Packaging and release support

### `build-windows.ps1`

Builds OpenVSP, installs the runtime tree, and copies the translation data plus
license and notice files into the release directory.

### `docs/WINDOWS_BUILD.md`

Documents the build environment and the expected release layout.

### `docs/RELEASE_CHECKLIST.md`

Provides the release-time checklist for GitHub Releases.

## Attribution

Originator: [WishYu-aero](https://github.com/WishYu-aero) / OpenVSP-Chinese
contributors.

All modifications listed here are distributed under the same NOSA 1.3 terms as
the upstream OpenVSP source unless a file states otherwise.
