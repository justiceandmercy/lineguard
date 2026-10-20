"""Scanning helpers for lineguard."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", "venv", ".venv",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
    ".idea", ".vscode", "target",
}

DEFAULT_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h",
    ".md", ".txt", ".yaml", ".yml", ".toml", ".json", ".sh",
}


def _iter_files(root: Path, exts: Set[str]) -> List[Path]:
    out: List[Path] = []
    if root.is_file():
        return [root] if root.suffix in exts or not exts else []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if exts and p.suffix.lower() not in exts:
                continue
            out.append(p)
    return out


def scan_file(path: Path, max_len: int, check_trailing: bool) -> List[Dict]:
    findings: List[Dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for i, line in enumerate(text.splitlines(), 1):
        # strip trailing newline already; check trailing whitespace
        if check_trailing and line != line.rstrip(" \t"):
            findings.append({
                "file": str(path),
                "line": i,
                "kind": "trailing-whitespace",
                "text": line.rstrip("\n"),
            })
        if len(line) > max_len:
            findings.append({
                "file": str(path),
                "line": i,
                "kind": "line-too-long",
                "length": len(line),
                "limit": max_len,
                "text": line,
            })
    return findings


def scan_path(path, max_len: int = 88, check_trailing: bool = True,
              exts: Optional[Set[str]] = None) -> List[Dict]:
    if exts is None:
        exts = DEFAULT_EXTS
    root = Path(path)
    files = _iter_files(root, exts)
    out: List[Dict] = []
    for f in files:
        out.extend(scan_file(f, max_len, check_trailing))
    return out


def fix_file(path: Path) -> bool:
    """Remove trailing whitespace from every line. Returns True if changed."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    lines = text.splitlines(keepends=True)
    new_lines = []
    changed = False
    for line in lines:
        if line.endswith("\n"):
            body, nl = line[:-1], "\n"
        elif line.endswith("\r\n"):
            body, nl = line[:-2], "\r\n"
        else:
            body, nl = line, ""
        stripped = body.rstrip(" \t")
        if stripped != body:
            changed = True
        new_lines.append(stripped + nl)
    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
    return changed