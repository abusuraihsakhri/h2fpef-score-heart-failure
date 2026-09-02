# H2fpef Score Heart Failure

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_h2fpef_score()`**: Calculate the H2FPEF score for HFpEF probability.

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
- **`calculate_h2fpef_from_bools()`**: Simplified H2FPEF calculation from boolean flags.

Args:
    heavy: BMI > 30
    hypertensive: >= 2 antihypertensives
    af: Atrial fibrillation present
    pulmonary_pressure: PASP > 35 mmHg
    elder: Age > 60
    filling_pressure: E/e' > 9

Returns:
    Dictionary with H2FPEF score and interpretation
- **`get_hfa_peff_algorithm()`**: Return the HFA-PEFF diagnostic algorithm as reference.

The HFA-PEFF score is an alternative comprehensive diagnostic algorithm
for HFpEF that includes:
- Step 1: Pre-test assessment (symptoms, risk factors, ECG, echo, natriuretic peptides)
- Step 2: HFA-PEFF score (functional, morphological, biomarker domains)
- Step 3: Exercise hemodynamics (invasive testing)

Returns:
    Dictionary with HFA-PEFF algorithm steps

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate the H2FPEF score for HFpEF probability.
  score = 0
  return calculate_h2fpef_score(
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --json <value> --bmi <value> --antihypertensives <value> --af <value>
```

### Parameter Reference
- `--json`: Specifies input measurement or parameter value.
- `--bmi`: Specifies input measurement or parameter value.
- `--antihypertensives`: Specifies input measurement or parameter value.
- `--af`: Specifies input measurement or parameter value.
- `--pasp`: Specifies input measurement or parameter value.
- `--age`: Specifies input measurement or parameter value.
- `--e-e-prime`: Specifies input measurement or parameter value.
- `--heavy`: Specifies input measurement or parameter value.
- `--hypertensive`: Specifies input measurement or parameter value.
- `--pulmonary-pressure`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t h2fpef-score-heart-failure .
docker run -p 8000:8000 h2fpef-score-heart-failure
```
