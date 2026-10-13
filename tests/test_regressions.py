import pytest
from h2fpef_score import calculate_h2fpef_score, calculate_h2fpef_from_bools
from agents.base import AuditTrail


def test_missing_measurements_not_silently_complete():
    result = calculate_h2fpef_score(age=75)
    assert result["complete"] is False
    assert "bmi" in result["missing_inputs"]
    assert "pasp_mmhg" in result["missing_inputs"]


def test_complete_measurements_and_explicit_boolean_flags():
    result = calculate_h2fpef_score(
        bmi=30, num_antihypertensives=1, af_present=False,
        pasp_mmhg=35, age=60, e_e_prime=9
    )
    assert result["complete"] is True
    assert result["score"] == 0
    assert calculate_h2fpef_from_bools()["complete"] is True


@pytest.mark.parametrize("kwargs", [
    {"num_antihypertensives": 1.5},
    {"num_antihypertensives": True},
    {"af_present": "false"},
    {"heavy": "false"},
])
def test_invalid_clinical_types_rejected(kwargs):
    with pytest.raises(TypeError):
        calculate_h2fpef_score(**kwargs)


def test_tamper_evidence_checks_signatures_and_returns_copies():
    audit = AuditTrail(secret_key="test-only-static-key")
    audit.log("test", "tester", "creation", {"x": 1})
    audit.log("test", "tester", "verification", {"x": 2})
    assert audit.verify_integrity()
    exported = audit.get_trail()
    exported[0]["actor"] = "tampered"
    assert audit.verify_integrity()
    audit.logs[0]["actor"] = "tampered"
    assert not audit.verify_integrity()


def test_hash_edit_without_rekey_is_detected():
    audit = AuditTrail(secret_key="test-only-static-key")
    audit.log("test", "tester", "event", {"x": 1})
    audit.logs[0]["payload_hash"] = "0" * 64
    assert not audit.verify_integrity()


def test_api_scoring_matches_reference():
    from fastapi.testclient import TestClient
    from agents.api import app
    client = TestClient(app)
    payload = dict(bmi=35, num_antihypertensives=2, af_present=True,
                   pasp_mmhg=42, age=75, e_e_prime=12)
    result = client.post("/api/score", json=payload)
    assert result.status_code == 200
    assert result.json()["score"] == 9
    assert result.json()["complete"] is True
    payload["bmi"] = 140
    assert client.post("/api/score", json=payload).status_code == 422
