#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "source" / "OpenVSP"
DEFAULT_DICT = ROOT / "translations" / "zh-CN.json"
DEFAULT_OUT = ROOT / "translations" / "gui-untranslated.json"
DEFAULT_PRESERVED_OUT = ROOT / "translations" / "gui-preserved.json"
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

# These labels are registered outside gui_and_draw and displayed by ManageGeomScreen.
REQUIRED_DYNAMIC_KEYS = {
    "POD", "FUSELAGE", "WING", "STACK", "BLANK", "ELLIPSOID",
    "BODYOFREVOLUTION", "HUMAN", "PROP", "GEAR", "HINGE", "CONFORMAL",
    "ROUTING", "AUXILIARY", "COBRA", "Box", "BoxGroup", "Cone", "Disk",
    "Duct", "OnOffExample", "PodMan", "Seat", "SeatGroup", "TransportFuse",
}

PRESERVED = {
    "0D", "0N", "1/C", "1/F", "1/K", "1/R", "2D", "3D", "CM", "FT", "IN",
    "M", "MM", "YD", "G", "E", "LE", "T/C", "MAC", "CLi", "FEM", "VSPAERO",
    "FOUR_SERIES", "SIX_SERIES", "CST_AIRFOIL", "KARMAN_TREFFTZ",
    "FOUR_DIGIT_MOD", "FIVE_DIGIT", "FIVE_DIGIT_MOD", "16_SERIES", "AC25_773",
    "63A", "64A", "65A", "G1", "LMN", "RST", "[X]", "[Y]",
    ".csv", ".curv", ".igs", ".msh", ".p3d", ".srf", ".stl", ".stp",
    "Ba", "BFT (slug, ft)", "C_f (1e-3)", "CGS (g, cm)", "f", "ft/s",
    "inchHg", "kg/m-s", "km/hr", "L/C", "L_ref (cm)", "L_ref (ft)",
    "L_ref (in)", "L_ref (LU)", "L_ref (m)", "L_ref (mm)", "L_ref (yd)",
    "m/s", "mB", "mmH20", "mmHg", "MPA (tonne, mm)", "mph", "Q",
    "Re (1e6)", "R_inner", "R_outer", "S_wet (ft2)", "SI (kg, m)",
    "slug/ft-s", "Surf_", "t", "t/c or l/d", "Taw/Tw", "Te/Tw",
    "Ixx", "Iyy", "Izy", "Izz", "Nkey", "[0, N]",
    "C0", "C1", "C2", "CD", "DATCOM", "KEAS", "KTAS", "KG",
    "LBFSEC2IN", "LBM", "USAF 1966", "OML R", "OML S", "OML T",
    "OML U", "OML V",
    "T", "N", "a", "R//L", "S", "T//B", "Xmax", "Xmin", "Ymax", "Ymin",
    "Y/T", "TE", "A0", "Beta 3/4", "BMI", "C_D", "CAD",
    "CLMax2D", "Clo2D", "Drim", "Eta",
    "FF", "Gamma", "Half Length (h/D)", "Hs", "Ixy", "Ixz", "Iyz", "N2",
    "N_X", "N_Y", "N_Z", "NASCART", "Num_U", "Num_W",
    "PowAL", "PowAU", "PowNL", "PowNU", "PowX", "r_0", "r_flap/R",
    "Re/L", "RPM", "Sitting H / H", "SLR",
    "U01", "U0N", "Value01", "Value0N", "Wrim", "Ws", "X <", "X <=", "X >",
    "X >=", "XoC", "Y <", "Y <=", "Y >", "Y >=", "Z <", "Z <=",
    "Z >", "Z >=",
    "Blasius", "Hoerner", "Kroo", "Shevell", "Williams",
    ".dat", ".facet", ".key", ".m", ".obj", ".poly", ".tkey", ".tri", ".txt", ".vspgeom",
    "Ae", "Amin", "Amin W", "C/R", "C_P/R", "C_T/R", "Cave", "CD0_w", "Cen",
    "Dim1", "Dim2", "Dim3", "Dim4", "Dim5", "Dim6", "g", "ISym = 0", "ISym = 1",
    "I xx", "I xy", "I xz", "I yy", "I yz", "I zz", "lbf s^2/in", "lbm", "Rng",
    "Spine_Normal", "Stot", "XY_Abs", "XY_Body", "XZ_Abs", "XZ_Body", "YZ_Abs", "YZ_Body",
}

VISIBLE_CALLS = {
    "BasicScreen", "GeomScreen", "TabScreen", "AddTab", "AddItem",
    "AddButton", "AddInput", "AddOutput", "AddSlider", "AddChoice",
    "AddDividerBox", "fl_alert", "fl_message", "fl_choice", "copy_label",
    "label", "SetButtonName", "Alert", "FileChooser",
    "Update", "SetTitle", "SetLabel", "SetText", "AddLabel", "copy_tooltip", "append",
    "AddOutputText",
}
STRING_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def strip_comments(data: str) -> str:
    out: list[str] = []
    i = 0
    in_string = False
    while i < len(data):
        if in_string:
            out.append(data[i])
            if data[i] == "\\" and i + 1 < len(data):
                i += 1
                out.append(data[i])
            elif data[i] == '"':
                in_string = False
            i += 1
            continue
        if data[i] == '"':
            in_string = True
            out.append(data[i])
            i += 1
        elif data.startswith("//", i):
            end = data.find("\n", i)
            if end < 0:
                break
            out.append("\n")
            i = end + 1
        elif data.startswith("/*", i):
            end = data.find("*/", i + 2)
            if end < 0:
                break
            out.extend("\n" for ch in data[i:end + 2] if ch == "\n")
            i = end + 2
        else:
            out.append(data[i])
            i += 1
    return "".join(out)


def visible_calls(data: str):
    clean = strip_comments(data)
    call_re = re.compile(r"\b(" + "|".join(sorted(VISIBLE_CALLS, key=len, reverse=True)) + r")\s*\(")
    for match in call_re.finditer(clean):
        start = match.end() - 1
        depth = 0
        in_string = False
        i = start
        while i < len(clean):
            ch = clean[i]
            if in_string:
                if ch == "\\":
                    i += 2
                    continue
                if ch == '"':
                    in_string = False
            elif ch == '"':
                in_string = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    yield match.group(1), clean[start:i + 1], clean.count("\n", 0, match.start()) + 1
                    break
            i += 1


def unescape_cpp(value: str) -> str:
    return bytes(value, "utf-8").decode("unicode_escape")


def is_translatable(value: str) -> bool:
    text = value.strip()
    if text in PRESERVED:
        return False
    if not text or text.startswith(("@", "%", "*.", "http://", "https://")):
        return False
    if re.fullmatch(r"[0-9.+\-/* ]+", text):
        return False
    if re.fullmatch(r"[XYZIJKUWLR]+", text):
        return False
    if re.fullmatch(r"[<>=|()[\]{}:;,.+\-/*_ ]+", text):
        return False
    if re.fullmatch(r"(?:mm|cm|m|in|ft|yd|kg|sec|SI|LU)", text):
        return False
    if re.fullmatch(r"[^ ]+\.(?:html|dat|facet|key|m|obj|poly|tkey|tri|txt|vspgeom)", text, re.IGNORECASE):
        return False
    if re.fullmatch(r"(?:1/)?(?:mm|cm|m|in|ft|yd|Unitless)", text):
        return False
    if re.fullmatch(r"(?:g/cm\^3|kg/m\^3|lbm/(?:ft|in)\^3|slug/ft\^3|lbf s\^2/in\^4|Pa|kPa|MPa|psi|psf|t/mm\^3)", text):
        return False
    return bool(re.search(r"[A-Za-z]", text))


def audit(source: Path, translations: dict[str, str], patterns: list[str]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    folded_translations = {key.casefold() for key in translations}
    hits: dict[str, list[dict[str, object]]] = defaultdict(list)
    preserved_hits: dict[str, list[dict[str, object]]] = defaultdict(list)
    for pattern in patterns:
        for path in source.glob(pattern):
            if not path.is_file():
                continue
            data = path.read_text(encoding="utf-8", errors="ignore")
            for kind, call_text, line_no in visible_calls(data):
                for match in STRING_RE.finditer(call_text):
                    try:
                        text = unescape_cpp(match.group(1))
                    except UnicodeDecodeError:
                        continue
                    location = {
                        "file": path.relative_to(source).as_posix(),
                        "line": line_no,
                        "kind": kind,
                    }
                    normalized = text.strip()
                    if normalized in PRESERVED:
                        preserved_hits[normalized].append(location)
                    elif (is_translatable(text) and text not in translations
                          and normalized not in translations
                          and text.casefold() not in folded_translations
                          and normalized.casefold() not in folded_translations):
                        hits[normalized].append(location)
    for text in REQUIRED_DYNAMIC_KEYS:
        if text not in translations and text.casefold() not in folded_translations:
            hits[text].append({"file": "<runtime geometry registry>", "line": 0, "kind": "dynamic"})
    untranslated = [
        {"source": text, "hits": len(locations), "locations": locations}
        for text, locations in sorted(hits.items(), key=lambda item: (-len(item[1]), item[0].lower()))
    ]
    preserved = [
        {"source": text, "reason": "technical identifier, unit, symbol, or proper name", "hits": len(locations), "locations": locations}
        for text, locations in sorted(preserved_hits.items())
    ]
    return untranslated, preserved


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit untranslated OpenVSP GUI literals")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--dict", type=Path, default=DEFAULT_DICT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--preserved-out", type=Path, default=DEFAULT_PRESERVED_OUT)
    parser.add_argument(
        "--pattern",
        action="append",
        default=None,
        help="glob pattern relative to the source root; can be repeated",
    )
    args = parser.parse_args()

    patterns = args.pattern if args.pattern else DEFAULT_PATTERNS
    translations = json.loads(args.dict.read_text(encoding="utf-8"))
    rows, preserved = audit(args.source, translations, patterns)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    args.preserved_out.write_text(json.dumps(preserved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"untranslated GUI literals: {len(rows)}")
    print(f"wrote {args.out}")
    print(f"preserved GUI literals: {len(preserved)}")
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
