#!/usr/bin/env python3
"""
Test script for the Calculator MCP server hosted on Azure Function App (or any HTTP endpoint).

Supports both Streamable HTTP and SSE transports.

Usage:
    # Test the default hosted URL
    python test_hosted.py

    # Test a custom URL
    python test_hosted.py --url https://your-function-app.azurewebsites.net/

    # Test with SSE transport explicitly
    python test_hosted.py --transport sse --url https://your-function-app.azurewebsites.net/sse
"""

import argparse
import asyncio
import sys

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

DEFAULT_URL = "https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/"
DEFAULT_SSE_URL = "https://testflexfunction-dre2eghthjc4ejd8.swedencentral-01.azurewebsites.net/sse"


async def run_tests(session: ClientSession) -> bool:
    """Run a set of calculator tests against the MCP session. Returns True if all pass."""
    await session.initialize()

    # List available tools
    tools_result = await session.list_tools()
    tool_names = [t.name for t in tools_result.tools]
    print(f"\n✅ Connected! Available tools: {tool_names}")

    test_cases = [
        ("add",      {"a": 5,   "b": 3},  "Result: 8"),
        ("subtract", {"a": 10,  "b": 4},  "Result: 6"),
        ("multiply", {"a": 6,   "b": 7},  "Result: 42"),
        ("divide",   {"a": 15,  "b": 3},  "Result: 5.0"),
        ("add",      {"a": 1.5, "b": 2.5}, "Result: 4.0"),
    ]

    all_passed = True
    print("\nRunning calculator tests:")
    for tool, args, expected_prefix in test_cases:
        result = await session.call_tool(tool, args)
        output = result.content[0].text if result.content else ""
        passed = output.startswith(expected_prefix)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {tool}({args}) → {output!r}  (expected prefix: {expected_prefix!r})")
        if not passed:
            all_passed = False

    # Test division by zero error handling
    result = await session.call_tool("divide", {"a": 5, "b": 0})
    output = result.content[0].text if result.content else ""
    passed = "error" in output.lower()
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}  divide({{a:5, b:0}}) → {output!r}  (expected: error message)")
    if not passed:
        all_passed = False

    return all_passed


async def test_streamable_http(url: str) -> bool:
    """Connect via Streamable HTTP transport and run tests."""
    print(f"\n🔗 Connecting via Streamable HTTP to: {url}")
    async with streamablehttp_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            return await run_tests(session)


async def test_sse(url: str) -> bool:
    """Connect via SSE transport and run tests."""
    print(f"\n🔗 Connecting via SSE to: {url}")
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            return await run_tests(session)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Test a hosted Calculator MCP server over HTTP"
    )
    parser.add_argument(
        "--url",
        default=None,
        help=(
            "Base URL of the hosted MCP server "
            f"(default: {DEFAULT_URL} for streamable-http, {DEFAULT_SSE_URL} for sse)"
        ),
    )
    parser.add_argument(
        "--transport",
        choices=["streamable-http", "sse", "auto"],
        default="auto",
        help=(
            "Transport to use. 'auto' tries streamable-http first, then falls back to SSE "
            "(default: auto)"
        ),
    )
    args = parser.parse_args()

    transport = args.transport
    url = args.url

    success = False

    if transport in ("streamable-http", "auto"):
        target = url or DEFAULT_URL
        try:
            success = await test_streamable_http(target)
        except Exception as exc:
            if transport == "streamable-http":
                print(f"\n❌ Streamable HTTP connection failed: {exc}", file=sys.stderr)
                sys.exit(1)
            print(f"\n⚠️  Streamable HTTP failed ({exc}), trying SSE transport…")
            transport = "sse"  # fall through to SSE

    if transport == "sse":
        target = url or DEFAULT_SSE_URL
        try:
            success = await test_sse(target)
        except Exception as exc:
            print(f"\n❌ SSE connection failed: {exc}", file=sys.stderr)
            sys.exit(1)

    print()
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
