import test from "node:test";
import assert from "node:assert/strict";

import {
  DEFAULT_MODEL,
  SYSTEM_ONE_URL,
  askJev,
  buildJevRequest,
  parseJevResponse,
} from "../scripts/jev-client.mjs";

test("buildJevRequest creates the System One request without exposing the key in the body", () => {
  const request = buildJevRequest({
    apiKey: "secret-test-key",
    state: { text: "hello" },
    questions: { useful: { type: "noul", instructions: "Is this useful?" } },
  });

  assert.equal(request.url, SYSTEM_ONE_URL);
  assert.equal(request.init.headers.authorization, "Bearer secret-test-key");
  assert.equal(JSON.parse(request.init.body).model, DEFAULT_MODEL);
  assert.equal(request.init.body.includes("secret-test-key"), false);
});

test("parseJevResponse accepts valid answers and rejects malformed bodies", () => {
  assert.deepEqual(
    parseJevResponse({ status: 200, ok: true, text: '{"answers":{"q":{"noul":0.8}}}' }),
    { answers: { q: { noul: 0.8 } } },
  );
  assert.throws(
    () => parseJevResponse({ status: 200, ok: true, text: "not-json" }),
    /malformed JSON/,
  );
  assert.throws(
    () => parseJevResponse({ status: 401, ok: false, text: "unauthorized" }),
    /Jev request failed \(401\)/,
  );
});

test("askJev supports an injected transport", async () => {
  let captured;
  const response = await askJev(
    {
      apiKey: "test",
      state: "state",
      questions: { q: { type: "noul", instructions: "Question" } },
    },
    async (url, init) => {
      captured = { url, init };
      return {
        status: 200,
        ok: true,
        async text() {
          return '{"model":"jev-test","answers":{"q":{"noul":0.75}}}';
        },
      };
    },
  );

  assert.equal(captured.url, SYSTEM_ONE_URL);
  assert.equal(captured.init.method, "POST");
  assert.equal(response.answers.q.noul, 0.75);
});
