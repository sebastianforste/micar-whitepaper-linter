"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from micar_linter import __version__
from micar_linter.linter import lint_whitepaper
from micar_linter.report import render_json, render_text
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
        "--strict",
        action="store_true",
        help="Exit with status 1 if any BLOCKER-severity finding is open.",
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

    if args.json:
        print(render_json(report))
    else:
        print(render_text(report))

    if args.strict and report.blockers:
        return 1
    return 0
