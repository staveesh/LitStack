#!/usr/bin/env bash
set -euo pipefail

# Check Docker
if ! command -v docker &>/dev/null; then
  echo "Error: Docker is not installed."
  echo "Install it at: https://docs.docker.com/get-docker/"
  exit 1
fi

if ! docker info &>/dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Start Docker and try again."
  exit 1
fi

# Bootstrap .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "  Created .env from .env.example."
  echo "  Open .env and fill in at least one AI provider key (ANTHROPIC_API_KEY or OPENAI_API_KEY)."
  echo "  Then re-run: ./start.sh"
  echo ""
  exit 0
fi

echo "Starting LitStack…"
docker compose up --build -d

echo ""
echo "  LitStack is running at http://localhost:3000"
echo ""
echo "  Logs:  docker compose logs -f"
echo "  Stop:  docker compose down"
