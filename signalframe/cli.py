"""CLI for signalframe probes."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="signalframe",
        description="Probe priced-in market signals / 探测已定价的市场信号",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    probe_cmd = sub.add_parser("probe", help="Fan-out probe across sources / 多源并发探测")
    probe_cmd.add_argument("query", nargs="?", default="", help="Keyword, e.g. bitcoin / recession")
    probe_cmd.add_argument("--limit", type=int, default=5)
    probe_cmd.add_argument("--json", action="store_true")

    sub.add_parser("sources", help="List probe sources / 列出探测源")

    serve = sub.add_parser("serve", help="Run local web UI / 启动网页")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8010)

    sub.add_parser("mcp", help="Run MCP server on stdio")

    args = parser.parse_args(argv)

    if args.command == "mcp":
        from signalframe.mcp_server import main as mcp_main

        mcp_main()
        return

    if args.command == "serve":
        import uvicorn

        from signalframe.api import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return

    if args.command == "sources":
        print(
            json.dumps(
                [
                    {"id": "polymarket", "name": "Polymarket"},
                    {"id": "fear_greed", "name": "CNN Fear & Greed"},
                    {"id": "treasury", "name": "US Treasury"},
                    {"id": "deribit", "name": "Deribit BTC futures"},
                    {"id": "coingecko", "name": "CoinGecko spot"},
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    from signalframe.probe import probe

    result = probe(args.query, args.limit)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    print(f"query={result.query or '(empty)'}  {result.duration_ms}ms")
    for hit in result.signals:
        prob = "" if hit.probability is None else f"  p={hit.probability:.2f}"
        print(f"[{hit.source}] {hit.title}{prob}")
        print(f"  {hit.summary}")
    if result.errors:
        print(json.dumps(result.errors, ensure_ascii=False), file=sys.stderr)
    print(result.note)


if __name__ == "__main__":
    main()
