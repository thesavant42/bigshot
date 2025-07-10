#  BigShot

A LAN-first analytics dashboard and bounty research companion for Bug Bonty  programs (beginning with hackerone) — designed with operational paranoia, local-first ethos, and total deniability in mind.

Inspired by **Big Shot** from *Cowboy Bebop*.

---

## What BigShot Does

BigShot collects, filters, and visualizes HackerOne data to help you:

- See which companies are paying the most — and **when**
- Promote interesting bounty programs to your own **favorites list**
- Summarize bounty reports using a **local LLM** over MCP (no cloud required)
- Track your **ranking vs. peers** via the “Leeterboard”
- Maintain a **denylist** of low-payout or disinteresting programs
- Use date filters (7d/30d/90d) and severity filters to focus your research

All data is stored locally in **PostgreSQL**. No public dashboard, no telemetry, no nonsense.

---

## MVP Features

- ✅ Scheduled sync from HackerOne (REST + GraphQL)
- ✅ Local PostgreSQL ingestion
- ✅ Payout charts over 7/30/90d
- ✅ Favorites + Denylist filtering
- ✅ Severity filters
- ✅ Summarization via MCP (LMStudio + Qwen2.5)
- ✅ Leeterboard with ranked context window
- ✅ CLI + Web UI support (Gradio/React optional)

Planned later: multi-user auth, scope tagging, alternate UIs

---

##  Architecture Overview

Each module lives in `modules/` and includes:
- Functional code
- Module-specific README
- `agent_notes.md` for LLMs and human handoffs

Support folders:
- `db/` — schema, queries, migration helpers
- `scripts/` — adhoc tools like `sync_once.py`
- `ui/` — gradio, HTML templates, web components
- `tests/` — basic test scaffolds
- `docs/` — architecture, ambiguity log, developer guide

---

## ⚙️ Quickstart

```bash
git clone https://github.com/thesavant42/bigshot.git
cd bigshot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit your HackerOne creds + local LLM endpoint
python scripts/sync_once.py  # Dry run sync
```

---

##  MCP + Local Model

Summarization and analysis are delegated to a local LLM (e.g. Qwen2.5 via LMStudio).

Configure your `MCP_ENDPOINT=http://192.168.1.98:1234/v1/` and set:

```env
FAKE_API_KEY=fake_api_LMStudio
```

---

##  License

MIT or Apache 2.0 — to be decided. No warranty, no cloud.

---

> “The Big Shot TV Show, for bounty hunters across the galaxy.”  
> —Cowboy Bebop
