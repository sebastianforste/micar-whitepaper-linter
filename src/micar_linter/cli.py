"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from micar_linter import __version__
from micar_linter.linter import lint_whitepaper
from micar_linter.report import render_html, render_json, render_text
from micar_linter.whitepaper import load_whitepaper


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="micar-lint",
        description=(
            "Deterministic first-pass linter for MiCAR crypto-asset white paper drafts. "
            "Reads a JSON draft, applies the rule set keyed to the whitepaper type "
            "(other / ART / EMT), and prints a structured review report with pinpoint "
            "citations to MiCAR articles and annexes. Not legal advice."
        ),
    )
    parser.add_argument("path", type=Path, help="Path to a whitepaper JSON file.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of text.",
    )
    parser.add_argument(
        "--html",
        type=Path,
        metavar="PATH",
        help="Export a beautiful, interactive HTML compliance report to the specified path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any BLOCKER-severity finding is open.",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        default=None,
        help="Force colorized text output.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Force plain text output with no ANSI colors.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"micar-lint {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    whitepaper = load_whitepaper(args.path)
    report = lint_whitepaper(whitepaper)

    # Determine whether to use color
    if args.no_color:
        use_color = False
    elif args.color:
        use_color = True
    else:
        use_color = sys.stdout.isatty()

    if args.json:
        print(render_json(report))
    else:
        print(render_text(report, color=use_color))

    if args.html:
        try:
            html_content = render_html(report)
            args.html.write_text(html_content, encoding="utf-8")
            print(f"\nHTML report saved to {args.html}", file=sys.stderr)
        except Exception as exc:
            print(f"\nError saving HTML report: {exc}", file=sys.stderr)
            return 2

    if args.strict and report.blockers:
        return 1
    return 0
