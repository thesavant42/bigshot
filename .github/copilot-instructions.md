## Pull Request Submission Policy

Do not submit pull requests if CI/CD jobs have failures. Instead:
- Use Context7 to research and understand the error.
- Apply the necessary fix.
- Re-run CI/CD jobs until all checks pass.
- Only submit the pull request when CI/CD is green.
## CI/CD Job Failure Handling

When a CI/CD job fails:
- Use Context7 MP to gather full context on the failure.
- Research the bug and investigate a solution.
- Automatically attach any fix recommendations as a markdown-formatted issue. The recommendation must be wrapped in a
  ```markdown
  ...recommendation content...
  ```
  codeblock, with all special characters safely encoded to prevent markdown formatting from breaking.

# Copilot Coding Agent Instructions for BigShot

This repository is a monorepo for the BigShot platform: a Flask (Python) backend and React (TypeScript) frontend for domain reconnaissance and AI-powered intelligence gathering. Follow these project-specific guidelines to maximize agent productivity and code quality.

## Architecture Overview
- **Backend**: Flask app (see `app/`, `server.py`, `run.py`) with modular API endpoints, background jobs (Celery), and integrations with external services (e.g., crt.sh, VirusTotal, Shodan).
- **Frontend**: React (TypeScript, Vite) in `frontend/` with a spreadsheet-style dashboard, LLM chat interface, and real-time job status via WebSockets.
- **Data Flow**: REST API and WebSocket communication between frontend and backend. Background jobs and external API calls are managed asynchronously.
- **Configuration**: Environment variables and config files in `config/`. Sensitive files and secrets are gitignored.

## Key Directories
- `app/`: Flask app modules (`api/`, `models/`, `services/`, `tasks/`, `utils/`)
- `frontend/`: React app (`src/`, `public/`, config and build files)
- `config/`: DB schema, migration, and environment config scripts
- `tests/`: Python backend tests (pytest)
- `docs/`: Architecture, API, testing, and deployment docs
- `scripts/`: DevOps and maintenance scripts

## Development Workflow
### Backend
- **Run dev server**: `python run.py` or `flask run` (ensure env vars are set)
- **Celery worker**: `celery -A celery_app.celery worker --loglevel=info`
- **Test**: `pytest` (see `pytest.ini`)
- **Lint/Format**: Use `black`, `flake8`, and `isort` (see `requirements.txt`)

### Frontend
- **Install deps**: `cd frontend && npm install`
- **Dev server**: `npm run dev`
- **Build**: `npm run build`
- **Test**: `npm run test` (Vitest)
- **Lint**: `npm run lint`

### Full System (Docker Compose)
- `docker-compose -f docker-compose.dev.yml up --build` (dev)
- `docker-compose -f docker-compose.prod.yml up -d` (prod)

## Project Conventions & Patterns
- **API**: RESTful, JSON responses, consistent error format, JWT or API key auth (see `app/api/`)
- **Background jobs**: Use Celery tasks for long-running or external API work (`app/tasks/`)
- **WebSockets**: Real-time updates for job status and chat (`app/api/chat.py`, frontend `src/components/chat/`)
- **Frontend state**: React Context + useReducer, Tailwind CSS for styling, Headless UI for primitives
- **Testing**: Table-driven/unit tests for backend (`tests/`), React Testing Library/Vitest for frontend
- **External integrations**: Each API integration is a separate module with mockable interfaces and robust error handling
- **Sensitive config**: Never commit secrets, DBs, or instance files (see `.gitignore`)

## Examples & References
- See `docs/architecture/spec.md` for detailed system and API design
- See `docs/frontend/frontend_architecture.md` for frontend structure and workflow
- See `docs/testing/testing.md` for test strategy and coverage
- See `docs/devops/cicd.md` for CI/CD and deployment

## When in Doubt
- Follow the structure and patterns of existing modules
- Reference the documentation in `docs/` for architecture, workflow, and conventions
- Prefer composition and modularity; keep logic testable and isolated
- Document new APIs and complex logic with docstrings and/or markdown in `docs/`
- Always use a context7 MCP tool when reviewing or writing code to ensure context-aware, high-quality contributions.
