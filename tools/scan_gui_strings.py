#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source" / "OpenVSP"
DEFAULT_OUT = ROOT / "translations" / "gui-candidates.json"
DEFAULT_PATTERNS = [
    "src/gui_and_draw/**/*.cpp",
    "src/gui_and_draw/**/*.cxx",
    "src/gui_and_draw/**/*.C",
    "src/gui_and_draw/**/*.h",
    "src/gui_and_draw/**/*.H",
    "src/vsp_aero/Viewer/**/*.cpp",
    "src/vsp_aero/Viewer/**/*.cxx",
    "src/vsp_aero/Viewer/**/*.C",
    "src/vsp_aero/Viewer/**/*.h",
    "src/vsp_aero/Viewer/**/*.H",
]
STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def unescape_cpp(text: str) -> str:
    return bytes(text, "utf-8").decode("unicode_escape")


def should_skip(text: str) -> bool:
    if not text or text.startswith("#"):
        return True
    if text.startswith(("http://", "https://", "D:\\", "C:\\")):
        return True
    if text in {"", "\\n", "\\t"}:
        return True
    if text.startswith(("%", "*.", ".{")):
        return True
    if all(ch in "<>|+-*/=_:.,;()[]{} " for ch in text):
        return True
    return False


def scan_files(src_root: Path, patterns: list[str], min_len: int) -> list[dict[str, object]]:
    counts: Counter[str] = Counter()
    hits: defaultdict[str, set[str]] = defaultdict(set)
    for pattern in patterns:
        for path in src_root.glob(pattern):
            if not path.is_file():
                continue
            data = path.read_text(encoding="utf-8", errors="ignore")
            for m in STRING_RE.finditer(data):
                raw = m.group(1)
                if len(raw) < min_len:
                    continue
                try:
                    text = unescape_cpp(raw)
                except UnicodeDecodeError:
                    continue
                if should_skip(text):
                    continue
                counts[text] += 1
                hits[text].add(path.as_posix())
    rows = []
    for text, count in counts.most_common():
        rows.append(
            {
                "source": text,
                "hits": count,
                "utf8_len": len(text.encode("utf-8")),
                "ascii_len": len(text.encode("ascii", errors="ignore")),
                "files": sorted(hits[text]),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan OpenVSP GUI source strings on Windows")
    parser.add_argument("--source", default=DEFAULT_SOURCE, type=Path, help=f"OpenVSP source root, default: {DEFAULT_SOURCE}")
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path, help=f"output json file, default: {DEFAULT_OUT}")
    parser.add_argument("--min-len", type=int, default=3)
    parser.add_argument(
        "--pattern",
        action="append",
        default=None,
        help="glob pattern relative to source root; can be repeated",
    )
    args = parser.parse_args()
    if not args.source.exists():
        raise SystemExit(f"source root not found: {args.source}")
    patterns = args.pattern if args.pattern else DEFAULT_PATTERNS
    rows = scan_files(args.source, patterns, args.min_len)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
