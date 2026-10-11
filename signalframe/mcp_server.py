"""MCP tools: probe_signals, list_signal_sources."""

from __future__ import annotations

import json
import sys


def build_mcp():
    try:
        from mcp.server import MCPServer
    except ImportError:  # pragma: no cover
        from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore

    server = MCPServer("signalframe")

    @server.tool()
    def list_signal_sources() -> str:
        """List the market data sources used by signalframe probes."""
        return json.dumps(
            [
                "polymarket",
                "fear_greed",
                "treasury",
                "deribit",
                "coingecko",
            ]
        )

    @server.tool()
    def probe_signals(query: str = "", limit: int = 5) -> str:
        """Fan out across prediction markets and macro/crypto signals for a keyword."""
        from signalframe.probe import probe

        return json.dumps(probe(query, limit).to_dict(), ensure_ascii=False)

    return server


def main() -> None:
    # Keep stdout clean for the MCP protocol.
    sys.stderr.write("signalframe mcp starting\n")
    server = build_mcp()
    if hasattr(server, "run"):
        server.run()
    else:  # pragma: no cover
        raise RuntimeError("unsupported MCP server API")


if __name__ == "__main__":
    main()
