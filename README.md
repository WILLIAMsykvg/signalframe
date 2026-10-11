# signalframe

English · [中文说明](README.zh-CN.md)

**Fork of [komako-workshop/digital-oracle](https://github.com/komako-workshop/digital-oracle)** ([live demo](https://oracle.komako.me/)).

Upstream is an AI Agent Skill: many free market-data providers + a methodology that answers questions from **prices**, not news.  
`signalframe` keeps that library and adds a runnable product shell — concurrent probe, bilingual web UI, CLI, and MCP — in the same spirit as [memeframe](https://github.com/WILLIAMsykvg/memeframe).

> All you need to know is already priced in.

## How Digital Oracle works (原理)

1. **Efficient-market bet** — If an outcome matters, someone is already trading it. Price aggregates that bet better than a social-media take.
2. **Providers, not scrapers of opinions** — Polymarket / Kalshi probabilities, Deribit futures basis & IV, Treasury curves, CFTC positioning, CoinGecko spot, Fear & Greed, etc. Most need no API key.
3. **Agent workflow** — Understand the question → pick ≥3 independent signals → `gather()` in parallel → explain contradictions → structured probability report (`SKILL.md`).
4. **Partial failure** — One source dying must not kill the rest.

`signalframe` does **not** replace the LLM report step. It makes the data fan-out something you can run locally and wire into Cursor via MCP.

## What this fork adds

| | digital-oracle | signalframe |
| --- | --- | --- |
| Provider library | yes | yes (unchanged upstream package) |
| Skill / SKILL.md | yes | kept |
| Local `probe` CLI | demos only | `signalframe probe` |
| Concurrent keyword fan-out | `gather()` helper | opinionated 5-source probe |
| Web UI | hosted separately | `signalframe serve` |
| MCP tools | via Skill instructions | `probe_signals`, `list_signal_sources` |

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
signalframe sources
signalframe probe bitcoin
signalframe serve
```

Open `http://127.0.0.1:8010`.

```powershell
python -m signalframe.mcp_server
```

## Probe sources (default set)

- `polymarket` — event contracts matching the keyword  
- `fear_greed` — CNN Fear & Greed  
- `treasury` — latest US yield curve (2Y / 10Y)  
- `deribit` — BTC futures term structure  
- `coingecko` — BTC/ETH spot  

Full provider API remains under `digital_oracle/` and `references/`.

## License

MIT. Upstream copyright © 2026 komako-workshop. signalframe additions © 2026 WILLIAMsykvg. See [LICENSE](LICENSE).
