import re
from micar_linter.rules import RULESETS
from micar_linter.rules.base import Rule


def test_rulesets_compile_patterns():
    for wp_type, rules in RULESETS.items():
        assert len(rules) > 0
        for rule in rules:
            assert isinstance(rule, Rule)
            assert rule.rule_id
            assert rule.citation
            assert rule.section
            
            # Verify required patterns compile cleanly
            for pattern in rule.required_patterns:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    pytest.fail(f"Invalid required_pattern '{pattern}' in rule {rule.rule_id}: {exc}")
            
            # Verify prohibited patterns compile cleanly
            for pattern in rule.prohibited_patterns:
                try:
                    re.compile(pattern)
                except re.error as exc:
                    pytest.fail(f"Invalid prohibited_pattern '{pattern}' in rule {rule.rule_id}: {exc}")
