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

### 1. pyproject.toml (Recommended for Package Deployment)

Configure in your `pyproject.toml`:

```toml
[tool.calculator-mcp]
data_types = "both"  # Options: "integer", "decimal", or "both"
```

This is the **recommended approach** as it keeps configuration with your project metadata.

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

1. Configure in `pyproject.toml`:
   ```toml
   [tool.calculator-mcp]
   data_types = "both"
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
