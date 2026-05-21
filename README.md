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

Or install as a package:

```bash
pip install -e .
```

## Configuration

The server supports multiple configuration methods with the following priority order:

### 1. pyproject.toml (Recommended - MCP Convention)

Configure in your `pyproject.toml` using MCP standard format:

```toml
[tool.mcp.config]
type = "object"

[tool.mcp.config.properties.data_types]
type = "string"
enum = ["integer", "decimal", "both"]
default = "both"
description = "Supported data types for calculations"
```

This follows the **MCP configuration convention** and allows MCP clients to discover and validate configuration options automatically.

### 2. Command-Line Arguments

```bash
python server.py --data-types both
```

Or if installed as package:

```bash
calculator-mcp --data-types integer
```

### 3. JSON Config File (Optional)

```bash
python server.py --config path/to/config.json
```

Where `config.json` contains:

```json
{
  "data_types": "both"
}
```

### 4. Environment Variable (Legacy)

```bash
# Windows
set CALCULATOR_DATA_TYPES=both
python server.py

# Unix/Linux/Mac
CALCULATOR_DATA_TYPES=both python server.py
```

## Running the Server

Once configured via `pyproject.toml`, simply run:

```bash
python server.py
```

Or with command-line override:

```bash
python server.py --data-types integer
```

## Usage with MCP Client

The recommended approach is to configure the server via `pyproject.toml`, then the MCP client configuration is simple:

### Option 1: Using pyproject.toml (Recommended)

1. Configure in `pyproject.toml` using MCP convention:
   ```toml
   [tool.mcp.config]
   type = "object"
   
   [tool.mcp.config.properties.data_types]
   type = "string"
   enum = ["integer", "decimal", "both"]
   default = "both"
   description = "Supported data types for calculations"
   ```

2. Configure MCP client to run the server:

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

### Option 3: Using JSON Config File

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": [
        "C:\\MCP_Calculator\\calculator_mcp\\server.py",
        "--config",
        "C:\\MCP_Calculator\\calculator_mcp\\config.json"
      ]
    }
  }
}
```

### Option 4: Using Environment Variable

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

**Best Practice:** Use Option 1 (pyproject.toml) for deployment. This keeps server configuration as part of the project, not the client configuration.

## Testing the Hosted MCP Server

If the server is deployed as an Azure Function App (or any HTTP host), you can test it without running the server locally.

### Hosted URL

```
https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/
```

### Option A: Python Test Script (Recommended)

Run the included `test_hosted.py` script. It automatically tries the **Streamable HTTP** transport first, then falls back to **SSE**:

```bash
# Install dependencies first
pip install -r requirements.txt

# Test the default hosted URL
python test_hosted.py

# Test a custom URL with Streamable HTTP
python test_hosted.py --url https://your-function-app.azurewebsites.net/

# Test with SSE transport explicitly
python test_hosted.py --transport sse --url https://your-function-app.azurewebsites.net/sse
```

Expected output:

```
🔗 Connecting via Streamable HTTP to: https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/

✅ Connected! Available tools: ['add', 'subtract', 'multiply', 'divide']

Running calculator tests:
  ✅ PASS  add({'a': 5, 'b': 3}) → 'Result: 8'
  ✅ PASS  subtract({'a': 10, 'b': 4}) → 'Result: 6'
  ✅ PASS  multiply({'a': 6, 'b': 7}) → 'Result: 42'
  ✅ PASS  divide({'a': 15, 'b': 3}) → 'Result: 5.0'
  ✅ PASS  add({'a': 1.5, 'b': 2.5}) → 'Result: 4.0'
  ✅ PASS  divide({a:5, b:0}) → 'Error: ...'

🎉 All tests passed!
```

### Option B: Configure an MCP Client (Claude Desktop / VS Code)

Point any MCP-compatible client directly at the hosted URL.

**Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "calculator": {
      "url": "https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/"
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "calculator": {
      "url": "https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/"
    }
  }
}
```

If your Function App uses the SSE transport, append `/sse` to the URL.

### Option C: Quick Smoke Test with curl

Check the server is reachable and returns a valid response:

```bash
# Streamable HTTP – send an initialize request
curl -s -X POST \
  https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "curl-test", "version": "1.0"}
    }
  }'

# SSE – open the event stream (Ctrl+C to stop)
curl -N \
  https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/sse
```

### Transport Notes

| Transport | Endpoint | When to use |
|-----------|----------|-------------|
| Streamable HTTP | `/` (or configurable path) | Modern MCP SDK ≥ 1.0; single POST endpoint |
| SSE | `/sse` + `/messages` | Legacy clients; persistent streaming connection |

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
