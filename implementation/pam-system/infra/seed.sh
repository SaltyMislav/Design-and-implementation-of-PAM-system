#!/bin/sh
set -e

docker compose exec backend python /app/infra/seed.py
