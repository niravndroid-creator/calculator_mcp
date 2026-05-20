# Calculator MCP Server

A basic calculator MCP server with add, subtract, multiply, and divide tools built using Python and the MCP SDK.

## Features

- **Add**: Add two numbers
- **Subtract**: Subtract second number from first
- **Multiply**: Multiply two numbers
- **Divide**: Divide first number by second (with zero-check)

## Configuration

**REQUIRED:** The `CALCULATOR_DATA_TYPES` environment variable must be set before starting the server.

Supported values:
- `both` - Supports both integers and decimals
- `integer` - Only accepts integers
- `decimal` - Only accepts decimals (non-integers)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

**Windows:**
```bash
set CALCULATOR_DATA_TYPES=both
python server.py
```

**Unix/Linux/Mac:**
```bash
CALCULATOR_DATA_TYPES=both python server.py
```

**Examples with different configurations:**
```bash
# Integer-only mode
set CALCULATOR_DATA_TYPES=integer && python server.py

# Decimal-only mode
set CALCULATOR_DATA_TYPES=decimal && python server.py
```

## Usage with MCP Client

Add to your MCP client configuration. **Note:** The `CALCULATOR_DATA_TYPES` environment variable is required:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["C:\\MCP_Calculator\\calculator_mcp\\server.py"],
      "env": {
        "CALCULATOR_DATA_TYPES": "both"
      }
    }
  }
}
```

The server will fail to start if `CALCULATOR_DATA_TYPES` is not set or has an invalid value.

## Available Tools

- `add(a, b)` - Returns a + b
- `subtract(a, b)` - Returns a - b
- `multiply(a, b)` - Returns a × b
- `divide(a, b)` - Returns a ÷ b (throws error if b = 0)

## Examples

With data types set to "both":
- `add(5, 3)` → 8
- `add(5.5, 3.2)` → 8.7
- `divide(10, 2)` → 5

With data types set to "integer":
- `add(5, 3)` → 8
- `add(5.5, 3)` → Error (decimals not supported)

With data types set to "decimal":
- `add(5.5, 3.2)` → 8.7
- `add(5, 3)` → Error (integers not supported)
