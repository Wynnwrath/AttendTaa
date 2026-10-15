#!/usr/bin/env python3
"""AttendTa v2 UI consistency checker.

Foundation rules (F*) are always fatal. Page rules (P*) are baseline
(informational, non-fatal) unless --strict is passed, in which case they
are fatal too.

Usage:
    python check_v2_ui.py [--strict]
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

V2_DIR = Path(__file__).resolve().parents[1]
ASSETS = V2_DIR / "assets"

FAMILIES = ["moss", "indigo", "teal", "violet", "crimson", "orange", "slate", "amber"]
INK_SEAM = [
    "index.html",
    "account/login.html",
    "account/register.html",
    "certificates/view.html",
]

ISSUES = []
INFO = {"contrast": [], "export": []}
STRICT = False


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(V2_DIR)).replace("\\", "/")
    except Exception:
        return str(path)


def add(rule, path, line, message):
    fatal = rule.startswith("F") or (STRICT and rule.startswith("P"))
    ISSUES.append({
        "fatal": fatal,
        "rule": rule,
        "path": rel(path),
        "line": int(line or 0),
        "message": message,
    })


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def line_of(text, needle):
    idx = text.find(needle)
    return text.count("\n", 0, idx) + 1 if idx >= 0 else 0


def pages():
    return sorted(V2_DIR.rglob("*.html"))


# --------------------------------------------------------------------------
# FOUNDATION (always fatal)
# --------------------------------------------------------------------------
def check_F1():
    required = [
        "assets/tokens.css", "assets/components.css", "assets/app.js",
        "assets/icons.svg", "assets/tailwind.config.js",
        "assets/DESIGN-TOKENS.md", "RAZOR-PORT.md",
    ]
    for name in required:
        if not (V2_DIR / name).exists():
            add("F1", name, 0, "missing required file")


F2_NEEDLES = [
    "display=swap", ":focus-visible", "prefers-reduced-motion", "scale(0.96)",
    "--shadow-flash", "--motion-fast", "--motion-base", "--motion-slow",
    "--ease-standard", "--radius-sm", "--radius-md", "--radius-lg",
    "--radius-pill", "--density-text", "--z-nav", "--z-sticky", "--z-drawer",
    "--z-modal", "--ink-primary", "--status-rose",
]
for _f in FAMILIES:
    F2_NEEDLES += [f"--event-{_f}-deep", f"--event-{_f}-subtle", f"--event-{_f}:"]


def check_F2():
    p = ASSETS / "tokens.css"
    txt = read_text(p)
    if not txt:
        add("F2", p, 0, "tokens.css missing or unreadable")
        return
    for n in F2_NEEDLES:
        if n not in txt:
            add("F2", p, 0, f"missing token/marker: {n}")


F3_NEEDLES = [
    "skip-link", ".icon", ".btn", "btn--primary", "btn--accent", "btn--secondary",
    "btn--ghost", "btn--danger", "btn--sm", "btn--lg", "field-label", "field-help",
    "field-error", ".input", ".select", ".textarea", ".checkbox", ".switch",
    "card-hairline", "card-elevated", "table-ledger", "table-ledger--cards",
    "badge--accent", "status-pill", ".tabs", "breadcrumb", ".drawer", ".sidenav",
    ".menu", ".dialog", ".toast", "empty-state", "skeleton", "timeline",
    ".gauge", ".steps", "viewfinder", "pass-card", "meta-cluster", "live-band",
    ".kpi", "gate-flash", "tap-target", "@media print",
]


def check_F3():
    comp = ASSETS / "components.css"
    txt = read_text(comp)
    if not txt:
        add("F3", comp, 0, "components.css missing or unreadable")
    else:
        for n in F3_NEEDLES:
            if n not in txt:
                add("F3", comp, 0, f"missing selector/marker: {n}")
    for p in (comp, ASSETS / "tokens.css"):
        t = read_text(p)
        m = re.search(r"transition\s*:\s*all\b", t)
        if m:
            add("F3", p, line_of(t, m.group(0)), "forbidden 'transition: all'")


F4_NEEDLES = [
    "Ta.store", "Ta.toast", "Ta.dialog", "Ta.nav", "Ta.sidebar", "Ta.drawer",
    "Ta.tabs", "Ta.menu", "Ta.table", "Ta.form", "Ta.kiosk", "Ta.export",
    "Ta.motion", "Ta.fonts", "attendta:v2:", "prefers-reduced-motion", "'use strict'",
]


def check_F4():
    p = ASSETS / "app.js"
    txt = read_text(p)
    if not txt:
        add("F4", p, 0, "app.js missing or unreadable")
        return
    for n in F4_NEEDLES:
        if n not in txt:
            add("F4", p, 0, f"missing marker: {n}")
    for bad in ("alert(", "onclick="):
        if bad in txt:
            add("F4", p, line_of(txt, bad), f"forbidden '{bad}'")


def check_F5():
    p = ASSETS / "icons.svg"
    if not p.exists():
        add("F5", p, 0, "icons.svg missing")
        return
    try:
        root = ET.parse(p).getroot()
    except Exception as exc:
        add("F5", p, 0, f"XML parse error: {exc}")
        return
    syms = [e for e in root.iter() if e.tag.split("}")[-1] == "symbol"]
    ids = [s.get("id") for s in syms]
    if len(syms) < 48:
        add("F5", p, 0, f"only {len(syms)} symbols (<48)")
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        add("F5", p, 0, f"duplicate symbol ids: {dups}")


F6_NEEDLES = [
    "tailwind.config", "var(--font-body)", "--event-moss", "borderRadius",
    "boxShadow", "transitionProperty",
]


def check_F6():
    p = ASSETS / "tailwind.config.js"
    txt = read_text(p)
    if not txt:
        add("F6", p, 0, "tailwind.config.js missing or unreadable")
        return
    for n in F6_NEEDLES:
        if n not in txt:
            add("F6", p, 0, f"missing marker: {n}")
    if "transition-all" in txt:
        add("F6", p, line_of(txt, "transition-all"), "forbidden 'transition-all'")


HEX_RE = re.compile(r"--([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})")


def _lum(h):
    h = h.lstrip("#")
    parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def chan(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (chan(x) for x in parts)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check_F7():
    p = ASSETS / "tokens.css"
    txt = read_text(p)
    if not txt:
        add("F7", p, 0, "tokens.css missing or unreadable")
        return
    colors = {}
    for name, hexv in HEX_RE.findall(txt):
        colors.setdefault("--" + name, hexv)
    pairs = [
        ("--ink-primary", "--canvas-surface", 4.5),
        ("--ink-secondary", "--canvas-surface", 4.5),
        ("--ink-muted", "--canvas-surface", 4.5),
        ("--ink-muted", "--canvas-ground", 4.5),
        ("--accent-amber-deep", "--canvas-surface", 4.5),
        ("--accent-amber", "--canvas-surface", 3.0),
        ("--status-emerald-text", "--canvas-surface", 4.5),
        ("--status-emerald", "--canvas-surface", 3.0),
        ("--status-rose", "--canvas-surface", 4.5),
        ("--status-neutral", "--canvas-surface", 4.5),
    ]
    for f in FAMILIES:
        pairs += [
            (f"--event-{f}", "--canvas-surface", 3.0),
            (f"--event-{f}-deep", "--canvas-surface", 4.5),
            (f"--event-{f}-deep", f"--event-{f}-subtle", 4.5),
        ]
    for fg, bg, thr in pairs:
        if fg not in colors or bg not in colors:
            add("F7", p, 0, f"missing color(s): {fg} / {bg}")
            continue
        r = _ratio(colors[fg], colors[bg])
        if r + 1e-9 < thr:
            add("F7", p, 0, f"contrast {fg} on {bg} = {r:.2f} (need {thr})")
    if "--ink-faint" in colors and "--canvas-surface" in colors:
        r = _ratio(colors["--ink-faint"], colors["--canvas-surface"])
        INFO["contrast"].append(
            f"--ink-faint on --canvas-surface = {r:.2f} — decorative — never text")


def check_F8():
    p = ASSETS / "DESIGN-TOKENS.md"
    txt = read_text(p)
    if not txt:
        add("F8", p, 0, "DESIGN-TOKENS.md missing or unreadable")
        return
    for f in FAMILIES:
        if f not in txt:
            add("F8", p, 0, f"missing family mention: {f}")
    for n in ("Do Not Use For", "AA"):
        if n not in txt:
            add("F8", p, 0, f"missing marker: {n}")


# --------------------------------------------------------------------------
# PAGE (baseline unless --strict)
# --------------------------------------------------------------------------
CONTROL_RE = re.compile(r"<(input|select|textarea)\b[^>]*>", re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
TH_RE = re.compile(r"<th\b[^>]*>", re.I)
LINK_RE = re.compile(r'\b(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "javascript:", "data:", "#", "//")


def check_P1(page, txt):
    for asset in ("assets/tokens.css", "assets/components.css", "assets/app.js"):
        if asset not in txt:
            add("P1", page, 0, f"missing link/ref: {asset}")
    m = re.search(r"tailwind\.config\s*=", txt)
    if m:
        add("P1", page, line_of(txt, m.group(0)), "inline tailwind.config present")


def check_P2(page, txt):
    pat = re.compile(r"\bon(click|change|submit|input|keydown|keyup|keypress)=")
    for i, line in enumerate(txt.splitlines(), 1):
        for m in pat.finditer(line):
            add("P2", page, i, f"inline handler on{m.group(1)}=")


def check_P3(page, txt):
    native = re.compile(r"(?<![\w.$])(?:alert|confirm)\s*\(")
    for i, line in enumerate(txt.splitlines(), 1):
        for m in native.finditer(line):
            add("P3", page, i, f"forbidden native call '{m.group(0).strip()}'")


def check_P4(page, txt):
    for i, line in enumerate(txt.splitlines(), 1):
        if "transition-all" in line:
            add("P4", page, i, "forbidden 'transition-all'")
        if "#000" in line:
            add("P4", page, i, "forbidden color '#000'")
        if re.search(r"(?:text|bg)-black\b", line):
            add("P4", page, i, "forbidden text-black/bg-black")


def check_P5(page, txt):
    seen = {}
    for i, line in enumerate(txt.splitlines(), 1):
        for mid in re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', line):
            if mid in seen:
                add("P5", page, i, f"duplicate id '{mid}' (first at line {seen[mid]})")
            else:
                seen[mid] = i
    label_for = set(re.findall(
        r'<label\b[^>]*\bfor\s*=\s*["\']([^"\']+)["\']', txt, re.I))
    for i, line in enumerate(txt.splitlines(), 1):
        for m in IMG_RE.finditer(line):
            tag = m.group(0)
            if not re.search(r"\balt\s*=", tag):
                add("P5", page, i, "<img> missing alt")
            if not re.search(r"\bwidth\s*=", tag) or not re.search(r"\bheight\s*=", tag):
                add("P5", page, i, "<img> missing width/height")
        for m in TH_RE.finditer(line):
            if not re.search(r"\bscope\s*=", m.group(0)):
                add("P5", page, i, "<th> missing scope")
        for m in CONTROL_RE.finditer(line):
            tag = m.group(0)
            kind = m.group(1).lower()
            typ = re.search(r'\btype\s*=\s*["\']([^"\']+)["\']', tag, re.I)
            if kind == "input" and typ and typ.group(1).lower() == "hidden":
                continue
            if re.search(r"\baria-label\s*=", tag, re.I):
                continue
            idm = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', tag)
            if idm and idm.group(1) in label_for:
                continue
            add("P5", page, i, f"<{kind}> without label/aria-label")
    h1 = len(re.findall(r"<h1\b", txt, re.I))
    if h1 != 1:
        add("P5", page, 0, f"<h1> count = {h1} (expected 1)")


def check_P6(page, txt):
    login_ids = {"username", "email", "studentnumber"}
    for i, line in enumerate(txt.splitlines(), 1):
        if re.search(r'href\s*=\s*["\']#["\']', line):
            add("P6", page, i, 'href="#" placeholder link')
        for m in CONTROL_RE.finditer(line):
            tag = m.group(0)
            typ = re.search(r'\btype\s*=\s*["\']([^"\']+)["\']', tag, re.I)
            val = re.search(r'\bvalue\s*=\s*["\']([^"\']*)["\']', tag, re.I)
            if typ and typ.group(1).lower() == "password" and val and val.group(1).strip():
                add("P6", page, i, "password input has non-empty value")
            idm = re.search(r'\bid\s*=\s*["\']([^"\']+)["\']', tag, re.I)
            if idm and idm.group(1).lower() in login_ids and val and val.group(1).strip():
                add("P6", page, i, f"login field #{idm.group(1)} has non-empty value")


def check_P7(page, txt):
    small = re.compile(r"text-\[(?:9|10)px\]")
    muted = re.compile(r"text-(?:slate-400|ink-faint)")
    for i, line in enumerate(txt.splitlines(), 1):
        if small.search(line):
            add("P7", page, i, "tiny text utility text-[9px]/text-[10px]")
        if muted.search(line):
            add("P7", page, i, "muted text utility text-slate-400/text-ink-faint")


def check_P8(page, txt):
    pat = re.compile(r"rounded-(?:2xl|3xl|xl|full)\b")
    for i, line in enumerate(txt.splitlines(), 1):
        for m in pat.finditer(line):
            add("P8", page, i, f"baseline: {m.group(0)}")


def check_P9(page, txt):
    r = rel(page)
    has = "data-ink-seam" in txt
    if r in INK_SEAM and not has:
        add("P9", page, 0, "missing data-ink-seam (required on this page)")
    elif r not in INK_SEAM and has:
        add("P9", page, line_of(txt, "data-ink-seam"), "unexpected data-ink-seam")


def check_P10(page, txt):
    for i, line in enumerate(txt.splitlines(), 1):
        for m in LINK_RE.finditer(line):
            val = m.group(1).strip()
            if not val or val.startswith(SKIP_PREFIX):
                continue
            raw = val.split("#", 1)[0].split("?", 1)[0]
            if not raw:
                continue
            raw = unquote(raw)
            target = V2_DIR / raw.lstrip("/") if raw.startswith("/") else page.parent / raw
            try:
                target = target.resolve()
            except Exception:
                continue
            if not target.exists():
                add("P10", page, i, f"unresolved link: {val}")


def check_P11(page, txt):
    marks = [m for m in ("data-export-csv", "data-export-pass", "Ta.export") if m in txt]
    if marks:
        INFO["export"].append(f"{rel(page)}: {', '.join(marks)}")


def check_P12():
    if not ASSETS.exists():
        return
    for f in sorted(ASSETS.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        try:
            size = f.stat().st_size
        except OSError:
            continue
        if size > 250 * 1024:
            add("P12", f, 0, f"large asset {size / 1024:.0f} KB (> 250 KB)")


# --------------------------------------------------------------------------
def run_checks():
    for fn in (check_F1, check_F2, check_F3, check_F4, check_F5, check_F6, check_F7, check_F8):
        fn()
    html_pages = pages()
    for page in html_pages:
        txt = read_text(page)
        check_P1(page, txt)
        check_P2(page, txt)
        check_P3(page, txt)
        check_P4(page, txt)
        check_P5(page, txt)
        check_P6(page, txt)
        check_P7(page, txt)
        check_P8(page, txt)
        check_P9(page, txt)
        check_P10(page, txt)
        check_P11(page, txt)
    check_P12()
    return html_pages


def report(html_pages):
    print(f"=== AttendTa v2 UI Check ({'strict' if STRICT else 'baseline'}) ===")
    print(f"Pages scanned: {len(html_pages)}")

    rules = sorted({i["rule"] for i in ISSUES})
    for rule in rules:
        group = [i for i in ISSUES if i["rule"] == rule]
        tag = "FATAL" if any(g["fatal"] for g in group) else "BASELINE"
        print(f"\n--- {rule} ({len(group)}) ---")
        for g in sorted(group, key=lambda x: (x["path"], x["line"], x["message"])):
            loc = f"{g['path']}:{g['line']}" if g["line"] else g["path"]
            print(f"  [{tag}] {loc}  {g['message']}")

    if INFO["contrast"]:
        print("\n--- INFO contrast (non-fatal) ---")
        for line in INFO["contrast"]:
            print(f"  {line}")
    if INFO["export"]:
        print("\n--- INFO export hooks (informational) ---")
        for line in INFO["export"]:
            print(f"  {line}")

    print("\n=== SUMMARY ===")
    counts = {}
    for i in ISSUES:
        counts[i["rule"]] = counts.get(i["rule"], 0) + 1
    if not counts:
        print("  (no issues)")
    for rule in sorted(counts):
        print(f"  {rule}: {counts[rule]}")
    foundation_fail = any(i["rule"].startswith("F") for i in ISSUES)
    baseline_total = sum(1 for i in ISSUES if i["rule"].startswith("P"))
    print(f"FOUNDATION: {'FAIL' if foundation_fail else 'PASS'}")
    print(f"TOTAL baseline: {baseline_total}")
    return 1 if any(i["fatal"] for i in ISSUES) else 0


def main():
    global STRICT
    parser = argparse.ArgumentParser(description="AttendTa v2 UI consistency checker")
    parser.add_argument("--strict", action="store_true",
                        help="treat page-level issues as fatal")
    args = parser.parse_args()
    STRICT = args.strict
    html_pages = run_checks()
    sys.exit(report(html_pages))


if __name__ == "__main__":
    main()
