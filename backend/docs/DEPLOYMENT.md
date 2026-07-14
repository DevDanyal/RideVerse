# RideVerse Backend Deployment Guide

## Prerequisites

- Python 3.13+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)
- Node.js 20+ (for frontend, if co-deployed)

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/rideverse.git
cd rideverse/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your local configuration

# Run database migrations
alembic upgrade head

# Seed the database
python -m scripts.seed

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Setup

```bash
# Build and start all services
docker compose up --build -d

# Run migrations inside the container
docker compose exec backend alembic upgrade head

# Seed the database
docker compose exec backend python -m scripts.seed

# View logs
docker compose logs -f backend

# Stop all services
docker compose down
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://rideverse:rideverse@localhost:5432/rideverse` | PostgreSQL async connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | `change-me-in-production` | Application secret key |
| `JWT_SECRET_KEY` | `change-me-jwt-secret-in-production` | JWT signing key |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `ENVIRONMENT` | `development` | Runtime environment (`development`, `staging`, `production`) |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Comma-separated allowed origins |
| `API_V1_PREFIX` | `/api/v1` | API version prefix |

## Database Migrations

```bash
# Generate a migration after model changes
alembic revision --autogenerate -m "description"

# Apply pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration version
alembic current

# View migration history
alembic history

# Using the helper script
./scripts/migrate.sh "add user preferences table"
```

## Celery Workers

```bash
# Start a worker
celery -A app.workers.celery_app worker -l info

# Start with concurrency
celery -A app.workers.celery_app worker -l info --concurrency=4

# Start the beat scheduler
celery -A app.workers.celery_app beat -l info

# Monitor tasks
celery -A app.workers.celery_app flower
```

## Common Issues

### Database connection refused
Ensure PostgreSQL is running and the `DATABASE_URL` is correct.
```bash
pg_isready -h localhost -p 5432
```

### Redis connection refused
Ensure Redis is running.
```bash
redis-cli ping
```

### Migration conflicts
```bash
alembic merge heads
alembic upgrade head
```

### Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows
```

### Docker build fails
```bash
# Clean build
docker compose down --rmi all
docker compose up --build --no-cache
```
