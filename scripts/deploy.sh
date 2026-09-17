#!/usr/bin/env bash
# Runs ON THE SERVER to update the app to the latest commit on main.
# The GitHub Actions deploy workflow calls this over SSH, but you can also
# run it by hand: ssh into the server, cd into the repo, and ./scripts/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Pulling latest code"
git fetch origin main
git reset --hard origin/main

echo "==> Rebuilding and restarting containers"
docker compose up --build -d --remove-orphans

echo "==> Cleaning up old images"
docker image prune -f

echo "==> Waiting for the app to report healthy"
for _ in $(seq 1 20); do
  if docker compose exec -T app python -c \
      "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" 2>/dev/null; then
    echo "==> Deploy complete"
    exit 0
  fi
  sleep 3
done

echo "!! App did not become healthy in time. Recent logs:"
docker compose logs --tail=50 app
exit 1
