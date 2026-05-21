#!/usr/bin/env python3

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def load_config() -> str:
    """
    Load configuration with priority:
    1. Command-line argument (--data-types)
    2. pyproject.toml [tool.calculator-mcp] section
    3. Config file (config.json)
    4. Environment variable (CALCULATOR_DATA_TYPES)
    """
    parser = argparse.ArgumentParser(description="Calculator MCP Server")
    parser.add_argument(
        "--data-types",
        choices=["integer", "decimal", "both"],
        help="Supported data types: integer, decimal, or both"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to JSON configuration file (optional)"
    )
    
    args = parser.parse_args()
    
    # Priority 1: Command-line argument
    if args.data_types:
        return args.data_types
    
    # Priority 2: pyproject.toml [tool.mcp.config]
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'rb') as f:
                pyproject_data = tomllib.load(f)
                
                # Check for MCP convention: [tool.mcp.config]
                if "tool" in pyproject_data and "mcp" in pyproject_data["tool"]:
                    mcp_config = pyproject_data["tool"]["mcp"]
                    if "config" in mcp_config and "properties" in mcp_config["config"]:
                        properties = mcp_config["config"]["properties"]
                        if "data_types" in properties:
                            # Use the default value from the schema
                            data_types = properties["data_types"].get("default", "both")
                            if data_types in ["integer", "decimal", "both"]:
                                return data_types
                            else:
                                print(f"ERROR: Invalid data_types in pyproject.toml: '{data_types}'", file=sys.stderr)
                                print("Valid values: 'integer', 'decimal', or 'both'", file=sys.stderr)
                                sys.exit(1)
        except Exception as e:
            print(f"WARNING: Failed to read pyproject.toml: {e}", file=sys.stderr)
    
    # Priority 3: Config file (if specified)
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    if "data_types" in config_data:
                        data_types = config_data["data_types"]
                        if data_types in ["integer", "decimal", "both"]:
                            return data_types
                        else:
                            print(f"ERROR: Invalid data_types in config file: '{data_types}'", file=sys.stderr)
                            print("Valid values: 'integer', 'decimal', or 'both'", file=sys.stderr)
                            sys.exit(1)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in config file: {e}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"ERROR: Failed to read config file: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
    
    # Priority 4: Environment variable
    env_value = os.getenv("CALCULATOR_DATA_TYPES")
    if env_value:
        if env_value in ["integer", "decimal", "both"]:
            return env_value
        else:
            print(f"ERROR: Invalid CALCULATOR_DATA_TYPES value: '{env_value}'", file=sys.stderr)
            print("Valid values: 'integer', 'decimal', or 'both'", file=sys.stderr)
            sys.exit(1)
    
    # No configuration found
    print("ERROR: No configuration found for data_types", file=sys.stderr)
    print("Please provide configuration via one of:", file=sys.stderr)
    print("  1. Command-line: --data-types <integer|decimal|both>", file=sys.stderr)
    print("  2. pyproject.toml: [tool.mcp.config.properties.data_types] default = \"both\"", file=sys.stderr)
    print("  3. Config file: --config path/to/config.json", file=sys.stderr)
    print("  4. Environment variable: CALCULATOR_DATA_TYPES=both", file=sys.stderr)
    sys.exit(1)


# Load configuration at startup
SUPPORTED_TYPES = load_config()

def validate_number(value: float) -> float:
    """Validate number based on configured data type support."""
    if SUPPORTED_TYPES == "integer" and not isinstance(value, int) and value != int(value):
        raise ValueError(f"Only integers are supported. Got: {value}")
    
    if SUPPORTED_TYPES == "decimal" and value == int(value):
        raise ValueError(f"Only decimals are supported. Got: {value}")
    
    return value

# Create server instance
app = Server("calculator-mcp")

@app.list_tools()
async def handle_list_tools():
    """List available calculator tools."""
    from mcp.types import Tool
    
    data_type_info = (
        "integers and decimals" if SUPPORTED_TYPES == "both"
        else "integers only" if SUPPORTED_TYPES == "integer"
        else "decimals only"
    )
    
    return [
        Tool(
            name="add",
            description=f"Add two numbers (supports {data_type_info})",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="subtract",
            description=f"Subtract second number from first (supports {data_type_info})",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description=f"Multiply two numbers (supports {data_type_info})",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="divide",
            description=f"Divide first number by second (supports {data_type_info})",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Numerator"},
                    "b": {"type": "number", "description": "Denominator (cannot be zero)"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Handle calculator tool calls."""
    from mcp.types import TextContent
    
    try:
        a = validate_number(arguments["a"])
        b = validate_number(arguments["b"])
        
        if name == "add":
            result = a + b
        elif name == "subtract":
            result = a - b
        elif name == "multiply":
            result = a * b
        elif name == "divide":
            if b == 0:
                raise ValueError("Division by zero is not allowed")
            result = a / b
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(type="text", text=f"Result: {result}")]
    except Exception as error:
        return [TextContent(type="text", text=f"Error: {str(error)}")]

async def main():
    """Run the calculator MCP server."""
    print(f"Calculator MCP server running on stdio", file=sys.stderr)
    print(f"Supported data types: {SUPPORTED_TYPES}", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="calculator-mcp",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
