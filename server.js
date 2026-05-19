import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const SUPPORTED_DATA_TYPES = ["integer", "decimal", "both"];
const configuredDataType = (process.env.SUPPORTED_DATA_TYPE ?? "both").toLowerCase();

if (!SUPPORTED_DATA_TYPES.includes(configuredDataType)) {
  throw new Error(
    `Invalid SUPPORTED_DATA_TYPE: "${configuredDataType}". Allowed values: ${SUPPORTED_DATA_TYPES.join(", ")}`
  );
}

const server = new McpServer({
  name: "calculator-mcp",
  version: "1.0.0"
});

const validateNumber = (value) => {
  if (!Number.isFinite(value)) {
    throw new Error("Inputs must be finite numbers.");
  }

  if (configuredDataType === "integer" && !Number.isInteger(value)) {
    throw new Error("Only integer inputs are supported by configuration.");
  }

  if (configuredDataType === "decimal" && Number.isInteger(value)) {
    throw new Error("Only decimal (non-integer) inputs are supported by configuration.");
  }
};

const schema = {
  a: z.number(),
  b: z.number()
};

const buildResult = (value) => ({
  content: [{ type: "text", text: String(value) }]
});

server.tool("add", "Add two numbers", schema, async ({ a, b }) => {
  validateNumber(a);
  validateNumber(b);
  return buildResult(a + b);
});

server.tool("subtract", "Subtract two numbers", schema, async ({ a, b }) => {
  validateNumber(a);
  validateNumber(b);
  return buildResult(a - b);
});

server.tool("multiply", "Multiply two numbers", schema, async ({ a, b }) => {
  validateNumber(a);
  validateNumber(b);
  return buildResult(a * b);
});

server.tool("divide", "Divide two numbers", schema, async ({ a, b }) => {
  validateNumber(a);
  validateNumber(b);
  if (b === 0) {
    throw new Error("Division by zero is not allowed.");
  }
  return buildResult(a / b);
});

const transport = new StdioServerTransport();
await server.connect(transport);
