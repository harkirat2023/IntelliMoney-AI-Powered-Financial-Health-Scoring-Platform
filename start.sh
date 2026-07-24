#!/usr/bin/env bash
set -euo pipefail

echo "=== IntelliMoney Startup ==="

# Copy .env if missing
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env from .env.example — edit it with your keys."
fi

# Start services
echo "Starting MongoDB, Redis (optional), Backend, Frontend..."
docker compose up --build -d

echo ""
echo "Frontend:  http://localhost:3002"
echo "Backend:   http://localhost:8080/api/v1"
echo "Health:    http://localhost:8080/healthz"
echo ""
echo "To seed demo data:  docker compose --profile with-seed run seed"
echo "To stop:            docker compose down"
