# taskapi — End-to-End DevOps Deployment Pipeline

A small Flask task-tracking API used as the vehicle to build and demonstrate a complete, real-world DevOps workflow — from a bare Linux server through full CI/CD automation.

**Live pipeline:** every push to `main` automatically tests, builds, containerizes, publishes, and deploys this app to a real AWS server with zero manual steps.

---

## What this project demonstrates

| Area | What was built |
|---|---|
| **Linux & systemd** | Manual deployment on a bare server: gunicorn managed as a systemd service, nginx as a reverse proxy |
| **Containerization** | Multi-stage-aware Dockerfile, image layer caching, `.dockerignore`, Docker Compose |
| **Cloud infrastructure (AWS)** | EC2, security groups, IAM users/roles, Elastic IPs, cost-safety practices |
| **Infrastructure as Code** | Full environment provisioned via Terraform — instance, networking, and app deployment via `user_data` |
| **Remote state management** | Terraform state stored in S3 with DynamoDB locking |
| **CI/CD** | GitHub Actions pipeline: test → build → smoke test → publish → deploy, fully automated |
| **Testing** | pytest suite covering core API behavior, enforced as a gate before any deployment |

---

## Architecture

```
 Developer
     │  git push
     ▼
 GitHub Actions (CI/CD)
     │
     ├─ 1. Run pytest suite
     ├─ 2. Build Docker image
     ├─ 3. Smoke-test the container
     ├─ 4. Push image → Docker Hub
     └─ 5. SSH deploy → EC2 instance
                │
                ▼
        ┌───────────────────┐
        │   AWS EC2 (Ubuntu) │
        │  ┌───────────────┐ │
        │  │     nginx      │ │  :80 → reverse proxy
        │  └───────┬───────┘ │
        │  ┌───────▼───────┐ │
        │  │ Docker container│ │  :8000
        │  │ gunicorn + Flask│ │
        │  └───────────────┘ │
        └───────────────────┘
```

Infrastructure (the EC2 instance, security group, and networking) is provisioned entirely by **Terraform**, with remote state in S3 and a `user_data` script that installs Docker, clones this repo, and starts the app automatically on first boot — meaning the entire server can be destroyed and recreated from code alone.

---

## Repositories

- **[taskapi](https://github.com/cyber-mya/taskapi)** — application code, Dockerfile, tests, and the CI/CD workflow
- **[terraform-taskapi](https://github.com/cyber-mya/terraform-taskapi)** — infrastructure as code, with a separate `terraform plan` workflow that runs automatically on every pull request

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task (`{"title": "..."}`) |
| DELETE | `/tasks/<id>` | Delete a task |

---

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Run tests:
```bash
python -m pytest test_app.py -v
```

Run in Docker:
```bash
docker build -t taskapi:latest .
docker run -d -p 8000:8000 taskapi:latest
```

---

## CI/CD Pipeline

Defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml). On every push to `main`:

1. **Test** — installs dependencies, runs the pytest suite. A failing test stops the pipeline here — nothing downstream runs.
2. **Build** — builds the Docker image from the `Dockerfile`.
3. **Smoke test** — actually runs the built container and hits `/health` for a real response, catching runtime issues a successful build alone wouldn't reveal.
4. **Publish** — pushes the image to Docker Hub, authenticated via GitHub encrypted secrets (no credentials in code).
5. **Deploy** — SSHs into the live EC2 instance, pulls the new image, and replaces the running container.

Verified end to end: a deliberately broken test was pushed and confirmed to halt the pipeline before the build, publish, or deploy steps ever ran — proving the safety net works, not just the happy path.

---

## Infrastructure as Code

Defined in the [`terraform-taskapi`](https://github.com/cyber-mya/terraform-taskapi) repo:

- `main.tf` — EC2 instance, security group, and AMI lookup
- `variables.tf` / `outputs.tf` — parameterized configuration and automatic IP output
- `backend.tf` — remote state in S3 with DynamoDB locking
- `setup.sh` — first-boot automation (Docker install, app clone, build, run, nginx config) via `user_data`
- `.github/workflows/terraform-plan.yml` — runs `terraform plan` automatically on every pull request, so infrastructure changes are visible before merge

Full reproducibility was verified by destroying and recreating the entire stack from code alone, with the server coming back fully configured and serving traffic with no manual intervention.

---

## Notable failure scenarios diagnosed

Part of this project's focus was building real debugging instinct, not just following happy-path tutorials. Failure modes deliberately triggered and diagnosed include:

- **502 Bad Gateway** vs **connection refused** vs **request timeout** — three distinct failure signatures traced to three different layers (backend down, proxy down, network/firewall block)
- **Infrastructure drift** — a manual AWS Console change was detected and reconciled via `terraform plan`/`apply`
- **CI pipeline safety net** — confirmed a failing test blocks deployment before it can reach production

---

## Tech stack

Python (Flask) · Docker · nginx · AWS (EC2, IAM, S3, DynamoDB) · Terraform · GitHub Actions · pytest
