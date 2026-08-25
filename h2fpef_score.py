#!/usr/bin/env python3
"""
H2FPEF Score Calculator for Heart Failure with Preserved Ejection Fraction

The H2FPEF score estimates the probability of HFpEF based on clinical
and echocardiographic parameters. It was developed and validated by
Reddy YNV et al. to help diagnose HFpEF in patients with unexplained dyspnea.

H2FPEF Score Components (0-9 points):
- Heavy (BMI >30): +2
- Hypertensive (>=2 antihypertensives): +1
- AF (paroxysmal or persistent): +3
- Pulmonary pressure (PASP >35mmHg on echo): +1
- Elder (age >60): +1
- Filling pressure (E/e' >9): +1

References:
- Reddy YNV, Carter RE, Obokata M, Redfield MM, Borlaug BA. A Simple,
  Evidence-Based Approach to Help Guide Diagnosis of Heart Failure With
  Preserved Ejection Fraction. Circulation. 2018;138(9):861-870.

Author: Medical Calculator Project
License: MIT
"""

import math
from typing import Dict, Any, Optional


# =============================================================================
# SCORE COMPONENTS
# =============================================================================

SCORE_COMPONENTS = {
    "heavy": {
        "name": "Heavy",
        "description": "BMI > 30 kg/m^2",
        "points": 2,
        "criteria": "bmi > 30",
    },
    "hypertensive": {
        "name": "Hypertensive",
        "description": "On >= 2 antihypertensive medications",
        "points": 1,
        "criteria": "num_antihypertensives >= 2",
    },
    "atrial_fibrillation": {
        "name": "Atrial Fibrillation",
        "description": "Paroxysmal or persistent AF",
        "points": 3,
        "criteria": "af_present",
    },
    "pulmonary_pressure": {
        "name": "Pulmonary Pressure",
        "description": "PASP > 35 mmHg on echocardiography",
        "points": 1,
        "criteria": "pasp > 35",
    },
    "elder": {
        "name": "Elder",
        "description": "Age > 60 years",
        "points": 1,
        "criteria": "age > 60",
    },
    "filling_pressure": {
        "name": "Filling Pressure",
        "description": "E/e' ratio > 9",
        "points": 1,
        "criteria": "e_e_prime > 9",
    },
}

# Interpretation categories
INTERPRETATION = {
    "low": {
        "range": (0, 1),
        "probability": 0.09,
        "probability_percent": 9,
        "label": "Low probability of HFpEF",
        "description": "Low probability HFpEF (9%). Consider alternative diagnoses.",
        "recommendation": "Consider other causes of dyspnea. HFpEF unlikely.",
    },
    "intermediate": {
        "range": (2, 5),
        "probability": 0.53,
        "probability_percent": 53,
        "label": "Intermediate probability of HFpEF",
        "description": "Intermediate probability HFpEF (53%). Further evaluation recommended.",
        "recommendation": "Consider invasive hemodynamic testing with exercise to confirm.",
    },
    "high": {
        "range": (6, 9),
        "probability": 0.91,
        "probability_percent": 91,
        "label": "High probability of HFpEF",
        "description": "High probability HFpEF (91%). Diagnosis is very likely.",
        "recommendation": "Initiate HFpEF management. Consider guideline-directed medical therapy.",
    },
}


# =============================================================================
# CORE CALCULATION
# =============================================================================

def calculate_h2fpef_score(
    bmi: Optional[float] = None,
    num_antihypertensives: int = 0,
    af_present: bool = False,
    pasp_mmhg: Optional[float] = None,
    age: Optional[float] = None,
    e_e_prime: Optional[float] = None,
    heavy: Optional[bool] = None,
    hypertensive: Optional[bool] = None,
    pulmonary_pressure: Optional[bool] = None,
    elder: Optional[bool] = None,
    filling_pressure: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Calculate the H2FPEF score for HFpEF probability.
    
    Score components:
    - H (Heavy): BMI >30 -> +2 points
    - 2 (Hypertensive): >=2 antihypertensives -> +1 point
    - F (Fibrillation): AF present -> +3 points
    - P (Pulmonary): PASP >35 mmHg -> +1 point
    - E (Elder): Age >60 -> +1 point
    - F (Filling): E/e' >9 -> +1 point
    
    Total: 0-9 points
    
    Interpretation:
    - 0-1: Low probability (9%)
    - 2-5: Intermediate probability (53%)
    - 6-9: High probability (91%)
    
    Args:
        bmi: Body mass index in kg/m^2
        num_antihypertensives: Number of antihypertensive medications
        af_present: Whether atrial fibrillation is present
        pasp_mmhg: Pulmonary artery systolic pressure in mmHg
        age: Age in years
        e_e_prime: E/e' ratio from echocardiography
        heavy: Override for heavy component (if True, adds 2 points)
        hypertensive: Override for hypertensive component
        pulmonary_pressure: Override for pulmonary pressure component
        elder: Override for elder component
        filling_pressure: Override for filling pressure component
    
    Returns:
        Dictionary with H2FPEF score and interpretation
    """
    score = 0
    components = {}
    
    # H - Heavy (BMI > 30)
    is_heavy = heavy if heavy is not None else (bmi is not None and bmi > 30)
    if is_heavy:
        score += 2
    components["heavy"] = {
        "name": "Heavy",
        "criteria": "BMI > 30 kg/m^2",
        "value": bmi,
        "met": is_heavy,
        "points": 2 if is_heavy else 0,
    }
    
    # 2 - Hypertensive (>=2 antihypertensives)
    is_hypertensive = hypertensive if hypertensive is not None else (num_antihypertensives >= 2)
    if is_hypertensive:
        score += 1
    components["hypertensive"] = {
        "name": "Hypertensive",
        "criteria": ">= 2 antihypertensive medications",
        "value": num_antihypertensives,
        "met": is_hypertensive,
        "points": 1 if is_hypertensive else 0,
    }
    
    # F - Fibrillation (AF)
    if af_present:
        score += 3
    components["atrial_fibrillation"] = {
        "name": "Atrial Fibrillation",
        "criteria": "Paroxysmal or persistent AF",
        "value": af_present,
        "met": af_present,
        "points": 3 if af_present else 0,
    }
    
    # P - Pulmonary pressure (PASP > 35)
    is_elevated_pasp = pulmonary_pressure if pulmonary_pressure is not None else (pasp_mmhg is not None and pasp_mmhg > 35)
    if is_elevated_pasp:
        score += 1
    components["pulmonary_pressure"] = {
        "name": "Pulmonary Pressure",
        "criteria": "PASP > 35 mmHg",
        "value": pasp_mmhg,
        "met": is_elevated_pasp,
        "points": 1 if is_elevated_pasp else 0,
    }
    
    # E - Elder (age > 60)
    is_elder = elder if elder is not None else (age is not None and age > 60)
    if is_elder:
        score += 1
    components["elder"] = {
        "name": "Elder",
        "criteria": "Age > 60 years",
        "value": age,
        "met": is_elder,
        "points": 1 if is_elder else 0,
    }
    
    # F - Filling pressure (E/e' > 9)
    is_elevated_filling = filling_pressure if filling_pressure is not None else (e_e_prime is not None and e_e_prime > 9)
    if is_elevated_filling:
        score += 1
    components["filling_pressure"] = {
        "name": "Filling Pressure",
        "criteria": "E/e' > 9",
        "value": e_e_prime,
        "met": is_elevated_filling,
        "points": 1 if is_elevated_filling else 0,
    }
    
    # Interpret score
    if score <= 1:
        category = "low"
    elif score <= 5:
        category = "intermediate"
    else:
        category = "high"
    
    interp = INTERPRETATION[category]
    
    return {
        "score": score,
        "max_score": 9,
        "category": category,
        "probability": interp["probability"],
        "probability_percent": interp["probability_percent"],
        "label": interp["label"],
        "description": interp["description"],
        "recommendation": interp["recommendation"],
        "components": components,
        "components_met": [c for c in components.values() if c["met"]],
        "components_not_met": [c for c in components.values() if not c["met"]],
    }


def calculate_h2fpef_from_bools(
    heavy: bool = False,
    hypertensive: bool = False,
    af: bool = False,
    pulmonary_pressure: bool = False,
    elder: bool = False,
    filling_pressure: bool = False,
) -> Dict[str, Any]:
    """
    Simplified H2FPEF calculation from boolean flags.
    
    Args:
        heavy: BMI > 30
        hypertensive: >= 2 antihypertensives
        af: Atrial fibrillation present
        pulmonary_pressure: PASP > 35 mmHg
        elder: Age > 60
        filling_pressure: E/e' > 9
    
    Returns:
        Dictionary with H2FPEF score and interpretation
    """
    return calculate_h2fpef_score(
        heavy=heavy,
        hypertensive=hypertensive,
        af_present=af,
        pulmonary_pressure=pulmonary_pressure,
        elder=elder,
        filling_pressure=filling_pressure,
    )


def get_hfa_peff_algorithm() -> Dict[str, Any]:
    """
    Return the HFA-PEFF diagnostic algorithm as reference.
    
    The HFA-PEFF score is an alternative comprehensive diagnostic algorithm
    for HFpEF that includes:
    - Step 1: Pre-test assessment (symptoms, risk factors, ECG, echo, natriuretic peptides)
    - Step 2: HFA-PEFF score (functional, morphological, biomarker domains)
    - Step 3: Exercise hemodynamics (invasive testing)
    
    Returns:
        Dictionary with HFA-PEFF algorithm steps
    """
    return {
        "name": "HFA-PEFF Diagnostic Algorithm",
        "description": "European Society of Cardiology HFA-PEFF algorithm for HFpEF diagnosis",
        "reference": "Pieske B et al. Eur J Heart Fail. 2019;21(10):1169-1186",
        "steps": {
            "step_1": {
                "name": "Pre-test Assessment",
                "description": "Clinical assessment, ECG, echocardiography, natriuretic peptides",
                "criteria": [
                    "Typical symptoms: dyspnea, fatigue, exercise intolerance",
                    "Risk factors: age >60, hypertension, diabetes, obesity, AF",
                    "ECG: LVH, LAE, AF, ST-T changes",
                    "Echo: LVH, LAE, diastolic dysfunction, elevated E/e'",
                    "BNP > 35 pg/mL or NT-proBNP > 125 pg/mL (if in sinus rhythm)",
                    "BNP > 105 pg/mL or NT-proBNP > 365 pg/mL (if in AF)",
                ],
                "result": "If >= 1 abnormality -> proceed to Step 2",
            },
            "step_2": {
                "name": "HFA-PEFF Score",
                "description": "Comprehensive scoring across 3 domains (max 6 points)",
                "domains": {
                    "functional": {
                        "max_points": 2,
                        "criteria": [
                            "E/e' >= 9 (1 point)",
                            "TR velocity > 2.8 m/s (1 point)",
                        ],
                    },
                    "morphological": {
                        "max_points": 2,
                        "criteria": [
                            "LA volume index > 34 mL/m^2 (1 point)",
                            "LV mass index > 149 g/m^2 (male) or > 122 g/m^2 (female) (1 point)",
                            "Relative wall thickness > 0.42 (1 point)",
                        ],
                    },
                    "biomarker": {
                        "max_points": 2,
                        "criteria": [
                            "BNP > 105 pg/mL or NT-proBNP > 365 pg/mL (1 point)",
                            "BNP > 220 pg/mL or NT-proBNP > 730 pg/mL (2 points)",
                        ],
                    },
                },
                "interpretation": {
                    "0-1 points": "HFpEF unlikely -> consider alternative diagnosis",
                    "2-4 points": "Indeterminate -> proceed to Step 3",
                    "5-6 points": "HFpEF highly likely",
                },
            },
            "step_3": {
                "name": "Exercise Hemodynamics",
                "description": "Invasive hemodynamic testing with exercise",
                "criteria": [
                    "PCWP >= 25 mmHg during exercise",
                    "Or resting PCWP > 15 mmHg",
                ],
                "result": "Elevated filling pressures confirm HFpEF diagnosis",
            },
        },
    }
