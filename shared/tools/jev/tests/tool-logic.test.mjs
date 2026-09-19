import test from "node:test";
import assert from "node:assert/strict";

import {
  assertSafeStateSize,
  buildQuestionMap,
  choiceResult,
  noulResult,
  scoreResult,
} from "../scripts/tool-logic.mjs";

test("buildQuestionMap converts all supported question types", () => {
  assert.deepEqual(
    buildQuestionMap([
      {
        id: "relevant",
        type: "noul",
        instructions: "Is it relevant?",
        trueCriteria: "Direct evidence",
      },
      {
        id: "category",
        type: "choice",
        instructions: "Choose a category",
        choices: { news: "A reported event", opinion: "A personal view" },
      },
      {
        id: "quality",
        type: "score",
        instructions: "Score quality",
        criteria: ["Poor", "Strong"],
      },
    ]),
    {
      relevant: {
        type: "noul",
        instructions: "Is it relevant?",
        criteria: { true: "Direct evidence" },
      },
      category: {
        type: "choice",
        instructions: "Choose a category",
        criteria: { news: "A reported event", opinion: "A personal view" },
      },
      quality: {
        type: "score",
        instructions: "Score quality",
        criteria: ["Poor", "Strong"],
      },
    },
  );
});

test("buildQuestionMap rejects duplicate ids", () => {
  assert.throws(
    () =>
      buildQuestionMap([
        { id: "same", type: "noul", instructions: "One" },
        { id: "same", type: "noul", instructions: "Two" },
      ]),
    /Duplicate question id/,
  );
});

test("state guard accepts normal JSON and rejects oversized state", () => {
  assert.doesNotThrow(() => assertSafeStateSize({ item: "small" }));
  assert.throws(() => assertSafeStateSize("x".repeat(100_001)), /exceeds/);
});

test("answer formatters retain uncertainty", () => {
  const response = {
    model: "jev-test",
    answers: {
      binary: { noul: 0.7 },
      category: { choice: "news", confidence: 0.8, probabilities: { news: 0.8, opinion: 0.2 } },
      quality: { score: 1, confidence: 0.6, probabilities: { 0: 0.4, 1: 0.6 } },
    },
  };

  assert.deepEqual(noulResult(response, "binary", 0.6), {
    probability: 0.7,
    threshold: 0.6,
    decision: true,
    model: "jev-test",
  });
  assert.equal(choiceResult(response, "category").choice, "news");
  assert.equal(scoreResult(response, "quality").score, 1);
});
