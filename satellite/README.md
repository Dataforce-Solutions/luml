Satellite (Docker Compose)

Run the satellite agent and build the sample model image with a single command.

Quickstart

- Copy `.env.example` to `.env` and set `SATELLITE_TOKEN`.
- Optionally adjust `BASE_URL` to the public URL that the platform can reach.
- From this directory, run: `docker compose up -d --build`
- Tail logs: `docker compose logs -f agent`

What this does

- Builds `df-random-svc:latest` from `model_server/` for the agent to deploy.
- Starts the `agent` service (async) which:
  - Connects to `${PLATFORM_URL}` using your `SATELLITE_TOKEN`.
  - Uses the host Docker daemon via `/var/run/docker.sock` to launch deployments.
  - Exposes each deployment on an ephemeral host port and reports
    `${BASE_URL}:<port>` back to the platform.

Notes

- The agent runs as root in the container to access the Docker socket.
- `BASE_URL` defaults to `http://localhost`. If the platform is not local, you
  should set this to a reachable hostname/IP for successful callbacks.

Development

- This module is packaged with `pyproject.toml` and uses `uv` for dependency
  management and fast installs inside the container.
- Linting is configured with Ruff. From this folder you can run:
  - `uvx ruff check agent` (or `uv run ruff check agent`)
  - `uvx ruff format agent` to format
