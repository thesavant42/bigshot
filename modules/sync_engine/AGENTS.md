# AGENTS

Responsible for fetching HackerOne activity. Implements retry and backoff logic around the MCP endpoints.

Key files:
- `fetch_hacktivity.py` - pulls new reports
- `backoff_handler.py` - handles rate limits
- `agent_notes.md` - ongoing design notes
