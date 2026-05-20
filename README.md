# Calculator MCP Server

A basic calculator MCP server with add, subtract, multiply, and divide tools built using Python and the MCP SDK.

## Features

- **Add**: Add two numbers
- **Subtract**: Subtract second number from first
- **Multiply**: Multiply two numbers
- **Divide**: Divide first number by second (with zero-check)
- **Configurable data type support**: integer, decimal, or both

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

The server requires configuration for supported data types. You can configure it in three ways (in priority order):

### 1. Config File (Recommended for Deployment)

Create a `config.json` file in the server directory:

```json
{
  "data_types": "both"
}
```

Supported values:
- `"both"` - Supports both integers and decimals
- `"integer"` - Only accepts integers
- `"decimal"` - Only accepts decimals (non-integers)

**Example:** Copy `config.example.json` to `config.json` and modify as needed.

### 2. Command-Line Argument

```bash
python server.py --data-types both
```

### 3. Environment Variable

```bash
# Windows
set CALCULATOR_DATA_TYPES=both
python server.py

# Unix/Linux/Mac
CALCULATOR_DATA_TYPES=both python server.py
```

## Running the Server

Once configured, simply run:

```bash
python server.py
```

Or with specific config file path:

```bash
python server.py --config /path/to/config.json
```

Or with command-line override:

```bash
python server.py --data-types integer
```

## Usage with MCP Client

The recommended approach is to configure the server via `config.json` at deployment, then the MCP client configuration becomes simple:

### Option 1: Using Config File (Recommended)

1. Create `config.json` in the server directory with your desired settings
2. Configure MCP client to just run the server:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["C:\\MCP_Calculator\\calculator_mcp\\server.py"]
    }
  }
}
```

### Option 2: Using Command-Line Argument

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:\\MCP_Calculator\\calculator_mcp\\server.py",
        "--data-types",
        "both"
      ]
    }
  }
}
```

### Option 3: Using Environment Variable (Legacy)

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

**Best Practice:** Use Option 1 (config file) for deployment. This separates server configuration from client configuration and follows MCP SDK standards.

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
