# taskapi — End-to-End DevOps Deployment Pipeline

A small Flask task-tracking API used as the vehicle to build and demonstrate a complete, real-world DevOps workflow — from a bare Linux server through full CI/CD automation.

**Live pipeline:** every push to `main` automatically tests, builds, containerizes, publishes, and deploys this app to a real AWS server with zero manual steps.

## What this project demonstrates

- **Linux & systemd** — gunicorn managed as a systemd service, nginx as a reverse proxy
- **Containerization** — Dockerfile with layer caching, .dockerignore, Docker Compose
- **AWS** — EC2, security groups, IAM users/roles, Elastic IPs
- **Infrastructure as Code** — Terraform-provisioned EC2 with automated app deployment via user_data
- **Remote state** — Terraform state in S3 with DynamoDB locking
- **CI/CD** — GitHub Actions: test, build, smoke test, publish, deploy
- **Testing** — pytest suite gating deployment

## Repositories

- taskapi — application code, Dockerfile, tests, CI/CD workflow
- terraform-taskapi — infrastructure as code, with a terraform plan workflow on pull requests

## API Endpoints

- GET /health — health check
- GET /tasks — list tasks
- POST /tasks — create a task
- DELETE /tasks/<id> — delete a task

## CI/CD Pipeline

Every push to main: runs tests, builds a Docker image, smoke-tests the container, pushes to Docker Hub, then deploys automatically to EC2 via SSH. A failing test halts the pipeline before any build, publish, or deploy step runs — verified by deliberately breaking and then fixing a test.

## Infrastructure as Code

The EC2 instance, security group, and full app setup are defined in Terraform, with state stored remotely in S3 with DynamoDB locking. The entire stack was destroyed and recreated from code alone to confirm full reproducibility.

## Tech stack

Python (Flask), Docker, nginx, AWS (EC2, IAM, S3, DynamoDB), Terraform, GitHub Actions, pytest
