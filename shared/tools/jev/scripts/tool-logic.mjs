const MAX_STATE_BYTES = 100_000;

export function assertSafeStateSize(state) {
  let encoded;
  try {
    encoded = JSON.stringify(state);
  } catch {
    throw new Error("State must be JSON-serializable");
  }

  if (encoded === undefined) {
    throw new Error("State must be JSON-serializable");
  }
  if (Buffer.byteLength(encoded, "utf8") > MAX_STATE_BYTES) {
    throw new Error(`State exceeds the ${MAX_STATE_BYTES.toLocaleString()}-byte limit`);
  }
}

export function toJevQuestion(question) {
  if (question.type === "noul") {
    const criteria = {};
    if (question.trueCriteria) criteria.true = question.trueCriteria;
    if (question.falseCriteria) criteria.false = question.falseCriteria;
    return {
      type: "noul",
      instructions: question.instructions,
      ...(Object.keys(criteria).length > 0 ? { criteria } : {}),
    };
  }

  if (question.type === "choice") {
    return {
      type: "choice",
      instructions: question.instructions,
      criteria: question.choices,
    };
  }

  if (question.type === "score") {
    return {
      type: "score",
      instructions: question.instructions,
      criteria: question.criteria,
    };
  }

  throw new Error(`Unsupported Jev question type: ${question.type}`);
}

export function buildQuestionMap(questions) {
  const result = {};
  for (const question of questions) {
    if (Object.hasOwn(result, question.id)) {
      throw new Error(`Duplicate question id: ${question.id}`);
    }
    result[question.id] = toJevQuestion(question);
  }
  return result;
}

export function compactJevResult(response) {
  return {
    ...(response.model ? { model: response.model } : {}),
    answers: response.answers,
    ...(response.usage ? { usage: response.usage } : {}),
  };
}

export function noulResult(response, id, threshold) {
  const answer = response.answers[id];
  if (!answer || typeof answer.noul !== "number" || !Number.isFinite(answer.noul)) {
    throw new Error(`Jev returned an invalid noul answer for ${id}`);
  }

  return {
    probability: answer.noul,
    threshold,
    decision: answer.noul >= threshold,
    ...(response.model ? { model: response.model } : {}),
    ...(response.usage ? { usage: response.usage } : {}),
  };
}

export function choiceResult(response, id) {
  const answer = response.answers[id];
  if (
    !answer ||
    typeof answer.choice !== "string" ||
    typeof answer.confidence !== "number" ||
    answer.probabilities === null ||
    typeof answer.probabilities !== "object"
  ) {
    throw new Error(`Jev returned an invalid choice answer for ${id}`);
  }

  return {
    choice: answer.choice,
    confidence: answer.confidence,
    probabilities: answer.probabilities,
    ...(response.model ? { model: response.model } : {}),
    ...(response.usage ? { usage: response.usage } : {}),
  };
}

export function scoreResult(response, id) {
  const answer = response.answers[id];
  if (
    !answer ||
    typeof answer.score !== "number" ||
    typeof answer.confidence !== "number" ||
    answer.probabilities === null ||
    typeof answer.probabilities !== "object"
  ) {
    throw new Error(`Jev returned an invalid score answer for ${id}`);
  }

  return {
    score: answer.score,
    confidence: answer.confidence,
    probabilities: answer.probabilities,
    ...(response.model ? { model: response.model } : {}),
    ...(response.usage ? { usage: response.usage } : {}),
  };
}
