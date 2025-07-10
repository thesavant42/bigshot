# ❓ Ambiguity Log

This document tracks key design decisions and open questions.

### ✅ Resolved

- Q: Should reports be summarized on ingest?
  - A: No. They’re summarized via action triggers only.

- Q: How are summaries updated?
  - A: New content is appended to the top of the existing summary field.

- Q: How is leaderboard data accessed?
  - A: The public-facing GraphQL endpoint is scraped using MCP patterns.

- Q: Where does user identity come from?
  - A: The username tied to the API Key (basic auth) maps to your HackerOne profile.

### ❓ Open Questions

- Should Gradio remain the UI layer, or migrate to React?
- Do we implement offline report editing?

