# System Overview

**BigShot** is a LAN-only HackerOne analytics dashboard designed to help bug bounty hunters:

- Track high-value bounty programs over time
- Promote interesting programs to a favorites list
- Use a local AI model to summarize bounty reports
- Visualize rankings with a HackerOne "Leeterboard"

All data lives locally — no external API calls once fetched.

### Key Modules
- **sync_engine/** — Pulls data from HackerOne via REST or GraphQL MCP
- **summarizer/** — Sends report data to a local LLM (via LMStudio)
- **leeterboard/** — Ranks users within bounty programs
- **favorites_manager/** — Allowlist / denylist logic
- **db/** — Schema, migrations, raw queries
- **ui/** — Optional Gradio or web UI for browsing results

