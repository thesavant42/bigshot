# Windows 11 + WSL2 Installation Guide for Bigshot

This comprehensive guide provides step-by-step instructions for installing and setting up Bigshot on Windows 11 using WSL2 (Windows Subsystem for Linux 2). 

## Prerequisites

### System Requirements
- **Operating System**: Windows 11 (build 19041 or higher)
- **WSL2**: Must be installed and configured
- **Memory**: Minimum 8GB RAM recommended
- **Storage**: At least 5GB free space for dependencies and application

### Required Software Versions
- **Python**: 3.12+ (3.12.3 or later recommended)
- **Node.js**: 20+ (20.19.3 or later recommended)
- **PostgreSQL**: 15+ 
- **Redis**: 7+
- **Git**: Latest version

## Environment Setup Overview

This installation uses the following environment strategy:
- **Windows**: Used for WSL2 management, Docker Desktop (optional), and IDE/editor
- **WSL2**: Primary development environment for all application components
- **Python Environment**: `venv` virtual environment (conda also supported)

## Step-by-Step Installation

### Phase 1: WSL2 Setup (Windows Environment)

#### 1.1 Verify WSL2 Installation
**Environment**: Windows PowerShell (Run as Administrator)

```powershell
# Check WSL version
wsl --version

# List installed distributions
wsl --list --verbose
```

**Expected Output**: WSL version 2.x.x or higher

#### 1.2 Install Ubuntu 22.04 LTS (if not already installed)
**Environment**: Windows PowerShell (Run as Administrator)

```powershell
# Install Ubuntu 22.04 LTS
wsl --install Ubuntu-22.04

# Set as default distribution
wsl --set-default Ubuntu-22.04
```

#### 1.3 Configure WSL2 Resources
**Environment**: Windows

Create or update `C:\Users\<YourUsername>\.wslconfig`:

```ini
[wsl2]
memory=6GB
processors=4
swap=2GB
localhostForwarding=true
```

**Restart WSL** after making changes:
```powershell
wsl --shutdown
wsl
```

### Phase 2: System Dependencies (WSL2 Environment)

#### 2.1 Switch to WSL2
**Environment**: Windows Terminal or Command Prompt

```bash
wsl
```

All subsequent commands are executed in the WSL2 environment unless otherwise specified.

#### 2.2 Update System Packages
**Environment**: WSL2 (Ubuntu)

```bash
# Update package lists and upgrade system
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release
```

#### 2.3 Install Python 3.12+
**Environment**: WSL2 (Ubuntu)

```bash
# Add deadsnakes PPA for latest Python versions
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.12 and essential packages
sudo apt install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    python3.12-distutils

# Set Python 3.12 as default (optional but recommended)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Verify installation
python --version  # Should show Python 3.12.x
python3 --version  # Should show Python 3.12.x
```

#### 2.4 Install Node.js 20+
**Environment**: WSL2 (Ubuntu)

```bash
# Install Node.js using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x
```

#### 2.5 Install PostgreSQL 15+
**Environment**: WSL2 (Ubuntu)

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Start PostgreSQL service
sudo service postgresql start

# Configure PostgreSQL to start automatically
sudo systemctl enable postgresql

# Set up PostgreSQL user and database
sudo -u postgres psql -c "CREATE USER bigshot WITH PASSWORD 'your_secure_password_here';"
sudo -u postgres psql -c "CREATE DATABASE bigshot OWNER bigshot;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE bigshot TO bigshot;"

# Verify installation
sudo -u postgres psql -c "SELECT version();"
```

#### 2.6 Install Redis 7+
**Environment**: WSL2 (Ubuntu)

```bash
# Install Redis
sudo apt install -y redis-server

# Start Redis service
sudo service redis-server start

# Configure Redis to start automatically
sudo systemctl enable redis-server

# Verify installation
redis-cli ping  # Should return "PONG"
redis-server --version  # Should show Redis 7.x.x
```

### Phase 3: Application Setup (WSL2 Environment)

#### 3.1 Clone Repository
**Environment**: WSL2 (Ubuntu)

```bash
# Navigate to your preferred directory (e.g., home)
cd ~

# Clone the repository
git clone https://github.com/thesavant42/bigshot.git
cd bigshot

# Verify repository structure
ls -la
```

#### 3.2 Backend Setup with Virtual Environment
**Environment**: WSL2 (Ubuntu) - Repository root directory

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify virtual environment activation
which python  # Should show path in venv directory
which pip     # Should show path in venv directory

# Upgrade pip to latest version
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify key dependencies
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import celery; print(f'Celery: {celery.__version__}')"
```

#### 3.3 Environment Configuration
**Environment**: WSL2 (Ubuntu) - Repository root directory (venv activated)

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Required .env Configuration**:
```bash
# Database Configuration
POSTGRES_DB=bigshot
POSTGRES_USER=bigshot
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://bigshot:your_secure_password_here@localhost/bigshot

# Application Configuration
FLASK_ENV=development
SECRET_KEY=your_flask_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
```

#### 3.4 Database Initialization
**Environment**: WSL2 (Ubuntu) - Repository root directory (venv activated)

```bash
# Initialize Flask database
export FLASK_APP=run.py
flask db init    # If migrations folder doesn't exist
flask db migrate # Create migration
flask db upgrade # Apply migration

# Verify database connection
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('Database connection successful!')
    except Exception as e:
        print(f'Database connection failed: {e}')
"
```

#### 3.5 Frontend Setup
**Environment**: WSL2 (Ubuntu) - Frontend directory

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0

# Build frontend (optional, for production)
npm run build

# Return to repository root
cd ..
```

### Phase 4: Service Testing and Verification

#### 4.1 Start Required Services
**Environment**: WSL2 (Ubuntu) - Repository root directory

```bash
# Start PostgreSQL (if not already running)
sudo service postgresql start

# Start Redis (if not already running)
sudo service redis-server start

# Verify services are running
sudo service postgresql status
sudo service redis-server status
```

#### 4.2 Test Backend Services
**Environment**: WSL2 (Ubuntu) - Repository root directory (venv activated)

Open multiple terminal sessions for testing:

**Terminal 1 - Celery Worker**:
```bash
cd ~/bigshot
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**Terminal 2 - Flask Backend**:
```bash
cd ~/bigshot
source venv/bin/activate
python run.py
```

**Terminal 3 - Frontend Development Server**:
```bash
cd ~/bigshot/frontend
npm run dev
```

#### 4.3 Verify Application Access
**Environment**: Windows (Browser)

1. **Backend API**: http://localhost:5000
2. **Frontend Application**: http://localhost:5173
3. **Health Check**: http://localhost:5000/api/health

### Phase 5: Development Workflow

#### 5.1 Starting Development Environment
**Environment**: WSL2 (Ubuntu)

Create a startup script for convenience:

```bash
# Create startup script
cat > ~/bigshot/start_dev.sh << 'EOF'
#!/bin/bash

# Start required services
echo "Starting PostgreSQL..."
sudo service postgresql start

echo "Starting Redis..."
sudo service redis-server start

# Activate Python virtual environment
echo "Activating Python environment..."
source ~/bigshot/venv/bin/activate

echo "Development environment ready!"
echo "To start services:"
echo "1. Celery worker: celery -A celery_app worker --loglevel=info"
echo "2. Flask backend: python run.py"
echo "3. Frontend: cd frontend && npm run dev"
EOF

# Make script executable
chmod +x ~/bigshot/start_dev.sh
```

#### 5.2 Environment Activation Reminder
**Environment**: WSL2 (Ubuntu)

Always ensure your Python virtual environment is activated:

```bash
# Check if virtual environment is active
echo $VIRTUAL_ENV  # Should show path to venv

# If not active, activate it
source ~/bigshot/venv/bin/activate

# Verify activation
which python  # Should show venv path
which pip     # Should show venv path
```

## Testing Installation

### Run Backend Tests
**Environment**: WSL2 (Ubuntu) - Repository root directory (venv activated)

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test types
python -m pytest -m "unit"
python -m pytest -m "performance"
```

### Run Frontend Tests
**Environment**: WSL2 (Ubuntu) - Frontend directory

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Troubleshooting

### Common Issues and Solutions

#### WSL2 Issues
```bash
# WSL2 not responding
wsl --shutdown  # (Run in Windows)
wsl             # (Restart WSL2)

# Permission denied errors
sudo chown -R $USER:$USER ~/bigshot
```

#### Database Connection Issues
```bash
# PostgreSQL not running
sudo service postgresql restart

# Connection refused
sudo -u postgres psql -c "SELECT pg_reload_conf();"
```

#### Redis Connection Issues
```bash
# Redis not running
sudo service redis-server restart

# Port conflicts
sudo lsof -i :6379
```

#### Python Environment Issues
```bash
# Virtual environment not found
cd ~/bigshot
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Performance Optimization

### WSL2 Performance Tips
1. **Store files in WSL2 filesystem**: Keep project files in `~/bigshot` rather than `/mnt/c/`
2. **Configure WSL2 resources**: Adjust memory and CPU allocation in `.wslconfig`
3. **Use WSL2 terminals**: Use Windows Terminal with WSL2 profile for better performance

### Development Tips
1. **Use IDE integration**: Configure VS Code or PyCharm to work with WSL2
2. **File watching**: Ensure file watching works correctly for auto-reload
3. **Port forwarding**: WSL2 automatically forwards ports to Windows

## Next Steps

After successful installation:

1. **Read the User Guide**: See [docs/user_guide.md](user_guide.md)
2. **Review API Documentation**: See [docs/api.md](api.md)
3. **Understand Architecture**: See [docs/frontend_architecture.md](frontend_architecture.md)
4. **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Support

If you encounter issues:
1. **Check logs**: Review application logs for error messages
2. **Verify services**: Ensure PostgreSQL and Redis are running
3. **Environment**: Confirm virtual environment is activated
4. **Dependencies**: Verify all dependencies are correctly installed
5. **GitHub Issues**: Create an issue with detailed error information

For additional help, see [docs/troubleshooting.md](troubleshooting.md).