"""Annex I MiCAR — crypto-assets other than ARTs and EMTs.

Reference: Anhang I VO (EU) 2023/1114 i.V.m. Art. 6 MiCAR.

Annex I is structured as Parts A through J. Each Part bundles point-level
disclosure requirements. The rules below are scaffolded at the Part level;
point-level granularity (e.g. Annex I, Part D, point 5) is left as a
deliberate extension point — those interpretive calls are the practising
lawyer's contribution and are tracked in the project issues.
"""

from __future__ import annotations

from micar_linter.rules.base import Rule, Severity

ANNEX_I_RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="ANNEX_I.A",
        citation="Anhang I Teil A MiCAR",
        section="offeror",
        label="Information about the offeror or person seeking admission to trading",
        required_terms=("name", "legal form", "registered", "address"),
        min_words=50,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.B",
        citation="Anhang I Teil B MiCAR",
        section="issuer",
        label="Information about the issuer, if different from the offeror or person seeking admission",
        required_terms=("issuer", "registered", "address"),
        min_words=40,
    ),
    Rule(
        rule_id="ANNEX_I.C",
        citation="Anhang I Teil C MiCAR",
        section="trading_platform_operator",
        label="Information about the operator of the trading platform, where applicable",
        required_terms=("trading platform", "operator"),
        min_words=20,
        severity=Severity.MINOR,
    ),
    Rule(
        rule_id="ANNEX_I.D",
        citation="Anhang I Teil D MiCAR",
        section="project",
        label="Information about the crypto-asset project",
        required_terms=("project", "purpose", "business model", "team"),
        min_words=80,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.E",
        citation="Anhang I Teil E MiCAR",
        section="offer_or_admission",
        label="Information about the offer to the public or admission to trading",
        required_terms=("offer", "price", "subscription", "target", "jurisdictions"),
        min_words=60,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.F",
        citation="Anhang I Teil F MiCAR",
        section="crypto_asset",
        label="Information about the crypto-asset (type, characteristics, functionality)",
        required_terms=("crypto-asset", "supply", "transfer", "functionality"),
        min_words=60,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.G",
        citation="Anhang I Teil G MiCAR",
        section="rights_and_obligations",
        label="Rights and obligations attached to the crypto-asset",
        required_terms=("rights", "obligations", "holder", "enforce"),
        min_words=60,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.H",
        citation="Anhang I Teil H MiCAR",
        section="technology",
        label="Information on the underlying technology",
        required_terms=("protocol", "consensus", "smart contract", "audit"),
        min_words=60,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.I",
        citation="Anhang I Teil I MiCAR",
        section="risks",
        label="Risk factors (market, project, technology, mitigation measures)",
        required_terms=("market", "technology", "regulatory", "liquidity", "operational"),
        min_words=120,
        severity=Severity.BLOCKER,
    ),
    Rule(
        rule_id="ANNEX_I.J",
        citation="Anhang I Teil J MiCAR i.V.m. ESMA RTS on sustainability indicators",
        section="environmental_impact",
        label="Principal adverse environmental and climate-related impact of the consensus mechanism",
        required_terms=("consensus", "energy", "climate", "environmental"),
        min_words=80,
        severity=Severity.MAJOR,
    ),
)
