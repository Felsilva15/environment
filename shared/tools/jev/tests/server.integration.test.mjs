import test from "node:test";
import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const pluginRoot = dirname(dirname(fileURLToPath(import.meta.url)));

test("MCP server advertises all Jev tools and status never exposes a key", async () => {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [join(pluginRoot, "scripts/server.mjs")],
    cwd: pluginRoot,
    env: {
      PATH: process.env.PATH ?? "",
      TYPESAFE_API_KEY: "integration-test-secret",
      TYPESAFE_JEV_MODEL: "jev-test",
    },
    stderr: "pipe",
  });
  const client = new Client({ name: "jev-plugin-test", version: "1.0.0" });

  try {
    await client.connect(transport);
    const listed = await client.listTools();
    assert.deepEqual(
      listed.tools.map((tool) => tool.name).sort(),
      ["jev_choice", "jev_decide", "jev_noul", "jev_score", "jev_status"],
    );

    const status = await client.callTool({ name: "jev_status", arguments: {} });
    const text = status.content.find((item) => item.type === "text")?.text ?? "";
    assert.match(text, /"configured": true/);
    assert.match(text, /"source": "environment"/);
    assert.equal(text.includes("integration-test-secret"), false);
  } finally {
    await client.close();
  }
});
