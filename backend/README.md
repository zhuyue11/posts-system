# FastAPI Backend

A modern, fast backend service built with FastAPI.

## Project Structure

```
fastapi-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/          # API routes
│   │       ├── __init__.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration settings
│   ├── models/              # Database models
│   │   └── __init__.py
│   └── schemas/             # Pydantic schemas
│       └── __init__.py
├── tests/                   # Test files
├── .env.example             # Environment variables example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### Option 1: Docker (Recommended)

1. Make sure Docker Desktop is installed and running

2. Start the application using docker-compose:
```bash
docker-compose up -d
```

3. The application will be available at http://localhost:8000

4. To stop the application:
```bash
docker-compose down
```

5. To view logs:
```bash
docker-compose logs -f fastapi-app
```

### Option 2: Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update the `.env` file with your configuration.

## Running the Application

### With Docker (using Makefile - Recommended)
```bash
# Start backend and database
make up

# Stop containers
make down

# View logs
make logs

# Restart containers
make restart

# Rebuild after code changes
make rebuild
```

For all available commands, run:
```bash
make help
```

### With Docker (using docker-compose directly)
```bash
docker-compose up -d
```

### Without Docker
Development mode with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Available Endpoints

- `GET /` - Root endpoint
- `GET /api/v1/health` - Health check endpoint

## Running Tests

```bash
pytest
```

## Database Configuration

This application is designed to work with two database types:

### PostgreSQL (Local Development)
- Automatically started with Docker Compose
- Accessible at `localhost:5432`
- Credentials configured in [.env](.env) file
- Data persists in Docker volume `postgres_data`

### Firestore (Google Cloud Production)
- Set `DB_TYPE=firestore` in your environment
- Configure `GCP_PROJECT_ID` for your Google Cloud project
- Recommended for production deployment on Google Cloud

To switch between databases, update the `DB_TYPE` environment variable in your [.env](.env) file.

## Docker Services

When you run `docker-compose up`, two services start:

1. **fastapi-app** (port 8000) - Your FastAPI backend application
2. **postgres** (port 5432) - PostgreSQL database for local development

The FastAPI app waits for PostgreSQL to be healthy before starting.

## Makefile Commands Reference

The project includes a [Makefile](Makefile) with convenient commands:

| Command | Description |
|---------|-------------|
| `make up` | Start backend and database containers |
| `make down` | Stop all containers |
| `make restart` | Restart all containers |
| `make build` | Build Docker images |
| `make rebuild` | Rebuild and restart containers |
| `make logs` | View logs from all containers |
| `make logs-app` | View logs from FastAPI app only |
| `make logs-db` | View logs from PostgreSQL only |
| `make clean` | Stop containers and remove volumes (deletes data) |
| `make test` | Run tests inside container |
| `make shell` | Open shell in FastAPI container |
| `make db-shell` | Open PostgreSQL shell |
| `make help` | Show all available commands |

## Features

- FastAPI framework
- CORS middleware configured
- Environment-based configuration (PostgreSQL/Firestore)
- Modular project structure
- Health check endpoint
- Auto-generated API documentation
- Dockerized with PostgreSQL for local development
- Production-ready for Google Cloud with Firestore
