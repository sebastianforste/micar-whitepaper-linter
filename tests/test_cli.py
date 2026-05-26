from pathlib import Path
import json
import pytest
from micar_linter.cli import main, build_parser


def test_cli_parser_help():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


def test_cli_main_success(tmp_path: Path):
    json_content = """{
        "title": "Clean Token",
        "type": "other",
        "sections": {
            "summary": "This summary provides key information about the token that has key information and is detailed enough.",
            "risk_warning": "This is a mandatory risk warning value loss warning details.",
            "management_statement": "The management body confirms this complies and is fair and clear and not misleading.",
            "notification_date": "Date is today.",
            "language": "Written in English language.",
            "offeror": "Offeror name is Test Ltd, legal form stock corp, registered office Berlin address.",
            "project": "This project purpose is business model and team detail is clear.",
            "offer_or_admission": "This public offer price and subscription target jurisdictions.",
            "crypto_asset": "The crypto-asset supply and transfer details and functionality description.",
            "rights_and_obligations": "The rights and obligations of holder to enforce claims.",
            "technology": "This protocol consensus smart contract security audit.",
            "risks": "The market risk and technology risk and regulatory risk and liquidity risk and operational risk factor.",
            "environmental_impact": "This consensus energy climate environmental impact statement."
        }
    }"""
    file_path = tmp_path / "other.json"
    file_path.write_text(json_content, encoding="utf-8")
    
    # Run in normal mode
    status = main([str(file_path)])
    assert status == 0
    
    # Run in strict mode
    status_strict = main([str(file_path), "--strict"])
    assert status_strict == 0


def test_cli_main_strict_blocker(tmp_path: Path):
    # Missing offeror which is a blocker
    json_content = """{
        "title": "Bad Token",
        "type": "other",
        "sections": {
            "summary": "Short",
            "risk_warning": "Short",
            "management_statement": "Short",
            "notification_date": "Short",
            "language": "Short"
        }
    }"""
    file_path = tmp_path / "bad.json"
    file_path.write_text(json_content, encoding="utf-8")
    
    # Strict mode should exit with status 1 due to blockers
    status = main([str(file_path), "--strict"])
    assert status == 1


def test_cli_main_json_format(tmp_path: Path, capsys):
    json_content = """{
        "title": "Clean Token",
        "type": "other",
        "sections": {
            "summary": "This summary provides key information about the token that has key information and is detailed enough."
        }
    }"""
    file_path = tmp_path / "json_test.json"
    file_path.write_text(json_content, encoding="utf-8")
    
    status = main([str(file_path), "--json"])
    assert status == 0
    
    captured = capsys.readouterr()
    report_data = json.loads(captured.out)
    assert report_data["title"] == "Clean Token"
    assert "findings" in report_data


def test_cli_main_html_export(tmp_path: Path):
    json_content = """{
        "title": "Clean Token",
        "type": "other",
        "sections": {
            "summary": "This summary provides key information about the token."
        }
    }"""
    file_path = tmp_path / "html_test.json"
    file_path.write_text(json_content, encoding="utf-8")
    
    html_path = tmp_path / "report.html"
    status = main([str(file_path), "--html", str(html_path)])
    assert status == 0
    
    assert html_path.exists()
    html_content = html_path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html_content
    assert "Clean Token" in html_content
