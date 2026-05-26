"""Report rendering — plain text, JSON, and beautiful HTML."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from micar_linter.linter import Report
from micar_linter.rules.base import Severity

_STATUS_ICON = {"pass": "PASS  ", "review": "REVIEW", "missing": "MISS  "}
_TITLE_BAR = "=" * 78


def render_text(report: Report, color: bool = False) -> str:
    if color:
        status_icons = {
            "pass": "\033[92mPASS\033[0m  ",
            "review": "\033[93mREVIEW\033[0m",
            "missing": "\033[91mMISS\033[0m  ",
        }
        severity_labels = {
            "BLOCKER": "\033[91mBLOCKER\033[0m",
            "MAJOR": "\033[93mMAJOR\033[0m",
            "MINOR": "\033[94mMINOR\033[0m",
        }
        title_style = lambda s: f"\033[1m{s}\033[0m"
        warning_style = lambda s: f"\033[93m[WARNING] {s}\033[0m"
        issue_style = lambda s: f"\033[91m- {s}\033[0m" if "missing" in s.lower() or "thin" in s.lower() else f"\033[33m- {s}\033[0m"
        passed_style = lambda s: f"\033[92m{s}\033[0m"
        failed_style = lambda s: f"\033[91m{s}\033[0m"
    else:
        status_icons = {"pass": "PASS  ", "review": "REVIEW", "missing": "MISS  "}
        severity_labels = {"BLOCKER": "BLOCKER", "MAJOR": "MAJOR", "MINOR": "MINOR"}
        title_style = lambda s: s
        warning_style = lambda s: f"[WARNING] {s}"
        issue_style = lambda s: f"           -  {s}"
        passed_style = lambda s: s
        failed_style = lambda s: s

    lines: list[str] = []
    lines.append(title_style(f"MiCAR Whitepaper Linter — {report.title}"))
    lines.append(f"Whitepaper type: {report.whitepaper_type.value.upper()}")
    
    if report.warnings:
        lines.append("")
        for warning in report.warnings:
            lines.append(warning_style(warning))

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
        icon = status_icons[finding.status]
        sev = severity_labels[rule.severity.label]
        lines.append(f"[{icon}] [{sev:7}] {rule.rule_id}  {rule.label}")
        lines.append(f"           Cite:  {rule.citation}")
        lines.append(f"           Section: '{rule.section}'  ({finding.word_count} words)")
        for issue in finding.issues:
            if color:
                lines.append(f"           {issue_style(issue)}")
            else:
                lines.append(issue_style(issue))
        lines.append("")

    lines.append(_TITLE_BAR)
    if report.is_clean:
        lines.append(passed_style("All required disclosures present. Lawyer review still required."))
    else:
        lines.append(
            failed_style(
                "First-pass screening only. The MiCAR notification under "
                "Art. 8 / 17 / 49 MiCAR cannot proceed until BLOCKER items are cured."
            )
        )
    lines.append("This tool is not legal advice.")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    payload = _build_payload(report)
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _build_payload(report: Report) -> dict[str, Any]:
    return {
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


def render_html(report: Report) -> str:
    payload = _build_payload(report)
    json_data = json.dumps(payload, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MiCAR Compliance Report — {report.title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-color: #0b0f19;
      --card-bg: rgba(22, 29, 49, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --text-primary: #f3f4f6;
      --text-secondary: #9ca3af;
      --color-pass: #10b981;
      --color-review: #f59e0b;
      --color-missing: #ef4444;
      --color-blocker: #ef4444;
      --color-major: #f97316;
      --color-minor: #3b82f6;
      --font-sans: 'Outfit', sans-serif;
    }}

    body {{
      background-color: var(--bg-color);
      color: var(--text-primary);
      font-family: var(--font-sans);
      margin: 0;
      padding: 2rem 1.5rem;
      line-height: 1.5;
      background-image: radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent 60%);
      background-attachment: fixed;
    }}

    .container {{
      max-width: 1000px;
      margin: 0 auto;
    }}

    header {{
      margin-bottom: 2rem;
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
      padding: 2rem;
      border-radius: 1rem;
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
      box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    }}

    h1 {{
      margin: 0 0 0.5rem 0;
      font-size: 2.25rem;
      font-weight: 700;
      letter-spacing: -0.025em;
    }}

    .meta-subtitle {{
      color: var(--text-secondary);
      font-size: 0.95rem;
      margin-bottom: 1.5rem;
      display: flex;
      gap: 1rem;
      align-items: center;
    }}

    .badge-wp-type {{
      background: rgba(59, 130, 246, 0.15);
      color: #93c5fd;
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .warnings-box {{
      background: rgba(245, 158, 11, 0.08);
      border: 1px solid rgba(245, 158, 11, 0.3);
      padding: 1rem 1.25rem;
      border-radius: 0.75rem;
      margin-bottom: 1.5rem;
    }}

    .warnings-title {{
      color: var(--color-review);
      font-weight: 600;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .warnings-box ul {{
      margin: 0;
      padding-left: 1.25rem;
      font-size: 0.9rem;
      color: var(--text-primary);
    }}

    .dashboard {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    .metric-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      padding: 1.25rem;
      border-radius: 0.75rem;
      text-align: center;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s;
    }}

    .metric-card:hover {{
      transform: translateY(-2px);
    }}

    .metric-value {{
      font-size: 2.25rem;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 0.25rem;
    }}

    .metric-value.pass {{ color: var(--color-pass); }}
    .metric-value.review {{ color: var(--color-review); }}
    .metric-value.missing {{ color: var(--color-missing); }}
    .metric-value.blockers {{ color: var(--color-blocker); }}

    .metric-label {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 500;
    }}

    .score-container {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 1.5rem;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      padding: 1.25rem;
      border-radius: 0.75rem;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }}

    .score-circle {{
      position: relative;
      width: 80px;
      height: 80px;
    }}

    .score-circle svg {{
      transform: rotate(-90deg);
      width: 80px;
      height: 80px;
    }}

    .score-circle circle {{
      fill: none;
      stroke-width: 8;
    }}

    .score-circle .bg-ring {{
      stroke: rgba(255, 255, 255, 0.06);
    }}

    .score-circle .score-ring {{
      stroke: var(--color-pass);
      stroke-linecap: round;
      stroke-dasharray: 226.2;
      stroke-dashoffset: 226.2;
      transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .score-text {{
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 1.3rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .score-info h3 {{
      margin: 0 0 0.25rem 0;
      font-size: 1.1rem;
      font-weight: 600;
    }}

    .score-info p {{
      margin: 0;
      font-size: 0.85rem;
      color: var(--text-secondary);
    }}

    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 1.5rem;
      background: rgba(15, 23, 42, 0.4);
      padding: 1rem;
      border-radius: 0.75rem;
      border: 1px solid var(--card-border);
      align-items: center;
    }}

    .search-wrapper {{
      position: relative;
      flex-grow: 1;
      min-width: 250px;
    }}

    .search-input {{
      width: 100%;
      box-sizing: border-box;
      background: rgba(10, 15, 30, 0.6);
      border: 1px solid var(--card-border);
      padding: 0.6rem 1rem;
      border-radius: 0.5rem;
      color: var(--text-primary);
      font-family: var(--font-sans);
      font-size: 0.9rem;
      transition: border-color 0.2s;
    }}

    .search-input:focus {{
      outline: none;
      border-color: #3b82f6;
    }}

    .filter-group {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .btn-filter {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--card-border);
      color: var(--text-secondary);
      padding: 0.5rem 0.875rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-family: var(--font-sans);
      font-size: 0.85rem;
      font-weight: 500;
      transition: all 0.2s;
      user-select: none;
    }}

    .btn-filter:hover {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
    }}

    .btn-filter.active {{
      background: rgba(59, 130, 246, 0.2);
      border-color: #3b82f6;
      color: #60a5fa;
    }}

    .findings-list {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 3rem;
    }}

    .finding-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 0.75rem;
      overflow: hidden;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
      transition: border-color 0.2s, box-shadow 0.2s;
    }}

    .finding-card:hover {{
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }}

    .finding-card.status-pass {{ border-left: 4px solid var(--color-pass); }}
    .finding-card.status-review {{ border-left: 4px solid var(--color-review); }}
    .finding-card.status-missing {{ border-left: 4px solid var(--color-missing); }}

    .finding-header {{
      padding: 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }}

    .finding-title-group {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .rule-id {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-secondary);
      background: rgba(255, 255, 255, 0.05);
      padding: 0.15rem 0.4rem;
      border-radius: 0.25rem;
    }}

    .finding-label {{
      font-weight: 600;
      font-size: 1rem;
    }}

    .finding-badges {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .status-badge {{
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }}

    .status-badge.pass {{ background: rgba(16, 185, 129, 0.12); color: var(--color-pass); }}
    .status-badge.review {{ background: rgba(245, 158, 11, 0.12); color: var(--color-review); }}
    .status-badge.missing {{ background: rgba(239, 68, 68, 0.12); color: var(--color-missing); }}

    .sev-badge {{
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.02em;
    }}

    .sev-badge.blocker {{ background: rgba(239, 68, 68, 0.12); color: var(--color-blocker); }}
    .sev-badge.major {{ background: rgba(249, 115, 22, 0.12); color: var(--color-major); }}
    .sev-badge.minor {{ background: rgba(59, 130, 246, 0.12); color: var(--color-minor); }}

    .toggle-icon {{
      width: 20px;
      height: 20px;
      fill: currentColor;
      color: var(--text-secondary);
      transition: transform 0.2s;
    }}

    .finding-card.open .toggle-icon {{
      transform: rotate(180deg);
    }}

    .finding-details {{
      display: none;
      background: rgba(10, 15, 30, 0.4);
      border-top: 1px solid var(--card-border);
    }}

    .finding-card.open .finding-details {{
      display: block;
    }}

    .details-content {{
      padding: 1.25rem;
    }}

    .detail-row {{
      margin-bottom: 0.75rem;
      display: flex;
      border-bottom: 1px solid rgba(255, 255, 255, 0.03);
      padding-bottom: 0.75rem;
    }}

    .detail-row:last-child {{
      border-bottom: none;
      padding-bottom: 0;
      margin-bottom: 0;
    }}

    .detail-label {{
      min-width: 140px;
      color: var(--text-secondary);
      font-size: 0.85rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .detail-value {{
      font-size: 0.9rem;
      color: var(--text-primary);
    }}

    .issues-list {{
      margin: 0;
      padding-left: 1.25rem;
      color: #fda4af;
    }}
    
    .issues-list li {{
      margin-bottom: 0.25rem;
    }}

    .legal-notice-footer {{
      margin-top: 4rem;
      border-top: 1px solid var(--card-border);
      padding-top: 1.5rem;
      color: var(--text-secondary);
      font-size: 0.8rem;
      text-align: center;
      line-height: 1.6;
    }}

    .legal-notice-warning {{
      background: rgba(239, 68, 68, 0.05);
      border: 1px solid rgba(239, 68, 68, 0.2);
      padding: 1rem;
      border-radius: 0.5rem;
      color: #fca5a5;
      text-align: left;
      margin-bottom: 1rem;
    }}

    @media (max-width: 600px) {{
      .finding-header {{
        flex-direction: column;
        align-items: flex-start;
        gap: 0.75rem;
      }}
      .finding-badges {{
        width: 100%;
        justify-content: space-between;
      }}
      .detail-row {{
        flex-direction: column;
        gap: 0.25rem;
      }}
    }}

    @media print {{
      body {{
        background-color: white !important;
        background-image: none !important;
        color: black !important;
        padding: 0;
      }}
      header, .controls, .btn-filter, .search-input, .toggle-icon {{
        display: none !important;
      }}
      .finding-card {{
        page-break-inside: avoid;
        border: 1px solid #ccc !important;
        background: transparent !important;
        color: black !important;
        box-shadow: none !important;
        margin-bottom: 1rem;
      }}
      .finding-card.open .finding-details, .finding-details {{
        display: block !important;
        background: transparent !important;
      }}
      .metric-card, .score-container {{
        border: 1px solid #ccc !important;
        background: transparent !important;
        color: black !important;
        box-shadow: none !important;
      }}
      .status-badge, .sev-badge {{
        border: 1px solid #aaa;
        background: transparent !important;
        color: black !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>{report.title}</h1>
      <div class="meta-subtitle">
        <span>MiCAR Compliance Report</span>
        <span class="badge-wp-type">{report.whitepaper_type.value}</span>
      </div>
      
      <div id="warnings-container"></div>
      
      <div class="dashboard">
        <div class="metric-card">
          <div class="metric-value" id="count-total">0</div>
          <div class="metric-label">Total Rules</div>
        </div>
        <div class="metric-card">
          <div class="metric-value pass" id="count-pass">0</div>
          <div class="metric-label">Passed</div>
        </div>
        <div class="metric-card">
          <div class="metric-value review" id="count-review">0</div>
          <div class="metric-label">Needs Review</div>
        </div>
        <div class="metric-card">
          <div class="metric-value missing" id="count-missing">0</div>
          <div class="metric-label">Missing</div>
        </div>
        <div class="metric-card">
          <div class="metric-value blockers" id="count-blockers">0</div>
          <div class="metric-label">Blockers</div>
        </div>
      </div>

      <div class="score-container">
        <div class="score-circle">
          <svg viewBox="0 0 80 80">
            <circle class="bg-ring" cx="40" cy="40" r="36" />
            <circle class="score-ring" id="progress-ring" cx="40" cy="40" r="36" />
          </svg>
          <div class="score-text" id="score-percentage">0%</div>
        </div>
        <div class="score-info">
          <h3>Completeness Score</h3>
          <p id="score-summary-text">Compliance analysis loading...</p>
        </div>
      </div>
    </header>

    <div class="controls">
      <div class="search-wrapper">
        <input type="text" class="search-input" id="search-input" placeholder="Search rules, sections or citations...">
      </div>
      <div class="filter-group">
        <button class="btn-filter active" data-filter="all">All</button>
        <button class="btn-filter" data-filter="blocker">Blockers</button>
        <button class="btn-filter" data-filter="review">Review Needed</button>
        <button class="btn-filter" data-filter="missing">Missing</button>
        <button class="btn-filter" data-filter="pass">Passed</button>
      </div>
    </div>

    <div class="findings-list" id="findings-list"></div>

    <div class="legal-notice-footer">
      <div class="legal-notice-warning">
        <strong>IMPORTANT REGULATORY NOTICE:</strong> This first-pass compliance report is a deterministic screening check for draft whitepapers against Markets in Crypto-Assets Regulation (MiCAR) disclosure frameworks under Regulation (EU) 2023/1114. The MiCAR notification procedure (Art. 8 / 17 / 49) cannot proceed until any BLOCKER findings are resolved. This report does not constitute legal counsel or formal regulatory review.
      </div>
      Generated by MiCAR Whitepaper Linter. Not legal advice. &copy; 2026.
    </div>
  </div>

  <script id="report-data" type="application/json">
    {json_data}
  </script>

  <script>
    const data = JSON.parse(document.getElementById('report-data').textContent);
    
    // Setup Header Metrics
    document.getElementById('count-total').textContent = data.summary.total;
    document.getElementById('count-pass').textContent = data.summary.pass;
    document.getElementById('count-review').textContent = data.summary.review;
    document.getElementById('count-missing').textContent = data.summary.missing;
    document.getElementById('count-blockers').textContent = data.summary.blockers;
    
    // Set score circle
    const score = Math.round((data.summary.pass / data.summary.total) * 100) || 0;
    document.getElementById('score-percentage').textContent = score + '%';
    
    const ring = document.getElementById('progress-ring');
    const radius = ring.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    ring.style.strokeDasharray = circumference;
    const offset = circumference - (score / 100) * circumference;
    // Animate ring offset
    setTimeout(() => {{
      ring.style.strokeDashoffset = offset;
    }}, 100);

    // Score message description
    let summaryText = "";
    if (data.summary.blockers > 0) {{
      summaryText = "Action required: " + data.summary.blockers + " Blocker severity findings are preventing MiCAR filing.";
      ring.style.stroke = "var(--color-missing)";
    }} else if (data.summary.review > 0 || data.summary.missing > 0) {{
      summaryText = "Cure warnings: All legal minimum fields present, but minor gaps need manual correction.";
      ring.style.stroke = "var(--color-review)";
    }} else {{
      summaryText = "Draft matches required baseline templates. Ready for legal practitioner validation.";
      ring.style.stroke = "var(--color-pass)";
    }}
    document.getElementById('score-summary-text').textContent = summaryText;

    // Render Warnings Box if warnings exist
    if (data.warnings && data.warnings.length > 0) {{
      const warningsBox = document.createElement('div');
      warningsBox.className = 'warnings-box';
      
      const title = document.createElement('div');
      title.className = 'warnings-title';
      title.innerHTML = '&#9888; Section Formatting Warnings';
      warningsBox.appendChild(title);
      
      const ul = document.createElement('ul');
      data.warnings.forEach(warn => {{
        const li = document.createElement('li');
        li.textContent = warn;
        ul.appendChild(li);
      }});
      warningsBox.appendChild(ul);
      
      document.getElementById('warnings-container').appendChild(warningsBox);
    }}

    // State for filtering
    let currentFilter = 'all';
    let searchQuery = '';

    // Render findings
    const listContainer = document.getElementById('findings-list');

    function renderFindings() {{
      listContainer.innerHTML = '';
      
      const filtered = data.findings.filter(f => {{
        // Match Search Query
        const matchesSearch = 
          f.rule_id.toLowerCase().includes(searchQuery) ||
          f.label.toLowerCase().includes(searchQuery) ||
          f.section.toLowerCase().includes(searchQuery) ||
          f.citation.toLowerCase().includes(searchQuery);
          
        if (!matchesSearch) return false;

        // Match filter buttons
        if (currentFilter === 'all') return true;
        if (currentFilter === 'blocker') return f.severity.toUpperCase() === 'BLOCKER' && f.status !== 'pass';
        if (currentFilter === 'review') return f.status === 'review';
        if (currentFilter === 'missing') return f.status === 'missing';
        if (currentFilter === 'pass') return f.status === 'pass';
        return true;
      }});

      if (filtered.length === 0) {{
        listContainer.innerHTML = `<div style="text-align: center; padding: 3rem; color: var(--text-secondary)">No matching compliance checks found.</div>`;
        return;
      }}

      filtered.forEach(f => {{
        const card = document.createElement('div');
        card.className = `finding-card status-${{f.status}}`;
        
        // Header
        const header = document.createElement('div');
        header.className = 'finding-header';
        
        const titleGroup = document.createElement('div');
        titleGroup.className = 'finding-title-group';
        titleGroup.innerHTML = `<span class="rule-id">${{f.rule_id}}</span> <span class="finding-label">${{f.label}}</span>`;
        header.appendChild(titleGroup);
        
        const badgeGroup = document.createElement('div');
        badgeGroup.className = 'finding-badges';
        badgeGroup.innerHTML = `
          <span class="status-badge ${{f.status}}">${{f.status}}</span>
          <span class="sev-badge ${{f.severity.toLowerCase()}}">${{f.severity}}</span>
          <svg class="toggle-icon" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
        `;
        header.appendChild(badgeGroup);
        card.appendChild(header);

        // Details Panel
        const details = document.createElement('div');
        details.className = 'finding-details';
        
        let issuesContent = '';
        if (f.issues && f.issues.length > 0) {{
          issuesContent = `
            <div class="detail-row">
              <div class="detail-label">Compliance Gaps</div>
              <div class="detail-value">
                <ul class="issues-list">
                  ${{f.issues.map(iss => `<li>${{iss}}</li>`).join('')}}
                </ul>
              </div>
            </div>
          `;
        }}

        details.innerHTML = `
          <div class="details-content">
            <div class="detail-row">
              <div class="detail-label">Citation</div>
              <div class="detail-value" style="font-weight: 500;">${{f.citation}}</div>
            </div>
            <div class="detail-row">
              <div class="detail-label">Section Name</div>
              <div class="detail-value" style="font-family: monospace;">"${{f.section}}"</div>
            </div>
            <div class="detail-row">
              <div class="detail-label">Words Checked</div>
              <div class="detail-value">${{f.word_count}} words</div>
            </div>
            ${{issuesContent}}
          </div>
        `;
        card.appendChild(details);

        // Click handler to toggle open class
        header.addEventListener('click', () => {{
          const isOpen = card.classList.contains('open');
          // Close all cards first (optional, let's allow multiple open but toggle this one)
          card.classList.toggle('open');
        }});

        listContainer.appendChild(card);
      }});
    }}

    // Search events
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value.toLowerCase().trim();
      renderFindings();
    }});

    // Filter events
    const filterButtons = document.querySelectorAll('.btn-filter');
    filterButtons.forEach(btn => {{
      btn.addEventListener('click', (e) => {{
        filterButtons.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        currentFilter = e.target.getAttribute('data-filter');
        renderFindings();
      }});
    }});

    // Initial render
    renderFindings();
  </script>
</body>
</html>
"""
    return html
