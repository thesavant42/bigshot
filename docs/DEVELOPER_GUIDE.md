# Developer Guide

## Setup

```bash
git clone https://github.com/thesavant42/bigshot.git
cd bigshot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `MCP_ENDPOINT` in `.env` to your LMStudio or MCP server URL.

## Running Tests

```bash
pytest tests/
```

## Module Development

Each module folder (`modules/{name}`) should include:
- Core logic in `.py` files
- `README.md` describing the purpose and usage
- `agent_notes.md` for passing context to other devs or AIs

## Look and Feel: DON'T USE EMOJI
