# H2FPEF Score for Heart Failure with Preserved Ejection Fraction

> **Cardiology - Heart Failure**  
> Reference: Reddy YNV et al. Circulation. 2018;138(9):861-870

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)

---

## Overview

A real implementation of the H2FPEF score for estimating the probability of Heart Failure with Preserved Ejection Fraction (HFpEF) in patients with unexplained dyspnea.

**H2FPEF Score Components (0-9 points):**
| Component | Criteria | Points |
|-----------|----------|--------|
| **H**eavy | BMI > 30 kg/m^2 | +2 |
| **2** (Hypertensive) | >= 2 antihypertensives | +1 |
| **F**ibrillation | AF (paroxysmal or persistent) | +3 |
| **P**ulmonary pressure | PASP > 35 mmHg on echo | +1 |
| **E**lder | Age > 60 years | +1 |
| **F**illing pressure | E/e' > 9 | +1 |

**Interpretation:**
| Score | Probability | Classification |
|-------|------------|---------------|
| 0-1 | 9% | Low probability |
| 2-5 | 53% | Intermediate probability |
| 6-9 | 91% | High probability |

Also includes the HFA-PEFF diagnostic algorithm as reference.

**No external dependencies** - uses only Python standard library.

---

## Quick Start

```bash
# Full calculation with clinical values
python cli.py calculate --bmi 34 --antihypertensives 3 --af --pasp 42 --age 72 --e-e-prime 12

# Quick calculation from boolean flags
python cli.py quick --heavy --hypertensive --af --elder

# Show HFA-PEFF algorithm reference
python cli.py reference
```

---

## Python API

```python
from h2fpef_score import calculate_h2fpef_score, calculate_h2fpef_from_bools, get_hfa_peff_algorithm

# Full calculation
result = calculate_h2fpef_score(
    bmi=34, num_antihypertensives=3, af_present=True,
    pasp_mmhg=42, age=72, e_e_prime=12,
)
print(f"Score: {result['score']}/9")
print(f"Probability: {result['probability_percent']}%")
print(f"Category: {result['label']}")

# Quick from booleans
result = calculate_h2fpef_from_bools(
    heavy=True, hypertensive=True, af=True, elder=True,
)
# -> score=7, high probability (91%)

# HFA-PEFF algorithm reference
algo = get_hfa_peff_algorithm()
```

---

## Clinical Reference

### H2FPEF Score Interpretation
| Score | HFpEF Probability | Action |
|-------|-------------------|--------|
| 0-1 | 9% (Low) | Consider alternative diagnoses |
| 2-5 | 53% (Intermediate) | Consider invasive hemodynamic testing |
| 6-9 | 91% (High) | Initiate HFpEF management |

### Maximum Score Breakdown
- Heavy (BMI >30): 2 points
- Hypertensive (>=2 meds): 1 point
- AF: 3 points (largest single contributor)
- PASP >35: 1 point
- Elder (>60): 1 point
- E/e' >9: 1 point
- **Maximum: 9 points**

### HFA-PEFF Algorithm (Alternative)
1. **Step 1**: Pre-test assessment (symptoms, risk factors, ECG, echo, BNP)
2. **Step 2**: HFA-PEFF score (functional, morphological, biomarker domains; max 6 points)
3. **Step 3**: Exercise hemodynamics (invasive PCWP measurement)

---

## Disclaimer

This tool is for **educational and clinical decision support purposes only**. It does not replace professional medical judgment. Always correlate with clinical context.

## License

MIT License. See [LICENSE](LICENSE) for details.
