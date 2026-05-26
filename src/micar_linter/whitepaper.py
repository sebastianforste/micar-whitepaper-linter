"""Input model for crypto-asset white papers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class WhitepaperType(str, Enum):
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
    """Load and validate a white paper JSON file."""
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
