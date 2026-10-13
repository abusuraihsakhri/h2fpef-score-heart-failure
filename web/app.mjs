import { scoreH2fpef } from "./score.mjs";

const form = document.getElementById("score-form");
const error = document.getElementById("error");
const result = document.getElementById("result");
const empty = document.getElementById("empty");
const scoreValue = document.getElementById("score-value");
const category = document.getElementById("category");
const interpretation = document.getElementById("interpretation");
const breakdown = document.getElementById("breakdown");

const COPY = {
  low: {
    label: "Low likelihood",
    text: "HFpEF is less likely in the original diagnostic context. Investigate other explanations for dyspnea where clinically appropriate."
  },
  intermediate: {
    label: "Intermediate likelihood",
    text: "The score alone does not resolve the diagnosis. Consider additional echocardiographic or exercise hemodynamic assessment based on clinical findings."
  },
  high: {
    label: "High likelihood",
    text: "HFpEF is more likely in the original diagnostic context. Correlate with symptoms, objective cardiac findings, and alternative diagnoses before making management decisions."
  }
};

function numberFrom(id) {
  const field = document.getElementById(id);
  if (!field.value.trim()) throw new RangeError("Complete all six clinical inputs.");
  const value = Number(field.value);
  if (!Number.isFinite(value)) throw new RangeError("Enter valid numeric values.");
  return value;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  error.hidden = true;
  try {
    const af = document.getElementById("af").value;
    if (af !== "true" && af !== "false") throw new TypeError("Select Yes or No for atrial fibrillation.");
    const input = {
      bmi: numberFrom("bmi"),
      antihypertensives: numberFrom("antihypertensives"),
      af: af === "true",
      pasp: numberFrom("pasp"),
      age: numberFrom("age"),
      ee: numberFrom("ee")
    };
    const assessment = scoreH2fpef(input);
    scoreValue.textContent = String(assessment.score);
    category.textContent = COPY[assessment.category].label;
    category.dataset.category = assessment.category;
    interpretation.textContent = COPY[assessment.category].text;
    breakdown.replaceChildren();
    for (const component of assessment.breakdown) {
      const row = document.createElement("tr");
      for (const text of [component.title, component.criterion, component.met ? "Yes" : "No", String(component.points)]) {
        const cell = document.createElement("td");
        cell.textContent = text;
        row.appendChild(cell);
      }
      breakdown.appendChild(row);
    }
    empty.hidden = true;
    result.hidden = false;
    result.focus();
  } catch (cause) {
    result.hidden = true;
    empty.hidden = false;
    error.textContent = cause.message || "Unable to calculate the score.";
    error.hidden = false;
    error.focus();
  }
});

form.addEventListener("reset", () => {
  result.hidden = true;
  error.hidden = true;
  empty.hidden = false;
});
