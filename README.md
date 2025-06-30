# CallbackListener Backend

A modern Flask-based webhook capture and logging service with PostgreSQL integration that allows you to create unique URLs to capture and inspect HTTP requests in real-time.

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Python 3.11+** (for local development)
- **uv** (Fast Python package manager) - `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hectorleondev/callback-listener.git
   cd callback-listener/backend
   ```

2. **Start with Docker (Recommended):**
   ```bash
   # Start PostgreSQL and backend
   docker compose up -d
   
   # Run migrations
   ./db-manage.sh migrate
   
   # Check status
   ./db-manage.sh status
   ```

3. **Or use Make commands:**
   ```bash
   # Complete development setup
   make setup-dev
   
   # Start development environment
   make dev
   ```

The application will be available at `http://localhost:5001`

### Quick Verification

```bash
# Health check
curl http://localhost:5001/health/

# API documentation
open http://localhost:5001/docs

# Create test webhook
curl -X POST http://localhost:5001/api/paths \
  -H "Content-Type: application/json" \
  -d '{"path_id": "test-webhook"}'
```

## 📋 Features

### Core Functionality
- **🎣 Webhook URL Generation**: Create unique URLs to capture HTTP requests
- **📝 Request Logging**: Store and retrieve detailed request information with PostgreSQL
- **🔄 Multi-method Support**: Capture GET, POST, PUT, DELETE, PATCH, and other HTTP methods
- **⚡ Real-time Capture**: Immediate request logging and retrieval
- **🔌 RESTful API**: Clean API for integration with frontend applications
- **❤️ Health Monitoring**: Built-in health check endpoints
- **🐳 Docker Support**: Complete containerization with PostgreSQL

### Advanced Features
- **🗄️ PostgreSQL Integration**: Robust database with connection pooling
- **📊 Request Analytics**: Dashboard with statistics and metrics
- **🔍 Request Filtering**: Search and filter captured requests
- **📱 Responsive API**: JSON-based API with comprehensive error handling
- **🛡️ Data Validation**: Input validation and sanitization
- **📈 Scalable Architecture**: Modular design for easy extension

## 🏗️ Architecture

### Tech Stack
- **Backend Framework**: Flask 3.0 with Blueprint architecture
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Migrations**: Flask-Migrate (Alembic)
- **Serialization**: Marshmallow for data validation
- **HTTP Client**: Requests for health checks
- **Container**: Docker with multi-stage builds
- **Process Manager**: Gunicorn for production

### Project Structure

```
backend/
├── app/
│   ├── __init__.py         # Application factory
│   ├── config.py           # Configuration classes
│   ├── api/                # API blueprints
│   │   ├── __init__.py
│   │   ├── health.py       # Health check endpoints
│   │   ├── paths.py        # Webhook path management
│   │   └── webhooks.py     # Request capture endpoints
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   ├── path.py         # Path model and schema
│   │   └── request.py      # Request model and schema
│   ├── services/           # Business logic layer
│   │   ├── __init__.py
│   │   ├── path_service.py # Path management logic
│   │   └── request_service.py # Request processing logic
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── database.py     # Database utilities
│       └── validators.py   # Input validation
├── tests/                  # Comprehensive test suite
│   ├── conftest.py         # Test configuration
│   ├── test_models.py      # Model tests
│   ├── test_api.py         # API endpoint tests
│   └── test_services.py    # Service layer tests
├── scripts/                # Management scripts
│   ├── init-db.sql         # Database initialization
│   └── seed_data.py        # Sample data creation
├── migrations/             # Database migrations
│   └── versions/           # Migration files
├── data/                   # Data directory (mounted volume)
├── docker-compose.yml      # Development environment
├── Dockerfile              # Application container
├── Makefile               # Development commands
├── requirements.txt        # Python dependencies
├── requirements.in         # Dependency source
├── gunicorn.conf.py       # Production server config
├── start.sh               # Container startup script
└── README.md              # This file
```

## 🔌 API Reference

### Base URL
- **Development**: `http://localhost:5001`
- **Production**: Your deployed URL

### Authentication
Currently no authentication required. All endpoints are publicly accessible.

### Path Management API

#### Create Webhook Path
```http
POST /api/paths
Content-Type: application/json

{
  "path_id": "my-webhook"  // Optional: auto-generated if not provided
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "path_id": "my-webhook",
    "created_at": "2025-06-14T19:44:40.190938",
    "updated_at": "2025-06-14T19:44:40.190940",
    "request_count": 0
  }
}
```

#### List All Paths
```http
GET /api/paths
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "path_id": "my-webhook",
      "created_at": "2025-06-14T19:44:40.190938",
      "updated_at": "2025-06-14T19:44:40.190940",
      "request_count": 5
    }
  ]
}
```

#### Get Path Details
```http
GET /api/paths/{path_id}
```

#### Delete Path
```http
DELETE /api/paths/{path_id}
```

### Request Capture API

#### Capture Any HTTP Request
```http
[ANY_METHOD] /webhook/{path_id}
```

All request details are automatically captured:
- Method (GET, POST, PUT, DELETE, etc.)
- Headers
- Query parameters
- Request body
- Client IP address
- User agent
- Timestamp

**Response (200):**
```json
{
  "success": true,
  "message": "Request captured successfully",
  "data": {
    "request_id": "789e1234-e89b-12d3-a456-426614174000",
    "timestamp": "2025-06-14T19:44:43.776984",
    "method": "POST"
  }
}
```

### Request Retrieval API

#### Get Captured Requests
```http
GET /api/paths/{path_id}/logs?limit=50&offset=0&include_body=true
```

**Query Parameters:**
- `limit` (optional): Number of requests to return (default: 50, max: 1000)
- `offset` (optional): Number of requests to skip (default: 0)
- `include_body` (optional): Include request body in response (default: true)
- `method` (optional): Filter by HTTP method
- `since` (optional): ISO datetime filter for requests after timestamp

**Response (200):**
```json
{
  "success": true,
  "data": {
    "path": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "path_id": "my-webhook",
      "request_count": 1
    },
    "requests": [
      {
        "id": "456e7890-e89b-12d3-a456-426614174000",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "User-Agent": "curl/8.7.1",
          "Accept": "*/*"
        },
        "body": "{\"message\": \"Hello World!\"}",
        "query_params": {"test": "value"},
        "ip_address": "192.168.65.1",
        "user_agent": "curl/8.7.1",
        "timestamp": "2025-06-14T19:44:43.776984"
      }
    ],
    "pagination": {
      "limit": 50,
      "offset": 0,
      "total": 1,
      "has_more": false
    }
  }
}
```

#### Get Specific Request
```http
GET /api/paths/{path_id}/logs/{request_id}
```

### Dashboard API

#### Get Statistics
```http
GET /api/dashboard/stats
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_webhooks": 3,
    "total_requests": 15,
    "active_webhooks": 3,
    "recent_requests": [
      {
        "id": "789e1234-e89b-12d3-a456-426614174000",
        "method": "POST",
        "path_id": "my-webhook",
        "timestamp": "2025-06-14T19:44:43.776984",
        "ip_address": "192.168.65.1"
      }
    ]
  }
}
```

### Health Check API

#### Basic Health Check
```http
GET /health/
```

**Response (200):**
```json
{
  "service": "callback-listener-backend",
  "status": "healthy"
}
```

#### Readiness Check
```http
GET /health/ready
```

Includes database connectivity check.

#### Liveness Check
```http
GET /health/live
```

### Error Handling

All endpoints return consistent error responses:

**Validation Error (400):**
```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "path_id": ["Path ID already exists"]
  }
}
```

**Not Found (404):**
```json
{
  "success": false,
  "error": "Path not found"
}
```

**Internal Server Error (500):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

## 🗄️ Database

### PostgreSQL Integration

The application uses PostgreSQL 15 with the following configuration:

- **Connection Pooling**: 10 connections, 20 overflow
- **Health Checks**: Automatic connection validation
- **Migrations**: Managed with Flask-Migrate/Alembic
- **Transactions**: ACID compliance for data integrity

### Database Schema

#### Paths Table
```sql
CREATE TABLE paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Requests Table
```sql
CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path_id UUID REFERENCES paths(id) ON DELETE CASCADE,
    method VARCHAR(10) NOT NULL,
    headers JSONB,
    body TEXT,
    query_params JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Management

#### Using db-manage.sh Script
```bash
# Check database status
./db-manage.sh status

# Run migrations
./db-manage.sh migrate

# Connect to database
./db-manage.sh connect

# Create backup
./db-manage.sh backup

# Restore from backup
./db-manage.sh restore backup_20250614_194430.sql

# Reset database (WARNING: Deletes all data)
./db-manage.sh reset

# View logs
./db-manage.sh logs
```

#### Using Make Commands
```bash
# Database operations
make migrate              # Run migrations
make migrate-create msg="Add new table"  # Create migration
make db-reset            # Reset database
make db-backup file=backup.sql  # Create backup
make db-restore file=backup.sql # Restore backup
make db-shell            # Connect to database
make db-status           # Check status
```

#### Manual Database Operations
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U callback_user callback_listener

# Run migrations manually
docker compose exec backend flask db upgrade

# Create new migration
docker compose exec backend flask db migrate -m "Description"
```

## 🧪 Testing

### Test Suite

The application includes comprehensive tests:

- **Unit Tests**: Model validation and business logic
- **Integration Tests**: API endpoints and database operations  
- **Service Tests**: Business logic and data processing
- **Health Check Tests**: Monitoring endpoint validation

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests locally (requires local database)
make test-local

# Specific test categories
make test-unit      # Model and utility tests
make test-api       # API endpoint tests
make test-services  # Business logic tests

# Generate coverage report
make test-coverage
```

### Test Configuration

Tests use a separate test database and configuration:

```bash
# Test environment variables
export FLASK_ENV=testing
export TEST_DATABASE_URL=postgresql://callback_user:callback_pass@localhost:5432/callback_listener_test
```

### Test Examples

```python
# Test webhook creation
def test_create_webhook_path(client):
    response = client.post('/api/paths', 
                          json={'path_id': 'test-webhook'})
    assert response.status_code == 201
    assert response.json['success'] is True

# Test request capture
def test_capture_request(client, sample_path):
    response = client.post(f'/webhook/{sample_path.path_id}',
                          json={'test': 'data'})
    assert response.status_code == 200
    assert 'request_id' in response.json['data']
```

## 🛠️ Development

### Local Development Setup

```bash
# 1. Set up virtual environment (optional)
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 2. Install dependencies
make install
# or manually: uv pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 4. Start PostgreSQL
docker compose up -d postgres

# 5. Run migrations
make migrate

# 6. Start development server
make run
# or manually: python run.py
```

### Code Quality Tools

```bash
# Format code (Black + isort)
make format

# Run linting (flake8)
make lint

# Type checking (if using mypy)
make type-check

# Security scanning
make security-check

# Complete quality check
make quick-test  # format + lint + test
```

### Dependency Management

The project uses `uv` for fast dependency management:

```bash
# Add new dependency
uv pip install package-name
echo "package-name" >> requirements.in

# Update dependencies
make update-deps

# Sync dependencies
make sync-deps

# Add development dependency
uv pip install --dev pytest-mock
```

### Git Hooks

Pre-commit hooks ensure code quality:

```bash
# Install hooks
make install-hooks

# Run hooks manually
make run-hooks

# Skip hooks (not recommended)
git commit --no-verify
```

## 🐳 Docker

### Development Environment

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild images
docker compose up --build

# Reset with clean volumes
docker compose down -v
```

### Production Deployment

```bash
# Build production image
docker build -t callback-listener-backend .

# Run with production settings
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://user:pass@db:5432/callback_listener \
  callback-listener-backend
```

### Container Health Checks

The container includes health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health/', timeout=5)"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Application environment | `development` | No |
| `FLASK_DEBUG` | Enable debug mode | `false` | No |
| `FLASK_HOST` | Server host | `0.0.0.0` | No |
| `FLASK_PORT` | Server port | `5000` | No |
| `DATABASE_URL` | PostgreSQL connection string | See config.py | Yes |
| `SECRET_KEY` | Flask secret key | Auto-generated | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `POSTGRES_DB` | Database name | `callback_listener` | No |
| `POSTGRES_USER` | Database user | `callback_user` | No |
| `POSTGRES_PASSWORD` | Database password | `callback_pass` | No |

### Configuration Classes

```python
# Development
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://callback_user:callback_pass@localhost:5432/callback_listener_dev"

# Testing  
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://callback_user:callback_pass@localhost:5432/callback_listener_test"

# Production
class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
```

### SSL/TLS Configuration

For production, configure SSL:

```python
# In production configuration
SSL_DISABLE = False
PREFERRED_URL_SCHEME = 'https'
```

## 📊 Monitoring & Logging

### Health Monitoring

Monitor application health with built-in endpoints:

```bash
# Basic health
curl http://localhost:5001/health/

# Readiness (includes DB check)
curl http://localhost:5001/health/ready

# Liveness
curl http://localhost:5001/health/live
```

### Logging Configuration

Structured logging with different levels:

```python
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### Metrics Collection

Monitor key metrics:

- **Request Rate**: Webhooks captured per minute
- **Response Time**: API endpoint performance
- **Database Performance**: Query execution time
- **Error Rate**: Failed requests percentage
- **Memory Usage**: Application memory consumption

### Production Monitoring

For production deployments, integrate with:

- **APM Tools**: New Relic, Datadog, or Sentry
- **Logging**: ELK Stack or Fluentd
- **Metrics**: Prometheus + Grafana
- **Alerts**: PagerDuty or similar

## 🚀 Deployment

### Production Checklist

```bash
# 1. Run pre-deployment checks
make deploy-check

# 2. Update environment variables
cp .env.example .env.production
# Edit .env.production with production values

# 3. Build and test
make build
make test

# 4. Security check
make security-check

# 5. Database backup
./db-manage.sh backup

# 6. Deploy
docker compose -f docker-compose.prod.yml up -d
```

### Environment Setup

1. **Database Configuration**:
   ```bash
   # Set production database URL
   export DATABASE_URL=postgresql://user:password@host:5432/callback_listener
   ```

2. **Security Configuration**:
   ```bash
   # Generate secure secret key
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   ```

3. **Server Configuration**:
   ```bash
   # Production server settings
   export FLASK_ENV=production
   export FLASK_DEBUG=false
   export LOG_LEVEL=WARNING
   ```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Compose Production

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: callback_listener
      POSTGRES_USER: callback_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    image: callback-listener-backend:latest
    environment:
      FLASK_ENV: production
      DATABASE_URL: postgresql://callback_user:${POSTGRES_PASSWORD}@postgres:5432/callback_listener
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
    restart: unless-stopped
```

## 🔐 Security

### Security Considerations

1. **Environment Variables**: Never commit secrets to git
2. **Database Security**: Use strong passwords and restrict access
3. **Input Validation**: All inputs are validated and sanitized
4. **SQL Injection**: Use parameterized queries (SQLAlchemy ORM)
5. **CORS**: Configure CORS appropriately for your frontend domain

### Security Headers

```python
# Add security headers
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### Rate Limiting

Consider implementing rate limiting for production:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/webhook/<path_id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("100 per minute")
def capture_request(path_id):
    # Implementation
```

## 📚 API Documentation

### OpenAPI/Swagger Documentation

Access interactive API documentation:

- **Development**: http://localhost:5001/docs
- **ReDoc**: http://localhost:5001/redoc (alternative format)

### API Versioning

Future API versions will be supported:

```http
# Version 1 (current)
GET /api/paths

# Future version 2
GET /api/v2/paths
```

### SDK Generation

Generate client SDKs from OpenAPI specification:

```bash
# Generate Python client
openapi-generator generate -i http://localhost:5001/openapi.yaml -g python -o client-python

# Generate JavaScript client  
openapi-generator generate -i http://localhost:5001/openapi.yaml -g javascript -o client-js
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Make changes with tests**
4. **Run quality checks**: `make quick-test`
5. **Update documentation**
6. **Commit changes**: Use conventional commit format
7. **Submit pull request**

### Code Standards

- **Python Style**: Follow PEP 8 (enforced by Black)
- **Type Hints**: Use type annotations where helpful
- **Documentation**: Update docstrings and README
- **Tests**: Maintain >85% test coverage
- **Commits**: Use conventional commit messages

### Commit Message Format

```
type(scope): description

feat(api): add request filtering endpoint
fix(db): resolve connection pool exhaustion
docs(readme): update API documentation
test(webhooks): add webhook creation tests
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature  
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL status
./db-manage.sh status

# Restart PostgreSQL
docker compose restart postgres

# Reset database
./db-manage.sh reset

# Check connection string
echo $DATABASE_URL
```

#### Port Conflicts

```bash
# Check what's using port 5001
lsof -i :5001

# Kill process using port
kill -9 $(lsof -t -i:5001)

# Use different port
export FLASK_PORT=5002
```

#### Migration Issues

```bash
# Check migration status
docker compose exec backend flask db current

# Reset migrations
rm -rf migrations/
docker compose exec backend flask db init
docker compose exec backend flask db migrate -m "Initial migration"
docker compose exec backend flask db upgrade
```

#### Performance Issues

```bash
# Check resource usage
docker stats

# Check database connections
docker compose exec postgres psql -U callback_user callback_listener \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
docker compose exec postgres psql -U callback_user callback_listener \
  -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Debug Mode

```bash
# Enable verbose logging
export FLASK_DEBUG=true
export LOG_LEVEL=DEBUG

# Start with debug output
make dev

# Or run directly
python run.py
```

### Getting Help

1. **Check Documentation**: This README and other docs
2. **Search Issues**: Look for similar problems
3. **Create Issue**: Use issue template with details
4. **Contact**: [Create an issue](https://github.com/hectorleondev/callback-listener/issues)

## 📞 Support

For support and questions:

- **GitHub Issues**: [Create an issue](https://github.com/hectorleondev/callback-listener/issues)
- **Documentation**: Check this README and project docs
- **Community**: Join discussions in GitHub Discussions

## 🎯 Roadmap

### Current Version (v1.0)
- ✅ PostgreSQL integration
- ✅ Request capture and logging
- ✅ RESTful API
- ✅ Docker support
- ✅ Health monitoring

### Planned Features (v1.1)
- [ ] Real-time WebSocket updates
- [ ] Request search and filtering
- [ ] Export functionality (JSON, CSV)
- [ ] Request replay capabilities
- [ ] Custom response configuration

### Future Features (v2.0)
- [ ] API authentication and authorization
- [ ] Rate limiting and security features
- [ ] Multi-tenant support
- [ ] Webhook transformation rules
- [ ] Advanced analytics and reporting
- [ ] Enterprise features

---

**CallbackListener Backend** - Built with ❤️ using Flask, PostgreSQL, and Docker.

For frontend documentation, see [../frontend/README.md](../frontend/README.md)
