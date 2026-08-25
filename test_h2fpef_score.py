#!/usr/bin/env python3
"""
Tests for H2FPEF Score Calculator.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from h2fpef_score import (
    calculate_h2fpef_score,
    calculate_h2fpef_from_bools,
    get_hfa_peff_algorithm,
    SCORE_COMPONENTS,
    INTERPRETATION,
)


# =============================================================================
# Score Component Tests
# =============================================================================

def test_all_components_defined():
    """All 6 H2FPEF components must be defined."""
    expected = {"heavy", "hypertensive", "atrial_fibrillation", "pulmonary_pressure", "elder", "filling_pressure"}
    assert set(SCORE_COMPONENTS.keys()) == expected


def test_component_points():
    """Verify point values for each component."""
    assert SCORE_COMPONENTS["heavy"]["points"] == 2
    assert SCORE_COMPONENTS["hypertensive"]["points"] == 1
    assert SCORE_COMPONENTS["atrial_fibrillation"]["points"] == 3
    assert SCORE_COMPONENTS["pulmonary_pressure"]["points"] == 1
    assert SCORE_COMPONENTS["elder"]["points"] == 1
    assert SCORE_COMPONENTS["filling_pressure"]["points"] == 1


def test_max_score():
    """Maximum possible score should be 9."""
    total = sum(c["points"] for c in SCORE_COMPONENTS.values())
    assert total == 9


# =============================================================================
# Basic Score Calculation Tests
# =============================================================================

def test_score_zero():
    """No risk factors -> score 0."""
    result = calculate_h2fpef_score(bmi=22, num_antihypertensives=0, af_present=False, age=40)
    assert result["score"] == 0
    assert result["category"] == "low"


def test_score_max():
    """All risk factors -> score 9."""
    result = calculate_h2fpef_score(
        bmi=35, num_antihypertensives=3, af_present=True,
        pasp_mmhg=50, age=75, e_e_prime=15,
    )
    assert result["score"] == 9
    assert result["category"] == "high"


def test_score_returns_required_keys():
    """Result must contain all required keys."""
    result = calculate_h2fpef_score(bmi=25, age=50)
    assert "score" in result
    assert "max_score" in result
    assert "category" in result
    assert "probability" in result
    assert "probability_percent" in result
    assert "label" in result
    assert "components" in result


# =============================================================================
# Individual Component Tests
# =============================================================================

def test_heavy_bmi_over_30():
    """BMI > 30 -> +2 points."""
    result = calculate_h2fpef_score(bmi=32)
    assert result["score"] == 2
    assert result["components"]["heavy"]["met"] is True


def test_heavy_bmi_under_30():
    """BMI <= 30 -> 0 points."""
    result = calculate_h2fpef_score(bmi=28)
    assert result["score"] == 0
    assert result["components"]["heavy"]["met"] is False


def test_heavy_bmi_exactly_30():
    """BMI exactly 30 -> NOT heavy (>30 required)."""
    result = calculate_h2fpef_score(bmi=30.0)
    assert result["components"]["heavy"]["met"] is False


def test_hypertensive_two_meds():
    """2 antihypertensives -> +1 point."""
    result = calculate_h2fpef_score(num_antihypertensives=2)
    assert result["score"] == 1
    assert result["components"]["hypertensive"]["met"] is True


def test_hypertensive_one_med():
    """1 antihypertensive -> 0 points."""
    result = calculate_h2fpef_score(num_antihypertensives=1)
    assert result["components"]["hypertensive"]["met"] is False


def test_hypertensive_three_meds():
    """3 antihypertensives -> +1 point (same as 2)."""
    result = calculate_h2fpef_score(num_antihypertensives=3)
    assert result["score"] == 1


def test_af_present():
    """AF present -> +3 points."""
    result = calculate_h2fpef_score(af_present=True)
    assert result["score"] == 3
    assert result["components"]["atrial_fibrillation"]["met"] is True


def test_af_absent():
    """AF absent -> 0 points."""
    result = calculate_h2fpef_score(af_present=False)
    assert result["score"] == 0


def test_pasp_over_35():
    """PASP > 35 -> +1 point."""
    result = calculate_h2fpef_score(pasp_mmhg=40)
    assert result["score"] == 1
    assert result["components"]["pulmonary_pressure"]["met"] is True


def test_pasp_under_35():
    """PASP <= 35 -> 0 points."""
    result = calculate_h2fpef_score(pasp_mmhg=30)
    assert result["components"]["pulmonary_pressure"]["met"] is False


def test_elder_over_60():
    """Age > 60 -> +1 point."""
    result = calculate_h2fpef_score(age=65)
    assert result["score"] == 1
    assert result["components"]["elder"]["met"] is True


def test_elder_under_60():
    """Age <= 60 -> 0 points."""
    result = calculate_h2fpef_score(age=55)
    assert result["components"]["elder"]["met"] is False


def test_elder_exactly_60():
    """Age exactly 60 -> NOT elder (>60 required)."""
    result = calculate_h2fpef_score(age=60.0)
    assert result["components"]["elder"]["met"] is False


def test_filling_pressure_over_9():
    """E/e' > 9 -> +1 point."""
    result = calculate_h2fpef_score(e_e_prime=12)
    assert result["score"] == 1
    assert result["components"]["filling_pressure"]["met"] is True


def test_filling_pressure_under_9():
    """E/e' <= 9 -> 0 points."""
    result = calculate_h2fpef_score(e_e_prime=7)
    assert result["components"]["filling_pressure"]["met"] is False


# =============================================================================
# Interpretation Category Tests
# =============================================================================

def test_low_probability():
    """Score 0-1 -> low probability."""
    result = calculate_h2fpef_score(bmi=22, age=40)
    assert result["category"] == "low"
    assert result["probability_percent"] == 9


def test_intermediate_probability():
    """Score 2-5 -> intermediate probability."""
    result = calculate_h2fpef_score(bmi=32, num_antihypertensives=2, age=65)
    assert result["score"] == 4  # 2+1+1
    assert result["category"] == "intermediate"
    assert result["probability_percent"] == 53


def test_high_probability():
    """Score 6-9 -> high probability."""
    result = calculate_h2fpef_score(
        bmi=35, num_antihypertensives=3, af_present=True,
        pasp_mmhg=50, age=75, e_e_prime=15,
    )
    assert result["score"] == 9
    assert result["category"] == "high"
    assert result["probability_percent"] == 91


def test_score_boundary_2():
    """Score exactly 2 -> intermediate."""
    result = calculate_h2fpef_score(bmi=32, af_present=False, age=50)
    assert result["score"] == 2
    assert result["category"] == "intermediate"


def test_score_boundary_6():
    """Score exactly 6 -> high."""
    result = calculate_h2fpef_score(
        bmi=32, num_antihypertensives=2, af_present=True, age=50,
    )
    assert result["score"] == 6  # 2+1+3
    assert result["category"] == "high"


# =============================================================================
# Boolean Shortcut Tests
# =============================================================================

def test_from_bools_all_false():
    result = calculate_h2fpef_from_bools()
    assert result["score"] == 0


def test_from_bools_all_true():
    result = calculate_h2fpef_from_bools(
        heavy=True, hypertensive=True, af=True,
        pulmonary_pressure=True, elder=True, filling_pressure=True,
    )
    assert result["score"] == 9


def test_from_bools_af_only():
    result = calculate_h2fpef_from_bools(af=True)
    assert result["score"] == 3


# =============================================================================
# Components Met/Not Met Tests
# =============================================================================

def test_components_met_list():
    """components_met should list only met criteria."""
    result = calculate_h2fpef_score(bmi=32, af_present=True)
    met_names = [c["name"] for c in result["components_met"]]
    assert "Heavy" in met_names
    assert "Atrial Fibrillation" in met_names
    assert len(result["components_met"]) == 2


def test_components_not_met_list():
    """components_not_met should list unmet criteria."""
    result = calculate_h2fpef_score(bmi=22, age=40)
    assert len(result["components_not_met"]) == 6


# =============================================================================
# HFA-PEFF Algorithm Tests
# =============================================================================

def test_hfa_peff_returns_steps():
    algo = get_hfa_peff_algorithm()
    assert "steps" in algo
    assert "step_1" in algo["steps"]
    assert "step_2" in algo["steps"]
    assert "step_3" in algo["steps"]


def test_hfa_peff_has_domains():
    algo = get_hfa_peff_algorithm()
    step2 = algo["steps"]["step_2"]
    assert "domains" in step2
    assert "functional" in step2["domains"]
    assert "morphological" in step2["domains"]
    assert "biomarker" in step2["domains"]


# =============================================================================
# CLI Tests
# =============================================================================

def test_cli_calculate():
    from cli import main
    rc = main(["calculate", "--bmi", "34", "--antihypertensives", "3", "--af", "--pasp", "42", "--age", "72", "--e-e-prime", "12"])
    assert rc == 0


def test_cli_quick():
    from cli import main
    rc = main(["quick", "--heavy", "--hypertensive", "--af", "--elder"])
    assert rc == 0


def test_cli_reference():
    from cli import main
    rc = main(["reference"])
    assert rc == 0


def test_cli_calculate_minimal():
    from cli import main
    rc = main(["calculate", "--age", "45"])
    assert rc == 0
