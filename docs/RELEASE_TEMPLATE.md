# Release Template

## Title

VSP-Chinese vX.Y.Z for Windows x64

## Summary

OpenVSP 3.51.2 简体中文汉化版。

## Downloads

- `OpenVSP-X.Y.Z-zh-CN-win64.zip`
- Source code archive for the matching tag

## Included

- Full runtime directory
- `LICENSE`
- `NOTICE.md`
- `translations/zh-CN.json`

## Notes

- This is a modified localization of OpenVSP, not an official NASA release.
- Keep the extracted directory structure intact.
- If Chinese text does not appear, confirm that `translations/zh-CN.json` is next to `vsp.exe` or inside `translations/`.

## Validation

- GUI translation audit completed with `untranslated GUI literals: 0`
- Windows package built with `build-windows.ps1`
