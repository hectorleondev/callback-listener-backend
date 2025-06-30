# Development Setup Guide

This guide will help you set up the CallbackListener backend for development.

## Prerequisites

- **Docker & Docker Compose**: For containerized development
- **Python 3.11+**: For local development
- **uv**: Modern Python package manager - `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git**: For version control
- **Make**: For using the Makefile commands

### Optional Tools
- **PostgreSQL**: If running database locally
- **Redis**: For future caching features
- **curl**: For testing API endpoints

## Quick Setup (Recommended)

The fastest way to get started is using Docker:

```bash
# Navigate to backend directory
cd /Users/payorayo/AI_PROJECTS/callback_listener/backend

# Complete setup in one command
make setup-dev

# Start development environment
make dev
```

This will:
1. Copy environment template
2. Install Python dependencies
3. Set up pre-commit hooks
4. Start database container
5. Run database migrations
6. Start the application

## Manual Setup

### 1. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your settings
# The defaults should work for Docker development
```

### 2. Python Environment

```bash
# Create virtual environment (optional with uv)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies using uv (much faster than pip)
uv pip install -r requirements.txt

# Install development tools
make install
```

### 3. Database Setup

#### Option A: Docker (Recommended)
```bash
# Start just the database
docker-compose up -d db

# Wait for database to be ready
sleep 10

# Run migrations
flask db upgrade
```

#### Option B: Local PostgreSQL
```bash
# Install PostgreSQL locally
# Create database and user as specified in .env

# Run migrations
FLASK_ENV=development flask db upgrade
```

### 4. Start Application

```bash
# Using make command
make run

# Or directly with Python
python run.py

# Or with Flask development server
flask run
```

## Development Workflow

### Daily Development

```bash
# Start services
make dev

# In another terminal, run tests
make test-local

# Check code quality
make lint format

# View logs
make logs

# Stop services when done
make stop
```

### Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes with TDD**:
   ```bash
   # Write tests first
   # Then implement feature
   
   # Run specific tests
   make test-unit
   make test-api
   ```

3. **Check code quality**:
   ```bash
   make quick-test  # Runs format, lint, and test
   ```

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks will run automatically
   # Changelog will be updated automatically
   ```

### Package Management with uv

uv is a fast Python package manager that's significantly faster than pip:

```bash
# Install dependencies
make install

# Add a new package
make add-package pkg=requests

# Remove a package
make remove-package pkg=requests

# Update all dependencies
make update-deps

# Sync exact dependencies
make sync-deps

# Install only development dependencies
make install-dev
```

### Database Operations

```bash
# Create new migration
make migrate-create msg="Add new field to users"

# Apply migrations
make migrate

# Rollback migration
make migrate-rollback

# Reset database (WARNING: destroys data)
make db-reset

# Backup/restore
make db-backup file=backup.sql
make db-restore file=backup.sql

# Database shell
make db-shell
```

### Testing

```bash
# All tests
make test

# Specific test categories
make test-unit
make test-api
make test-services

# With coverage report
make test-coverage

# Local tests (faster, requires local DB)
make test-local
```

## Debugging

### Enable Debug Mode

```bash
# In .env file
FLASK_DEBUG=true
LOG_LEVEL=DEBUG

# Restart application
make stop
make dev
```

### View Detailed Logs

```bash
# All services
make logs

# Specific service
make logs-web
make logs-db

# Follow logs
docker-compose logs -f web
```

### Database Debugging

```bash
# Connect to database
make db-shell

# View tables
\dt

# View table structure
\d paths
\d requests

# View sample data
SELECT * FROM paths LIMIT 5;
```

### Application Debugging

```bash
# Python shell with app context
make shell

# Test API endpoints
curl http://localhost:5000/health/
curl -X POST http://localhost:5000/api/paths
```

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true
}
```

### PyCharm

1. Set Python interpreter to `./venv/bin/python`
2. Enable Black formatter
3. Configure isort with Black profile
4. Set up run configuration for `run.py`

## Performance Testing

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu
brew install httpie                  # macOS

# Create test path
curl -X POST http://localhost:5000/api/paths

# Load test webhook endpoint (replace path_id)
ab -n 1000 -c 10 http://localhost:5000/webhook/your-path-id
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Profile specific function
python -m memory_profiler app/api/webhooks.py
```

## Troubleshooting

### Common Issues

**Port 5000 already in use:**
```bash
# Find process using port
lsof -i :5000

# Kill process or change port in .env
FLASK_PORT=5001
```

**Database connection refused:**
```bash
# Check database status
make health

# Restart database
docker-compose restart db

# Check database logs
make logs-db
```

**Permission denied errors:**
```bash
# Fix file permissions
chmod +x scripts/*.py

# Fix Docker permissions
sudo chown -R $USER:$USER .
```

**Migration errors:**
```bash
# Reset migrations
rm -rf migrations/versions/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Getting Help

1. Check the logs: `make logs`
2. Review the README.md
3. Check existing issues in the repository
4. Run health checks: `make health`
5. Verify environment: `printenv | grep FLASK`

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | development | Application environment |
| `FLASK_DEBUG` | true | Enable debug mode |
| `FLASK_HOST` | 0.0.0.0 | Host to bind to |
| `FLASK_PORT` | 5000 | Port to listen on |
| `DATABASE_URL` | postgres://... | Database connection string |
| `SECRET_KEY` | generated | Flask secret key |
| `LOG_LEVEL` | INFO | Logging level |

## Development Best Practices

1. **Always write tests first** (TDD)
2. **Use the pre-commit hooks** (automatically installed)
3. **Update CHANGELOG.md** (automated via git hooks)
4. **Follow code style** (enforced by pre-commit)
5. **Use meaningful commit messages** (conventional commits)
6. **Keep functions small** (<20 lines)
7. **Document your code** (docstrings)
8. **Handle errors gracefully** (try/catch with logging)
9. **Use environment variables** for configuration
10. **Test edge cases** and error conditions

## Next Steps

Once your development environment is running:

1. **Explore the API**:
   - Visit http://localhost:5000/health/
   - Create a webhook path
   - Send test requests

2. **Review the codebase**:
   - Start with `app/__init__.py`
   - Look at the models in `app/models/`
   - Understand the API in `app/api/`

3. **Run the test suite**:
   - Understand the test structure
   - Add tests for new features

4. **Make your first change**:
   - Add a simple feature
   - Follow the TDD workflow
   - Create a pull request

Happy coding! 🚀
