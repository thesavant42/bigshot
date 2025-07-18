# BigShot Docker Runbook

This guide describes how to build, run, and test BigShot using Docker and Docker Compose for development, testing, and production.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
- [Git](https://git-scm.com/downloads)
- **Node.js 20+** (required for Vite compatibility - containers use Node.js 20-alpine)
- Clone this repo:
  ```bash
  git clone https://github.com/thesavant42/bigshot.git
  cd bigshot
  ```

---

## 1. **Local Development**

### Build and Run (Dev Mode)
```bash
docker compose -f docker-compose.dev.yml up --build
```
- **Frontend (React):** http://localhost:3000  
- **Backend (Flask API):** http://localhost:5001  
- **Database:** localhost:5433 (user: bigshot, db: bigshot_dev, password: bigshot_dev_password)
- **Redis:** localhost:6380

### Hot Reload
- Backend and frontend use code bind-mounts for instant updates.

### Stopping Services
```bash
docker compose -f docker-compose.dev.yml down
```

---

## 2. **Production**

### Build and Run (Production)
1. **Set up environment variables** (e.g. in a `.env` file).
2. **Start services**:
   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```
   - Frontend: port 80 (HTTP), port 443 (HTTPS, if SSL configured)
   - Backend: port 5000
   - Database: port 5432
   - Redis: port 6379
   - Monitoring: Prometheus (9090), Grafana (3000)
3. **Stopping services**:
   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

---

## 3. **Testing**

### Running Backend Tests in Docker

- **Ad-hoc (dev):**
  ```bash
  docker compose -f docker-compose.dev.yml run --rm backend pytest
  ```
  *(Requires `pytest` in `requirements.txt` and tests in the repo)*

- **Ad-hoc (prod):**
  ```bash
  docker compose -f docker-compose.prod.yml run --rm backend pytest
  ```

- **You can also add a dedicated test service to your compose if desired.**

---

## 4. **Database Migrations**

- If using Flask-Migrate or Alembic, run migrations manually:
  ```bash
  docker compose -f docker-compose.dev.yml run --rm backend flask db upgrade
  ```
  *(Replace with your actual migration command if different)*

---

## 5. **Troubleshooting**

- **Logs:**  
  Use `docker compose logs -f <service>` to view logs.

- **Database/Redis Not Ready:**  
  Compose waits for DB/Redis healthchecks before starting backend/celery.

- **Node.js Version Issues:**  
  If you see `crypto.hash is not a function` errors in the frontend:
  - This indicates Node.js version incompatibility
  - Containers use Node.js 20-alpine (required for Vite 7.0.4+)
  - Rebuild with `--build` flag to pull latest base images:
    ```bash
    docker compose -f docker-compose.dev.yml up --build
    ```

- **Rebuilding Containers:**  
  If dependencies or code change, use `--build` flag:
  ```bash
  docker compose -f docker-compose.dev.yml up --build
  ```

- **Port Conflicts:**  
  Change the host ports in your compose files if they’re in use.

---

## 6. **CI/CD Notes**

- Use `docker build -t bigshot_backend .` and `docker build -t bigshot_frontend ./frontend` in your CI pipeline.
- Run backend tests using:
  ```bash
  docker run --rm bigshot_backend pytest
  ```
- For full integration, bring up all services with compose in your CI job.

---

## 7. **Configuration & Secrets**

- Use environment variables (or `.env` files) for secrets and API keys.
- **Never commit secrets to git.**

---

## 8. **Monitoring (Production Only)**

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (password via `GRAFANA_PASSWORD` environment variable)

---

## 9. **File/Directory Reference**

- **Backend:** Flask API, Celery worker (`Dockerfile` in root)
- **Frontend:** React app (`frontend/Dockerfile`, dev: `frontend/Dockerfile.dev`) - uses Node.js 20-alpine
- **Compose Files:**  
  - `docker-compose.yml` – generic/legacy  
  - `docker-compose.dev.yml` – development  
  - `docker-compose.prod.yml` – production

---

## 10. **Customizing**

- Edit `docker-compose.dev.yml` or `docker-compose.prod.yml` to adjust ports, volumes, or add/remove services.
- Update environment variables for your deployment or testing needs.

---

## 11. **More Help**

- See the `docs/` directory (if present) for more details.
- For Go-specific code (in `cmd/`, `internal/`, `lib/`), see language-specific docs.

---

**This runbook covers a full cycle: fresh clone → build → dev/prod usage → testing → CI/CD integration.**
