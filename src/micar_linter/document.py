"""PDF and DOCX document ingestion and section parsing."""

from __future__ import annotations

import re
from pathlib import Path

# Common patterns (in English and German) matching whitepaper section headings.
# Word boundaries are used to avoid false positives.
SECTION_PATTERNS = {
    "summary": [r"\bsummary\b", r"\bzusammenfassung\b", r"\bplain-language\s+summary\b", r"\bkey\s+information\b"],
    "risk_warning": [r"\brisk\s+warning\b", r"\bwarnhinweis\b", r"\bmandatory\s+warning\b"],
    "management_statement": [r"\bmanagement\s+body\b", r"\bleitungsorgan\b", r"\bmanagement\s+statement\b", r"\bstatement\b.*\bmanagement\b"],
    "notification_date": [r"\bdate\s+of\s+notification\b", r"\bnotifizierungsdatum\b", r"\bnotification\s+date\b"],
    "language": [r"\blanguage\b", r"\bsprache\b"],
    "offeror": [r"\bofferor\b", r"\banbieter\b"],
    "issuer": [r"\bissuer\b", r"\bemittent\b"],
    "trading_platform_operator": [r"\btrading\s+platform\b", r"\bhandelsplattform\b", r"\boperator\b.*\btrading\b"],
    "project": [r"\bproject\b", r"\bprojekt\b", r"\bbusiness\s+model\b", r"\bteam\b"],
    "offer_or_admission": [r"\bpublic\s+offer\b", r"\bzulassung\b", r"\badmission\s+to\s+trading\b", r"\boffer\b.*\badmission\b"],
    "crypto_asset": [r"\bcrypto-asset\b", r"\bcrypto\s+asset\b", r"\bcharacteristics\b.*\bcrypto\b"],
    "art": [r"\basset-referenced\s+token\b", r"\bstabilisation\s+mechanism\b", r"\breference\s+assets\b"],
    "emt": [r"\be-money\s+token\b", r"\bdenomination\b", r"\breferenced\s+currency\b"],
    "rights_and_obligations": [r"\brights\s+and\s+obligations\b", r"\brechte\s+und\s+pflichten\b", r"\bholder\s+rights\b"],
    "technology": [r"\btechnology\b", r"\btechnologie\b", r"\bunderlying\s+technology\b", r"\bdlt\b", r"\bconsensus\b"],
    "risks": [r"\brisk\s+factors\b", r"\brisikofaktoren\b", r"\brisks\b", r"\brisiken\b"],
    "environmental_impact": [r"\benvironmental\b", r"\bclimate\b", r"\bsustainability\b", r"\bumwelt\b", r"\bklima\b"],
    "reserve_of_assets": [r"\breserve\b.*\bassets\b", r"\breservevermögen\b", r"\basset\s+reserve\b"],
    "redemption": [r"\bredemption\b", r"\brücknahme\b", r"\bredemption\s+right\b"],
    "safeguarding": [r"\bsafeguarding\b", r"\babsicherung\b", r"\bsicherung\b.*\bgelder\b"],
}


def match_heading_to_section(heading: str) -> str | None:
    """Matches a heading line to a known ruleset section key."""
    normalized = heading.lower()
    for key, patterns in SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized):
                return key
    return None


def load_from_docx(path: Path) -> dict[str, str]:
    """Parse a DOCX file and group text paragraphs under identified section headings."""
    import docx

    doc = docx.Document(path)
    sections: dict[str, list[str]] = {}
    current_key = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Heuristics for DOCX headings
        is_heading = False
        if para.style.name.startswith("Heading"):
            is_heading = True
        elif any(run.bold for run in para.runs) and len(text) < 120:
            is_heading = True
        elif text.isupper() and len(text) < 120:
            is_heading = True

        if is_heading:
            matched_key = match_heading_to_section(text)
            if matched_key:
                current_key = matched_key

        if current_key:
            sections.setdefault(current_key, []).append(text)

    return {k: "\n".join(v) for k, v in sections.items()}


def load_from_pdf(path: Path) -> dict[str, str]:
    """Parse a PDF file and extract text grouped under identified section headings."""
    import pypdf

    reader = pypdf.PdfReader(path)
    full_text_lines = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text_lines.extend(text.splitlines())

    sections: dict[str, list[str]] = {}
    current_key = None

    for line in full_text_lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Heuristics for PDF line headings
        is_heading = False
        if len(line_clean) < 120:
            matched_key = match_heading_to_section(line_clean)
            if matched_key:
                is_heading = True

        if is_heading:
            matched_key = match_heading_to_section(line_clean)
            if matched_key:
                current_key = matched_key

        if current_key:
            sections.setdefault(current_key, []).append(line_clean)

    return {k: "\n".join(v) for k, v in sections.items()}
