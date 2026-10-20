"""Command-line interface for lineguard."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .scanner import scan_path, fix_file, DEFAULT_EXTS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="lineguard",
        description="Enforce maximum line length and forbid trailing whitespace.",
    )
    parser.add_argument("path", nargs="?", default=".",
                        help="file or directory to scan (default: .)")
    parser.add_argument("--max-len", type=int, default=88,
                        help="maximum allowed line length (default: 88)")
    parser.add_argument("--no-trailing", action="store_true",
                        help="do not check trailing whitespace")
    parser.add_argument("--ext", default="",
                        help="comma-separated extensions (e.g. .py,.js)")
    parser.add_argument("--json", action="store_true",
                        help="emit findings as JSON")
    parser.add_argument("--fix", action="store_true",
                        help="remove trailing whitespace in place")
    parser.add_argument("--version", action="version",
                        version="lineguard " + __version__)
    args = parser.parse_args(argv)

    exts = None
    if args.ext:
        exts = {e.strip() if e.strip().startswith(".") else "." + e.strip()
                for e in args.ext.split(",") if e.strip()}

    check_trailing = not args.no_trailing

    if args.fix:
        from pathlib import Path as _P
        root = _P(args.path)
        files = []
        if root.is_file():
            files = [root]
        else:
            for dp, dns, fns in __import__("os").walk(root):
                dns[:] = [d for d in dns if d not in {".git", "node_modules", "__pycache__"}]
                for fn in fns:
                    p = _P(dp) / fn
                    if exts and p.suffix.lower() not in exts:
                        continue
                    files.append(p)
        changed = 0
        for f in files:
            if fix_file(f):
                changed += 1
        print(f"Fixed trailing whitespace in {changed} file(s).")
        # still report remaining issues
    findings = scan_path(args.path, max_len=args.max_len,
                         check_trailing=check_trailing, exts=exts)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        if not findings:
            print("No line issues found.")
        else:
            for fnd in findings:
                if fnd["kind"] == "line-too-long":
                    print(f'{fnd["file"]}:{fnd["line"]}: line too long '
                          f'({fnd["length"]} > {fnd["limit"]})')
                else:
                    print(f'{fnd["file"]}:{fnd["line"]}: trailing whitespace')
            print(f"\nTotal: {len(findings)}")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())