# Release Checklist

Use this checklist before uploading any GitHub Release asset.

## Required contents

- `LICENSE`
- `NOTICE.md`
- `README.md`
- `translations/zh-CN.json`
- All runtime DLLs and executables needed to launch the app

## Required statements

- The release title must identify the package as a modified Chinese localization
  of OpenVSP.
- The release description must point to the exact source tag or source archive.
- The release description must not claim official NASA or OpenVSP affiliation.
- The binary package must preserve upstream license files for bundled content.

## Verification

- The release archive opens and launches from its top-level directory.
- `vsp.exe` can find `translations\\zh-CN.json` beside it.
- `LICENSE` and `NOTICE.md` are present inside the archive.
- The archive name matches the version being released.
