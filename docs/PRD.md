# Product Requirements Document (PRD): BigShot

## Overview

**BigShot** is a LAN-first analytics dashboard and bounty research companion for bug bounty programs, designed for operational privacy, local-first data handling, and total deniability. The initial focus is on HackerOne integration, with all data stored locally in PostgreSQL and no external telemetry.

## 1. Purpose

Enable bug bounty hunters and security researchers to efficiently analyze, track, and summarize bounty program data with full local control, advanced filtering, and privacy-preserving features.

## 2. Target Users

- Bug bounty hunters
- Security researchers
- Program managers seeking bounty insights

## 3. Key Features

- Scheduled sync from HackerOne (REST + GraphQL)
- Local PostgreSQL data ingestion and storage
- Payout analytics with time-based filters (7/30/90 days)
- Favorites and denylist management
- Severity-based filtering
- Report summarization using a local LLM (e.g., Qwen2.5 via LMStudio)
- Leaderboard (“Leeterboard”) for peer ranking
- CLI and Web UI (Gradio/React optional)

## 4. User & Feature Specifications

| Feature                | User Story Example                                                                 | Functional Notes                         |
|------------------------|-----------------------------------------------------------------------------------|------------------------------------------|
| Data Sync              | As a user, I want to sync HackerOne data locally, so I can analyze it offline.    | Scheduled/manual sync, error handling    |
| Payout Analytics       | As a user, I want to view payout trends over time, so I can prioritize programs.  | Charts for 7/30/90 days                  |
| Favorites/Denylist     | As a user, I want to curate my own target lists, so I can focus my research.      | Add/remove programs, persist locally     |
| Severity Filters       | As a user, I want to filter reports by severity, so I can focus on high-value bugs.| Multi-level filtering                    |
| Summarization          | As a user, I want to get AI-generated summaries of reports, so I can save time.   | Local LLM integration, privacy-first     |
| Leaderboard            | As a user, I want to compare my ranking with peers, so I can track my progress.   | Contextual ranking, privacy preserved    |
| CLI/Web UI             | As a user, I want both CLI and web interfaces, so I can use the tool flexibly.    | Gradio/React optional                    |

## 5. Acceptance Criteria

- Data sync completes successfully and handles network/API errors gracefully.
- Analytics charts accurately reflect local data for selected timeframes.
- Favorites and denylist persist across sessions and are editable.
- Severity filters return correct subsets of reports.
- Summarization works offline and does not leak data externally.
- Leaderboard updates with new data and reflects user’s current standing.
- Both CLI and Web UI are intuitive and accessible.

## 6. Data & API Documentation

- **Data Storage:** PostgreSQL schema for programs, reports, user preferences.
- **APIs:**
  - HackerOne REST & GraphQL endpoints for data sync.
  - Local endpoints for UI components (if applicable).
- **Data Flow:** Sync → Ingestion → Local Processing → Visualization/Summarization.

## 7. UX Flows

- **Onboarding:** User configures HackerOne credentials and local LLM endpoint.
- **Sync Flow:** User initiates or schedules data sync; progress and errors are displayed.
- **Analytics Flow:** User applies filters, views payout charts, and explores trends.
- **Curation Flow:** User adds/removes programs from favorites or denylist.
- **Summarization Flow:** User selects a report and receives an AI-generated summary.
- **Leaderboard Flow:** User views and sorts rankings among peers.

## 8. Non-Functional Requirements

- **Performance:** Fast data sync and query response times.
- **Security:** All data stored locally; no external telemetry or cloud sync.
- **Reliability:** Robust error handling for sync and data processing.
- **Scalability:** Capable of handling large datasets as user history grows.
- **Usability:** Simple, intuitive CLI and Web UI.

## 9. Operational & Testing Requirements

- **Setup:** Clear instructions for environment configuration, PostgreSQL setup, and LLM integration.
- **Maintenance:** Scripts for database migration, backup, and troubleshooting.
- **Testing:** Unit, integration, and end-to-end tests for all modules. Tests will be organized by subfeature being tested, and an agents.md will provide specific guidance for that tet.

## 10. Open Questions & Ownership

| Open Question                                            | Owner/Assignee      |
|----------------------------------------------------------|---------------------|
| How should MCP endpoint networking be configured for LLM? | [To be assigned]    |
| What is the final scope for multi-user authentication?    | [To be assigned]    |
| Which UI framework will be the default (Gradio/React)?   | [To be assigned]    |
| How will scope tagging and alternate UIs be prioritized?  | [To be assigned]    |
| What are the privacy guarantees for peer ranking data?    | [To be assigned]    |

## 11. Next Steps

- Expand each feature into detailed user stories and technical specs.
- Draft acceptance criteria for all features.
- Develop initial UX wireframes.
- Assign owners to open questions and unresolved areas.
- Prepare operational and test plans for MVP delivery.

This PRD outlines the high-level requirements and structure needed to move BigShot from concept to actionable development handoff[1].

[1] https://github.com/thesavant42/bigshot
[2] https://raw.githubusercontent.com/thesavant42/bigshot/refs/heads/main/docs/TODO.md
