import test from "node:test";
import assert from "node:assert/strict";
import { scoreH2fpef } from "../web/score.mjs";

const baseline = { bmi: 30, antihypertensives: 1, af: false, pasp: 35, age: 60, ee: 9 };
test("all strict thresholds at boundary score zero", () => {
  const output = scoreH2fpef(baseline);
  assert.equal(output.score, 0);
  assert.equal(output.category, "low");
});
test("each component contributes exactly the published points", () => {
  const cases = [
    ["bmi", 30.01, 2],
    ["antihypertensives", 2, 1],
    ["af", true, 3],
    ["pasp", 35.01, 1],
    ["age", 60.01, 1],
    ["ee", 9.01, 1]
  ];
  for (const [key, value, points] of cases) {
    assert.equal(scoreH2fpef({ ...baseline, [key]: value }).score, points, key);
  }
});
test("maximum and categories", () => {
  const all = { bmi: 33, antihypertensives: 2, af: true, pasp: 44, age: 67, ee: 13 };
  assert.equal(scoreH2fpef(all).score, 9);
  assert.equal(scoreH2fpef(all).category, "high");
  assert.equal(scoreH2fpef({ ...baseline, bmi: 31 }).category, "intermediate");
  assert.equal(scoreH2fpef({ ...baseline, af: true, bmi: 31, antihypertensives: 2 }).score, 6);
});
test("reject missing, non-finite, untyped and fractional counts", () => {
  assert.throws(() => scoreH2fpef({ ...baseline, pasp: undefined }), RangeError);
  assert.throws(() => scoreH2fpef({ ...baseline, ee: Number.NaN }), RangeError);
  assert.throws(() => scoreH2fpef({ ...baseline, af: "false" }), TypeError);
  assert.throws(() => scoreH2fpef({ ...baseline, antihypertensives: 1.5 }), RangeError);
  assert.throws(() => scoreH2fpef({ ...baseline, age: -1 }), RangeError);
});
