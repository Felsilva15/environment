import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { askJev, DEFAULT_MODEL } from "./jev-client.mjs";
import { credentialStatus, readApiKey } from "./credentials.mjs";
import {
  assertSafeStateSize,
  buildQuestionMap,
  choiceResult,
  compactJevResult,
  noulResult,
  scoreResult,
} from "./tool-logic.mjs";

const server = new McpServer({ name: "jev-decisions", version: "0.1.0" });

const stateSchema = z.union([
  z.string().max(100_000),
  z.array(z.unknown()),
  z.record(z.string(), z.unknown()),
]);
const instructionSchema = z.string().min(1).max(4_000);
const questionIdSchema = z.string().regex(/^[A-Za-z][A-Za-z0-9_-]{0,63}$/);
const choicesSchema = z
  .record(z.string().min(1).max(80), z.string().min(1).max(2_000))
  .refine((choices) => Object.keys(choices).length >= 2, "Provide at least two choices")
  .refine((choices) => Object.keys(choices).length <= 20, "Provide no more than 20 choices");

const noulQuestionSchema = z.object({
  id: questionIdSchema,
  type: z.literal("noul"),
  instructions: instructionSchema,
  trueCriteria: z.string().min(1).max(2_000).optional(),
  falseCriteria: z.string().min(1).max(2_000).optional(),
});
const choiceQuestionSchema = z.object({
  id: questionIdSchema,
  type: z.literal("choice"),
  instructions: instructionSchema,
  choices: choicesSchema,
});
const scoreQuestionSchema = z.object({
  id: questionIdSchema,
  type: z.literal("score"),
  instructions: instructionSchema,
  criteria: z.array(z.string().min(1).max(2_000)).min(1).max(50),
});

function textResult(payload) {
  return {
    content: [{ type: "text", text: JSON.stringify(payload, null, 2) }],
    structuredContent: payload,
  };
}

function errorResult(error) {
  const message = error instanceof Error ? error.message : String(error);
  return {
    isError: true,
    content: [{ type: "text", text: message }],
  };
}

function model() {
  return process.env.TYPESAFE_JEV_MODEL?.trim() || DEFAULT_MODEL;
}

async function request(state, questions) {
  assertSafeStateSize(state);
  return askJev({
    apiKey: readApiKey(),
    model: model(),
    state,
    questions,
  });
}

server.registerTool(
  "jev_status",
  {
    title: "Check Jev configuration",
    description: "Check whether this local plugin can find a TypeSafe API key. Never returns the key.",
    inputSchema: {},
  },
  async () => textResult({ ...credentialStatus(), model: model() }),
);

server.registerTool(
  "jev_noul",
  {
    title: "Ask a binary Jev question",
    description:
      "Send selected, non-secret state to TypeSafe Jev and return a probability plus a thresholded true/false decision.",
    inputSchema: {
      state: stateSchema.describe("Relevant JSON state or text. Do not include secrets or credentials."),
      question: instructionSchema,
      trueCriteria: z.string().min(1).max(2_000).optional(),
      falseCriteria: z.string().min(1).max(2_000).optional(),
      threshold: z.number().min(0).max(1).default(0.5),
    },
  },
  async ({ state, question, trueCriteria, falseCriteria, threshold }) => {
    try {
      const id = "decision";
      const questions = buildQuestionMap([
        { id, type: "noul", instructions: question, trueCriteria, falseCriteria },
      ]);
      return textResult(noulResult(await request(state, questions), id, threshold));
    } catch (error) {
      return errorResult(error);
    }
  },
);

server.registerTool(
  "jev_choice",
  {
    title: "Ask Jev to choose a category",
    description:
      "Send selected, non-secret state to TypeSafe Jev and choose one category with confidence and probabilities.",
    inputSchema: {
      state: stateSchema.describe("Relevant JSON state or text. Do not include secrets or credentials."),
      question: instructionSchema,
      choices: choicesSchema.describe("Map of choice labels to their decision criteria."),
    },
  },
  async ({ state, question, choices }) => {
    try {
      const id = "decision";
      const questions = buildQuestionMap([
        { id, type: "choice", instructions: question, choices },
      ]);
      return textResult(choiceResult(await request(state, questions), id));
    } catch (error) {
      return errorResult(error);
    }
  },
);

server.registerTool(
  "jev_score",
  {
    title: "Ask Jev for a rubric score",
    description:
      "Send selected, non-secret state to TypeSafe Jev and return a rubric score with confidence and probabilities.",
    inputSchema: {
      state: stateSchema.describe("Relevant JSON state or text. Do not include secrets or credentials."),
      question: instructionSchema,
      criteria: z.array(z.string().min(1).max(2_000)).min(1).max(50),
    },
  },
  async ({ state, question, criteria }) => {
    try {
      const id = "decision";
      const questions = buildQuestionMap([
        { id, type: "score", instructions: question, criteria },
      ]);
      return textResult(scoreResult(await request(state, questions), id));
    } catch (error) {
      return errorResult(error);
    }
  },
);

server.registerTool(
  "jev_decide",
  {
    title: "Ask Jev multiple questions",
    description:
      "Send selected, non-secret state to TypeSafe Jev and answer up to 20 mixed binary, choice, or score questions in one request.",
    inputSchema: {
      state: stateSchema.describe("Relevant JSON state or text. Do not include secrets or credentials."),
      questions: z
        .array(z.discriminatedUnion("type", [noulQuestionSchema, choiceQuestionSchema, scoreQuestionSchema]))
        .min(1)
        .max(20),
    },
  },
  async ({ state, questions }) => {
    try {
      return textResult(
        compactJevResult(await request(state, buildQuestionMap(questions))),
      );
    } catch (error) {
      return errorResult(error);
    }
  },
);

const transport = new StdioServerTransport();
await server.connect(transport);
