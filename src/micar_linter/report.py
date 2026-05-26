"""Report rendering — plain text and JSON."""

from __future__ import annotations

import json

from micar_linter.linter import Report

_STATUS_ICON = {"pass": "PASS  ", "review": "REVIEW", "missing": "MISS  "}
_TITLE_BAR = "=" * 78


def render_text(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"MiCAR Whitepaper Linter — {report.title}")
    lines.append(f"Whitepaper type: {report.whitepaper_type.value.upper()}")
    lines.append(_TITLE_BAR)
    lines.append(
        "Pass: {p}  |  Review: {r}  |  Missing: {m}  |  Blockers: {b}".format(
            p=len(report.passed),
            r=len(report.needs_review),
            m=len(report.missing),
            b=len(report.blockers),
        )
    )
    lines.append("")

    for finding in report.findings:
        rule = finding.rule
        icon = _STATUS_ICON[finding.status]
        sev = rule.severity.label
        lines.append(f"[{icon}] [{sev:7}] {rule.rule_id}  {rule.label}")
        lines.append(f"           Cite:  {rule.citation}")
        lines.append(f"           Section: '{rule.section}'  ({finding.word_count} words)")
        for issue in finding.issues:
            lines.append(f"           -  {issue}")
        lines.append("")

    if report.warnings:
        lines.append("Warnings:")
        for warning in report.warnings:
            lines.append(f"  -  {warning}")
        lines.append("")

    lines.append(_TITLE_BAR)
    if report.is_clean:
        lines.append("All required disclosures present. Lawyer review still required.")
    else:
        lines.append(
            "First-pass screening only. The MiCAR notification under "
            "Art. 8 / 17 / 49 MiCAR cannot proceed until BLOCKER items are cured."
        )
    lines.append("This tool is not legal advice.")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    payload = {
        "title": report.title,
        "whitepaper_type": report.whitepaper_type.value,
        "summary": {
            "pass": len(report.passed),
            "review": len(report.needs_review),
            "missing": len(report.missing),
            "blockers": len(report.blockers),
            "total": len(report.findings),
        },
        "warnings": list(report.warnings),
        "findings": [
            {
                "rule_id": f.rule.rule_id,
                "citation": f.rule.citation,
                "section": f.rule.section,
                "label": f.rule.label,
                "severity": f.rule.severity.label,
                "status": f.status,
                "word_count": f.word_count,
                "issues": list(f.issues),
            }
            for f in report.findings
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
