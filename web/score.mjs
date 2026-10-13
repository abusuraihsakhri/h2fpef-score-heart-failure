/**
 * Reddy et al., Circulation 2018;138:861-870. DOI: 10.1161/CIRCULATIONAHA.118.034646
 * Deterministic H2FPEF point score. Does not estimate an individual probability.
 */
export const COMPONENTS = Object.freeze([
  { key: "heavy", title: "Heavy", criterion: "BMI > 30 kg/m²", points: 2 },
  { key: "hypertensive", title: "Hypertensive", criterion: "≥ 2 antihypertensive medications", points: 1 },
  { key: "af", title: "Atrial fibrillation", criterion: "Paroxysmal or persistent AF", points: 3 },
  { key: "pulmonary", title: "Pulmonary pressure", criterion: "PASP > 35 mmHg", points: 1 },
  { key: "elder", title: "Elder", criterion: "Age > 60 years", points: 1 },
  { key: "filling", title: "Filling pressure", criterion: "E/e′ > 9", points: 1 }
]);

const RANGES = Object.freeze({
  bmi: [5, 120],
  antihypertensives: [0, 20],
  pasp: [0, 200],
  age: [0, 150],
  ee: [0, 50]
});

export function scoreH2fpef(values) {
  if (!values || typeof values !== "object") throw new TypeError("Clinical inputs are required.");
  for (const [key, [min, max]] of Object.entries(RANGES)) {
    const value = values[key];
    if (typeof value !== "number" || !Number.isFinite(value) || value < min || value > max) {
      throw new RangeError(`${key} must be a finite number between ${min} and ${max}.`);
    }
  }
  if (!Number.isInteger(values.antihypertensives)) {
    throw new RangeError("The antihypertensive count must be a whole number.");
  }
  if (typeof values.af !== "boolean") throw new TypeError("Atrial fibrillation must be Yes or No.");

  const met = {
    heavy: values.bmi > 30,
    hypertensive: values.antihypertensives >= 2,
    af: values.af,
    pulmonary: values.pasp > 35,
    elder: values.age > 60,
    filling: values.ee > 9
  };
  const breakdown = COMPONENTS.map(({key, title, criterion, points}) => ({
    key, title, criterion, met: met[key], points: met[key] ? points : 0
  }));
  const score = breakdown.reduce((sum, item) => sum + item.points, 0);
  const category = score <= 1 ? "low" : score <= 5 ? "intermediate" : "high";
  return { score, maxScore: 9, category, breakdown };
}
