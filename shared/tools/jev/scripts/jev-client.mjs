export const SYSTEM_ONE_URL = "https://api.typesafe.ai/v1/systemone";
export const DEFAULT_MODEL = "jev-latest";

export function buildJevRequest({ apiKey, model = DEFAULT_MODEL, state, questions }) {
  if (!apiKey) {
    throw new Error("TypeSafe API key is not configured");
  }

  return {
    url: SYSTEM_ONE_URL,
    init: {
      method: "POST",
      headers: {
        authorization: `Bearer ${apiKey}`,
        "content-type": "application/json",
      },
      body: JSON.stringify({ model, state, questions }),
    },
  };
}

export function parseJevResponse({ status, ok, text }) {
  if (!ok) {
    throw new Error(`Jev request failed (${status}): ${text.slice(0, 300)}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("Jev returned malformed JSON");
  }

  if (
    parsed === null ||
    typeof parsed !== "object" ||
    parsed.answers === null ||
    typeof parsed.answers !== "object" ||
    Array.isArray(parsed.answers)
  ) {
    throw new Error("Jev response is missing an answers object");
  }

  return parsed;
}

export async function askJev(
  { apiKey, model = DEFAULT_MODEL, state, questions },
  fetcher = globalThis.fetch,
) {
  const request = buildJevRequest({ apiKey, model, state, questions });
  const response = await fetcher(request.url, {
    ...request.init,
    signal: AbortSignal.timeout(110_000),
  });

  return parseJevResponse({
    status: response.status,
    ok: response.ok,
    text: await response.text(),
  });
}
