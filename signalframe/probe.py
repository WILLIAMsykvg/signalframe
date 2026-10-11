"""Concurrent multi-source probe. One keyword → several priced-in signals."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from digital_oracle import (
    CoinGeckoPriceQuery,
    CoinGeckoProvider,
    DeribitFuturesCurveQuery,
    DeribitProvider,
    FearGreedProvider,
    PolymarketEventQuery,
    PolymarketProvider,
    USTreasuryProvider,
    YieldCurveQuery,
    gather,
)


@dataclass
class SignalHit:
    source: str
    title: str
    summary: str
    probability: float | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProbeResult:
    query: str
    duration_ms: int
    signals: list[SignalHit]
    errors: dict[str, str]
    note: str = (
        "Prices are market consensus, not advice. "
        "价格是市场共识，不是投资建议。"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "duration_ms": self.duration_ms,
            "signals": [asdict(item) for item in self.signals],
            "errors": self.errors,
            "note": self.note,
        }


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _polymarket(query: str, limit: int) -> list[SignalHit]:
    provider = PolymarketProvider()
    events = provider.list_events(
        PolymarketEventQuery(
            limit=max(limit, 10),
            active=True,
            closed=False,
            slug_contains=query.strip() or None,
        )
    )
    hits: list[SignalHit] = []
    for event in events[:limit]:
        market = event.primary_market()
        yes = market.yes_probability if market else None
        hits.append(
            SignalHit(
                source="polymarket",
                title=event.title,
                summary=f"Yes {_pct(yes)} · vol24h={event.volume_24hr or 0:.0f}",
                probability=yes,
                meta={"slug": event.slug, "liquidity": event.liquidity},
            )
        )
    return hits


def _fear_greed(_: str) -> list[SignalHit]:
    snap = FearGreedProvider().get_index()
    return [
        SignalHit(
            source="fear_greed",
            title="CNN Fear & Greed",
            summary=f"score={snap.score:.1f} · {snap.rating}",
            meta={"score": snap.score, "rating": snap.rating},
        )
    ]


def _treasury(_: str) -> list[SignalHit]:
    curve = USTreasuryProvider().latest_yield_curve(YieldCurveQuery())
    if curve is None:
        return [
            SignalHit(
                source="treasury",
                title="US Treasury yield curve",
                summary="no curve available",
            )
        ]
    y2 = curve.yield_for("2Y")
    y10 = curve.yield_for("10Y")
    spread = None if y2 is None or y10 is None else y10 - y2
    summary = f"date={curve.date} · 2Y={y2} 10Y={y10}"
    if spread is not None:
        summary += f" · 10Y-2Y={spread:.2f}%"
    return [
        SignalHit(
            source="treasury",
            title="US Treasury yield curve",
            summary=summary,
            meta={"date": curve.date, "y2": y2, "y10": y10, "spread_10y_2y": spread},
        )
    ]


def _deribit_btc(_: str) -> list[SignalHit]:
    ts = DeribitProvider().get_futures_term_structure(DeribitFuturesCurveQuery(currency="BTC"))
    perp = ts.perpetual()
    dated = [point for point in ts.points if not point.is_perpetual][:3]
    bits: list[str] = []
    if perp is not None:
        bits.append(f"perp mark={perp.mark_price}")
    for point in dated:
        if point.annualized_basis_vs_perpetual is not None:
            bits.append(f"{point.instrument_name} ann.basis={point.annualized_basis_vs_perpetual:.2%}")
        else:
            bits.append(point.instrument_name)
    return [
        SignalHit(
            source="deribit",
            title="BTC futures term structure",
            summary=" · ".join(bits) if bits else "no points",
            meta={"points": len(ts.points)},
        )
    ]


def _coingecko(query: str) -> list[SignalHit]:
    needle = query.strip().lower()
    if needle in {"eth", "ethereum"}:
        coin_id = "ethereum"
    else:
        coin_id = "bitcoin"
    prices = CoinGeckoProvider().get_prices(CoinGeckoPriceQuery(coin_ids=(coin_id,)))
    if not prices:
        return [
            SignalHit(
                source="coingecko",
                title=f"{coin_id} spot",
                summary="no price",
            )
        ]
    item = prices[0]
    change = item.price_change_24h_pct
    change_text = "n/a" if change is None else f"{change:.2f}%"
    return [
        SignalHit(
            source="coingecko",
            title=f"{item.coin_id} spot",
            summary=f"usd={item.price_usd} · 24h={change_text}",
            meta={
                "id": item.coin_id,
                "usd": item.price_usd,
                "usd_24h_change": item.price_change_24h_pct,
            },
        )
    ]


def probe(query: str, limit: int = 5) -> ProbeResult:
    started = time.perf_counter()
    limit = max(1, min(limit, 20))
    q = query.strip()
    tasks = {
        "polymarket": lambda: _polymarket(q, limit),
        "fear_greed": lambda: _fear_greed(q),
        "treasury": lambda: _treasury(q),
        "deribit": lambda: _deribit_btc(q),
        "coingecko": lambda: _coingecko(q),
    }
    gathered = gather(tasks, timeout_seconds=20, fail_fast=False)
    signals: list[SignalHit] = []
    for value in gathered.results.values():
        if isinstance(value, list):
            signals.extend(value)
    errors = {key: str(exc) for key, exc in gathered.errors.items()}
    return ProbeResult(
        query=q,
        duration_ms=int((time.perf_counter() - started) * 1000),
        signals=signals,
        errors=errors,
    )
