# Dependency Mapping & Installation Order for Bigshot

This document provides a comprehensive dependency mapping table showing the exact order of operations for installation and setup, with clear environment specifications and CI/CD optimization recommendations.

## Installation Order Overview

The installation follows a specific dependency hierarchy to ensure all prerequisites are met before dependent components are installed.

## Phase-by-Phase Dependency Mapping

### Phase 1: System Foundation (Windows Environment)

| Order | Component | Environment | Command | Purpose | Time Estimate |
|-------|-----------|-------------|---------|---------|---------------|
| 1.1   | WSL2 Verification | Windows PowerShell (Admin) | `wsl --version` | Verify WSL2 installation | 1 min |
| 1.2   | Ubuntu 22.04 LTS | Windows PowerShell (Admin) | `wsl --install Ubuntu-22.04` | Install Linux distribution | 5-15 min |
| 1.3   | WSL2 Configuration | Windows (File System) | Edit `.wslconfig` | Configure resource allocation | 2 min |
| 1.4   | WSL2 Restart | Windows PowerShell | `wsl --shutdown && wsl` | Apply configuration | 1 min |

**Dependencies**: Windows 11 build 19041+
**Total Time**: 10-20 minutes

### Phase 2: System Packages (WSL2 Environment)

| Order | Component | Environment | Command | Purpose | Time Estimate |
|-------|-----------|-------------|---------|---------|---------------|
| 2.1   | System Update | WSL2 (Ubuntu) | `sudo apt update && sudo apt upgrade -y` | Update package database | 3-10 min |
| 2.2   | Build Essentials | WSL2 (Ubuntu) | `sudo apt install build-essential curl wget git...` | Install compilation tools | 2-5 min |
| 2.3   | Python Repository | WSL2 (Ubuntu) | `sudo add-apt-repository ppa:deadsnakes/ppa -y` | Add Python PPA | 1 min |
| 2.4   | Python 3.12+ | WSL2 (Ubuntu) | `sudo apt install python3.12 python3.12-venv...` | Install Python interpreter | 2-5 min |
| 2.5   | Node.js Repository | WSL2 (Ubuntu) | `curl -fsSL https://deb.nodesource.com/setup_20.x` | Add Node.js repository | 1 min |
| 2.6   | Node.js 20+ | WSL2 (Ubuntu) | `sudo apt install nodejs` | Install Node.js runtime | 2-5 min |
| 2.7   | PostgreSQL 15+ | WSL2 (Ubuntu) | `sudo apt install postgresql postgresql-contrib` | Install database server | 3-8 min |
| 2.8   | Redis 7+ | WSL2 (Ubuntu) | `sudo apt install redis-server` | Install caching/message broker | 1-3 min |

**Dependencies**: Working WSL2 Ubuntu installation
**Total Time**: 15-40 minutes

### Phase 3: Database & Service Configuration (WSL2 Environment)

| Order | Component | Environment | Command | Purpose | Time Estimate |
|-------|-----------|-------------|---------|---------|---------------|
| 3.1   | PostgreSQL Service | WSL2 (Ubuntu) | `sudo service postgresql start` | Start database service | 30 sec |
| 3.2   | PostgreSQL User | WSL2 (Ubuntu) | `sudo -u postgres psql -c "CREATE USER..."` | Create application user | 30 sec |
| 3.3   | PostgreSQL Database | WSL2 (Ubuntu) | `sudo -u postgres psql -c "CREATE DATABASE..."` | Create application database | 30 sec |
| 3.4   | Redis Service | WSL2 (Ubuntu) | `sudo service redis-server start` | Start caching service | 30 sec |
| 3.5   | Service Verification | WSL2 (Ubuntu) | `redis-cli ping` / PostgreSQL test | Verify services running | 1 min |

**Dependencies**: PostgreSQL and Redis packages installed
**Total Time**: 3-5 minutes

### Phase 4: Application Dependencies (WSL2 Environment)

| Order | Component | Environment | Command | Purpose | Time Estimate |
|-------|-----------|-------------|---------|---------|---------------|
| 4.1   | Repository Clone | WSL2 (Ubuntu) | `git clone https://github.com/thesavant42/bigshot.git` | Get source code | 1-2 min |
| 4.2   | Python Virtual Environment | WSL2 (Ubuntu) | `python -m venv venv` | Create isolated Python environment | 1 min |
| 4.3   | Environment Activation | WSL2 (Ubuntu) | `source venv/bin/activate` | Activate Python environment | 5 sec |
| 4.4   | Pip Upgrade | WSL2 (Ubuntu) - venv | `pip install --upgrade pip` | Update package manager | 30 sec |
| 4.5   | Python Dependencies | WSL2 (Ubuntu) - venv | `pip install -r requirements.txt` | Install Python packages | 3-10 min |
| 4.6   | Node.js Dependencies | WSL2 (Ubuntu) | `cd frontend && npm install` | Install JavaScript packages | 2-8 min |

**Dependencies**: Git, Python 3.12+, Node.js 20+, virtual environment
**Total Time**: 8-25 minutes

### Phase 5: Application Configuration (WSL2 Environment)

| Order | Component | Environment | Command | Purpose | Time Estimate |
|-------|-----------|-------------|---------|---------|---------------|
| 5.1   | Environment File | WSL2 (Ubuntu) | `cp .env.example .env` | Create configuration template | 10 sec |
| 5.2   | Environment Edit | WSL2 (Ubuntu) | `nano .env` (manual edit) | Configure application settings | 2-5 min |
| 5.3   | Database Initialization | WSL2 (Ubuntu) - venv | `flask db upgrade` | Set up database schema | 30 sec |
| 5.4   | Frontend Build | WSL2 (Ubuntu) | `cd frontend && npm run build` (optional) | Build production assets | 1-3 min |

**Dependencies**: Application dependencies installed, database running
**Total Time**: 4-10 minutes

## Detailed Dependency Specifications

### System-Level Dependencies

| Component | Minimum Version | Recommended Version | Installation Method | Environment |
|-----------|----------------|-------------------|-------------------|-------------|
| Windows | 11 (build 19041+) | Latest | Pre-installed | Windows |
| WSL2 | 2.0.0+ | Latest | `wsl --install` | Windows |
| Ubuntu | 22.04 LTS | 22.04 LTS | `wsl --install Ubuntu-22.04` | WSL2 |
| Git | 2.34+ | Latest | `sudo apt install git` | WSL2 |

### Runtime Dependencies

| Component | Minimum Version | Recommended Version | Installation Method | Environment |
|-----------|----------------|-------------------|-------------------|-------------|
| Python | 3.12.0 | 3.12.3+ | `sudo apt install python3.12` | WSL2 |
| Node.js | 20.0.0 | 20.19.3+ | NodeSource repository | WSL2 |
| npm | 10.0.0 | 10.8.2+ | Included with Node.js | WSL2 |
| PostgreSQL | 15.0 | 15.8+ | `sudo apt install postgresql` | WSL2 |
| Redis | 7.0.0 | 7.2+ | `sudo apt install redis-server` | WSL2 |

### Python Package Dependencies

| Package | Version Specification | Purpose | Install Order |
|---------|---------------------|---------|---------------|
| Flask | >=2.3.0 | Web framework | Core |
| Flask-SQLAlchemy | >=3.0.0 | Database ORM | Core |
| Flask-JWT-Extended | >=4.5.0 | Authentication | Core |
| Flask-CORS | >=4.0.0 | Cross-origin requests | Core |
| Flask-SocketIO | >=5.3.0 | WebSocket support | Core |
| psycopg2-binary | >=2.9.0 | PostgreSQL adapter | Database |
| celery[redis] | >=5.3.0 | Background tasks | Background |
| redis | >=4.6.0 | Redis client | Background |
| requests | >=2.31.0 | HTTP client | External |
| aiohttp | >=3.8.0 | Async HTTP client | External |
| python-socketio | >=5.8.0 | Socket.IO server | WebSocket |
| eventlet | >=0.33.0 | Async networking | WebSocket |
| python-dotenv | >=1.0.0 | Environment management | Config |
| openai | >=1.0.0 | LLM integration | AI |
| mcp | >=1.0.0 | MCP protocol | AI |
| pytest | >=7.4.0 | Testing framework | Testing |
| pytest-flask | >=1.2.0 | Flask testing | Testing |
| pytest-cov | >=4.1.0 | Coverage reporting | Testing |
| black | >=23.0.0 | Code formatting | Development |
| flake8 | >=6.0.0 | Code linting | Development |

### Node.js Package Dependencies

| Package | Version Specification | Purpose | Install Order |
|---------|---------------------|---------|---------------|
| react | ^19.1.0 | UI framework | Core |
| react-dom | ^19.1.0 | React DOM renderer | Core |
| react-router-dom | ^7.7.0 | Client-side routing | Core |
| @tanstack/react-query | ^5.83.0 | Data fetching | Core |
| axios | ^1.10.0 | HTTP client | Core |
| socket.io-client | ^4.8.1 | WebSocket client | Core |
| @headlessui/react | ^2.2.4 | UI components | UI |
| @heroicons/react | ^2.2.0 | Icon library | UI |
| tailwindcss | ^4.1.11 | CSS framework | Styling |
| typescript | ~5.8.3 | Type system | Development |
| vite | ^7.0.4 | Build tool | Development |
| vitest | ^2.0.0 | Testing framework | Testing |
| eslint | ^9.30.1 | Code linting | Development |

## CI/CD Optimization

### Pre-installed Packages for Speed

To optimize CI/CD pipeline speed, pre-install these packages in your CI environment:

#### System Packages (Ubuntu)
```bash
# Essential build tools
build-essential curl wget git software-properties-common
apt-transport-https ca-certificates gnupg lsb-release

# Development libraries
libpq-dev python3.12-dev

# Services (or use external services)
postgresql-client redis-tools
```

#### Python Packages (Global Cache)
```bash
# Core packages that rarely change
pip wheel Flask>=2.3.0 SQLAlchemy>=2.0.0 psycopg2-binary>=2.9.0
pip wheel pytest>=7.4.0 black>=23.0.0 flake8>=6.0.0
```

#### Node.js Packages (Global Cache)
```bash
# Base packages
npm install -g @types/node typescript
```

### Environment Variables for CI/CD

| Variable | Value | Purpose |
|----------|-------|---------|
| `POSTGRES_HOST` | External service URL | Use managed PostgreSQL |
| `REDIS_URL` | External service URL | Use managed Redis |
| `NODE_ENV` | `test` | Optimize for testing |
| `PYTHONPATH` | `./app` | Python import paths |
| `CI` | `true` | Enable CI-specific optimizations |

## Parallel Installation Strategy

For faster installation, these components can be installed in parallel:

### Parallel Group 1 (No Dependencies)
- System package updates
- Git repository clone
- Environment file creation

### Parallel Group 2 (After System Updates)
- Python 3.12 installation
- Node.js 20 installation
- PostgreSQL installation
- Redis installation

### Parallel Group 3 (After Runtime Installation)
- Python virtual environment creation
- Service configuration (PostgreSQL user/database)
- Service startup (PostgreSQL, Redis)

### Sequential Group (Must be sequential)
1. Python virtual environment activation
2. Python package installation
3. Node.js package installation
4. Database schema initialization
5. Application testing

## Troubleshooting Dependency Issues

### Common Dependency Conflicts

| Issue | Symptom | Solution |
|-------|---------|----------|
| Python version mismatch | Import errors, syntax errors | Use `python3.12` explicitly |
| Virtual environment not active | Packages not found | `source venv/bin/activate` |
| Node.js version too old | Build failures | Install Node.js 20+ from NodeSource |
| PostgreSQL connection refused | Database connection errors | `sudo service postgresql start` |
| Redis connection refused | Celery worker failures | `sudo service redis-server start` |
| Permission denied | File access errors | Fix file ownership: `chown -R $USER:$USER ~/bigshot` |

### Dependency Verification Commands

```bash
# Verify all critical dependencies
python --version        # Should be 3.12+
node --version         # Should be 20+
psql --version         # Should be 15+
redis-server --version # Should be 7+

# Verify Python packages
python -c "import flask; print(flask.__version__)"
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import celery; print(celery.__version__)"

# Verify Node.js packages
cd frontend
npm list react typescript vite

# Verify services
redis-cli ping  # Should return "PONG"
sudo -u postgres psql -c "SELECT version();"
```

## Performance Optimization Notes

### Installation Speed Optimization
1. **Package Caching**: Use package managers' cache features
2. **Parallel Downloads**: Enable concurrent package downloads
3. **Local Mirrors**: Use local package mirrors when available
4. **Incremental Installs**: Only install changed dependencies

### Runtime Performance Dependencies
1. **Database Connection Pooling**: Configured via SQLAlchemy settings
2. **Redis Persistence**: Configured for optimal memory usage
3. **Node.js Production Build**: Use `npm run build` for production

This dependency mapping ensures reproducible installations and provides clear guidance for both development and CI/CD environments.