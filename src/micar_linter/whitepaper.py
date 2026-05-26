"""Input model for crypto-asset white papers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class WhitepaperType(StrEnum):
    """The three MiCAR white paper regimes.

    OTHER:  Art. 6 i.V.m. Anhang I MiCAR (crypto-assets other than ARTs and EMTs).
    ART:    Art. 19 i.V.m. Anhang II MiCAR (asset-referenced tokens).
    EMT:    Art. 51 i.V.m. Anhang III MiCAR (e-money tokens).
    """

    OTHER = "other"
    ART = "art"
    EMT = "emt"


@dataclass(frozen=True)
class Whitepaper:
    """A parsed white paper draft."""

    title: str
    type: WhitepaperType
    sections: dict[str, str]
    metadata: dict[str, Any]

    def section(self, key: str) -> str:
        value = self.sections.get(key, "")
        return value if isinstance(value, str) else str(value)


def load_whitepaper(path: Path) -> Whitepaper:
    """Load and validate a white paper JSON, PDF, or DOCX file."""
    suffix = path.suffix.lower()
    
    if suffix == ".json":
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except FileNotFoundError as exc:
            raise SystemExit(f"File not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc

        if not isinstance(data, dict):
            raise SystemExit("Whitepaper JSON must be an object.")
        if not isinstance(data.get("sections"), dict):
            raise SystemExit("Whitepaper JSON must contain a 'sections' object.")

        type_str = str(data.get("type", "other")).lower()
        try:
            wp_type = WhitepaperType(type_str)
        except ValueError as exc:
            raise SystemExit(
                f"Unknown whitepaper type '{type_str}'. Expected one of: "
                + ", ".join(t.value for t in WhitepaperType)
            ) from exc

        sections = {str(k): (v if isinstance(v, str) else str(v)) for k, v in data["sections"].items()}
        metadata = {k: v for k, v in data.items() if k not in ("title", "type", "sections")}

        return Whitepaper(
            title=str(data.get("title", "Untitled white paper")),
            type=wp_type,
            sections=sections,
            metadata=metadata,
        )
        
    elif suffix in (".pdf", ".docx"):
        if not path.exists():
            raise SystemExit(f"File not found: {path}")
            
        try:
            if suffix == ".pdf":
                from micar_linter.document import load_from_pdf
                sections = load_from_pdf(path)
            else:
                from micar_linter.document import load_from_docx
                sections = load_from_docx(path)
        except Exception as exc:
            raise SystemExit(f"Error reading document {path}: {exc}") from exc

        # Infer whitepaper type based on keywords in full text
        full_text = "\n".join(sections.values()).lower()
        if "asset-referenced" in full_text or "stabilisation mechanism" in full_text or "reserve of assets" in full_text:
            wp_type = WhitepaperType.ART
        elif "e-money token" in full_text or "referenced currency" in full_text or "safeguarding of funds" in full_text:
            wp_type = WhitepaperType.EMT
        else:
            wp_type = WhitepaperType.OTHER

        title = path.stem.replace("-", " ").replace("_", " ").title()
        metadata = {"source_file": str(path)}

        return Whitepaper(
            title=title,
            type=wp_type,
            sections=sections,
            metadata=metadata,
        )
        
    else:
        raise SystemExit(f"Unsupported file format '{suffix}'. Expected: .json, .pdf, .docx")
