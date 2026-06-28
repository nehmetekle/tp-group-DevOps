# DevOps Task API

Small FastAPI REST API used for a DevOps CI/CD pipeline project.

## Features

- REST API for managing tasks
- Health endpoint at `/health`
- Prometheus metrics endpoint at `/metrics`
- Unit tests with coverage
- Docker image and Compose setup with healthcheck

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The API Locally

```bash
uvicorn app.main:app --reload
```

Useful URLs:

- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Metrics: `http://localhost:8000/metrics`

## Run Tests

```bash
pytest --cov=app --cov-report=xml
```

## Lint

```bash
flake8 app tests
```

## Run With Docker Compose

```bash
docker network create cicd-network
docker compose up --build -d
curl http://localhost:8000/health
curl http://localhost:8000/metrics
docker compose down
```

If `cicd-network` already exists, Docker will show a message and you can continue.
If port `8000` is already used, run Compose with another host port:

```bash
APP_PORT=8001 docker compose up --build -d
curl http://localhost:8001/health
docker compose down
```

## CI/CD Pipeline

The complete project pipeline will cover:

1. Checkout
2. Lint
3. Build and test
4. SonarQube analysis
5. Quality Gate
6. Trivy security scan
7. Push Docker image to registry
8. Terraform apply
9. Smoke test on `/health`
