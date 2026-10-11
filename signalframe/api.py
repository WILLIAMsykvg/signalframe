"""Tiny bilingual web UI over the same probe path as CLI/MCP."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from signalframe.probe import probe

INDEX_PATH = Path(__file__).with_name("web") / "index.html"


def create_app() -> FastAPI:
    app = FastAPI(title="signalframe", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        return INDEX_PATH.read_text(encoding="utf-8")

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "service": "signalframe"}

    @app.get("/api/sources")
    def sources() -> dict:
        return {
            "sources": [
                {"id": "polymarket", "name": "Polymarket", "enabled": True},
                {"id": "fear_greed", "name": "Fear & Greed", "enabled": True},
                {"id": "treasury", "name": "US Treasury", "enabled": True},
                {"id": "deribit", "name": "Deribit", "enabled": True},
                {"id": "coingecko", "name": "CoinGecko", "enabled": True},
            ]
        }

    @app.get("/api/probe")
    def api_probe(q: str = "", limit: int = 5) -> dict:
        return probe(q, limit).to_dict()

    return app
