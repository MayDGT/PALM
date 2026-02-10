#!/usr/bin/env bash
set -e

echo "=== PALM Docker Environment ==="
echo "Python:" $(python --version)
echo "Working directory:" $(pwd)

# sanity check
if ! docker ps >/dev/null 2>&1; then
  echo "[ERROR] Docker socket not mounted!"
  echo "Please run with: -v /var/run/docker.sock:/var/run/docker.sock"
  exit 1
fi

echo "Docker available ✔"

exec python main.py
