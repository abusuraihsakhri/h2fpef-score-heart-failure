# H₂FPEF Score — HFpEF Calculator

Clinical point-score calculator for estimating the likelihood of heart failure with preserved ejection fraction (HFpEF) during evaluation of **adults with unexplained exertional dyspnea**.

## What it does

The H₂FPEF score assigns 0–9 points across six factors:

| Factor | Criterion | Points |
| --- | --- | ---: |
| Heavy | BMI > 30 kg/m² | 2 |
| Hypertensive | ≥ 2 antihypertensive medications | 1 |
| Atrial fibrillation | Paroxysmal or persistent AF | 3 |
| Pulmonary pressure | Echo-estimated PASP > 35 mmHg | 1 |
| Elder | Age > 60 years | 1 |
| Filling pressure | E/e′ > 9 | 1 |

Interpretation: **0–1 low**, **2–5 intermediate**, **6–9 high** likelihood. These categories are diagnostic aids, **not individualized probabilities**, definitive diagnoses, or treatment instructions. The Python API retains historical category-level percentages for compatibility and explicitly labels them as illustrative. The score is most applicable to its original diagnostic population; use clinical judgment and additional testing as indicated.

## Browser calculator

The static site lives in `web/`. It evaluates all six inputs using browser-native JavaScript; no server, account, API key, Python runtime, or external dependency is required. Each field is mandatory, with range and type validation. Results show the total score, likelihood category, and component contributions.

The browser site is designed for GitHub Pages. To serve it locally:

```bash
python -m http.server 8000
# Open http://localhost:8000/web/
```

**Privacy:** Clinical values entered in the browser are processed locally in memory. The browser calculator does not upload or persist entered data. Do not enter identifiable patient information into the optional API or audit/chat interfaces.

## Python CLI

Requires Python 3.10+.

```bash
python -m pip install -r requirements-dev.txt
python cli.py calculate --bmi 32 --antihypertensives 2 --af --pasp 40 --age 65 --e-e-prime 12
python cli.py quick --heavy --hypertensive --af --elder
python cli.py reference
python cli.py --json calculate --bmi 32 --antihypertensives 2 --af --pasp 40 --age 65 --e-e-prime 12
```

The CLI supports partial inputs for backwards compatibility but **warns when inputs are missing**; incomplete scores may underestimate likelihood. `quick` accepts six explicit criterion flags and treats omitted flags as negative by design. `reference` provides an abbreviated HFA-PEFF overview, not a full standalone HFA-PEFF implementation.

## Optional REST API and container

```bash
python -m pip install -r requirements.txt
uvicorn agents.api:app --host 127.0.0.1 --port 8000
# Open http://localhost:8000/docs
```

`POST /api/score` requires `bmi`, `num_antihypertensives`, `af_present`, `pasp_mmhg`, `age`, and `e_e_prime`; it returns the score and breakdown. `GET /health` provides a service health check. Existing generic audit and deterministic mock-chat endpoints remain available for compatibility; they do **not** perform HFpEF diagnosis.

For container use:

```bash
docker build -t h2fpef-score .
docker run --rm -p 8000:8000 h2fpef-score
# Or docker compose up --build
```

Set `AUDIT_SECRET_KEY` to a securely generated value when using audit functionality. Without it, an ephemeral key is used. Audit records are held only in process memory; the regular-expression identifier screen is not a comprehensive PHI de-identification system. Do not expose the optional API publicly without authentication and operational security controls.

## Tests and technology

```bash
pytest -q
node --test tests/web_score.test.mjs
node --check web/app.mjs
```

Python 3.10–3.12, FastAPI, Pydantic 2, JavaScript ES modules, HTML/CSS, and GitHub Actions. Browser support: current browsers supporting ES modules and standard HTML forms. No Pyodide is needed because the six-component point score is implemented directly in JavaScript for static deployment.

## Reference and license

Reddy YNV, Carter RE, Obokata M, Redfield MM, Borlaug BA. A Simple, Evidence-Based Approach to Help Guide Diagnosis of Heart Failure With Preserved Ejection Fraction. *Circulation*. 2018;138:861–870. [DOI: 10.1161/CIRCULATIONAHA.118.034646](https://doi.org/10.1161/CIRCULATIONAHA.118.034646).

Licensed under the [MIT License](LICENSE).
