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
- ✅A: For MVP we can stick to Gradio, but React is in the disucssional mix.
-- Q: I want a modern UI with relativelty few and fixed ui optios, so that dont have to think about it looking good, just working well. React is nice necuse it makes app creation easy, but sice the database is hosted on site an app proabby doesnt matter much.

- Do we implement offline report editing?
- This is an interesting question, what do you mean by offline report editing?
  - - Clarifying question❓  Do you men hacker1 report submissions for points?
- An online connection to a third-party should not be considered a full-time requirement for this project, only when interacting with third paries.
  - ✅ This sounds interesting but needs clarity; the local database, postgres, is always on source of truth for the app, and is always "online".
    -- We *should* support externally inputting reports, but not as an mvp showstopper

