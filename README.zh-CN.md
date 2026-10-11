# signalframe

[English](README.md) · 中文

**本仓库是 [komako-workshop/digital-oracle](https://github.com/komako-workshop/digital-oracle) 的 fork**（在线演示：[oracle.komako.me](https://oracle.komako.me/)）。

上游是给 AI Agent 用的 Skill：接入大量免费金融数据源，用**交易价格**而不是新闻观点回答宏观/事件问题。  
`signalframe` 保留整套 provider，并加上可直接跑的产品壳：多源并发探测、双语网页、CLI、MCP —— 思路和 [memeframe](https://github.com/WILLIAMsykvg/memeframe) 一致。

## 原理（Digital Oracle）

1. **有效市场直觉** —— 真要紧的结果，会有人拿真钱下注；价格比短视频更认真。  
2. **只读定价信号** —— 预测市场概率、衍生品期限结构/IV、国债曲线、机构持仓、现货与情绪指数等。  
3. **Agent 流程** —— 拆问题 → 选 ≥3 路独立信号 → `gather()` 并行拉取 → 解释矛盾 → 结构化概率报告（见 `SKILL.md`）。  
4. **部分失败可容忍** —— 单源挂掉不影响其他源。

`signalframe` 不取代大模型写报告那一步，而是把「并行取数」变成你本地能跑、能接 Cursor 的工具。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
signalframe probe bitcoin
signalframe serve
```

浏览器打开 `http://127.0.0.1:8010`。

## License

MIT。上游 © 2026 komako-workshop；signalframe 新增部分 © 2026 WILLIAMsykvg。
