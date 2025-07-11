# AGENTS

`modules/` contains BigShot's core functionality. Each subfolder represents a module with its own README, AGENTS file and `agent_notes.md` for ongoing context.

Subfolders:
- `db/` - database schema and query helpers
- `favorites_manager/` - favorites and denylist logic
- `leeterboard/` - ranking calculations
- `report_parser/` - parse HackerOne report data
- `summarizer/` - send reports to local LLM
- `sync_engine/` - fetch data from HackerOne
- `mcp/` - HackerOne GraphQL MCP server
- `utils/` - shared helper utilities

Add new modules as peer directories and document them similarly.
