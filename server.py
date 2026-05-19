#!/usr/bin/env python3

import asyncio
import os
import sys

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server

# Configuration - can be set via environment variable
SUPPORTED_TYPES = os.getenv("CALCULATOR_DATA_TYPES", "both")  # "integer", "decimal", or "both"

def validate_number(value: float) -> float:
    """Validate number based on configured data type support."""
    if SUPPORTED_TYPES == "integer" and not isinstance(value, int) and value != int(value):
        raise ValueError(f"Only integers are supported. Got: {value}")
    
    if SUPPORTED_TYPES == "decimal" and value == int(value):
        raise ValueError(f"Only decimals are supported. Got: {value}")
    
    return value

# Create server instance
app = Server("calculator-mcp")

@app.tool()
async def add(a: float, b: float) -> str:
    """Add two numbers."""
    validate_number(a)
    validate_number(b)
    result = a + b
    return f"Result: {result}"

@app.tool()
async def subtract(a: float, b: float) -> str:
    """Subtract second number from first."""
    validate_number(a)
    validate_number(b)
    result = a - b
    return f"Result: {result}"

@app.tool()
async def multiply(a: float, b: float) -> str:
    """Multiply two numbers."""
    validate_number(a)
    validate_number(b)
    result = a * b
    return f"Result: {result}"

@app.tool()
async def divide(a: float, b: float) -> str:
    """Divide first number by second."""
    validate_number(a)
    validate_number(b)
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    result = a / b
    return f"Result: {result}"

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
