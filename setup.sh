#!/bin/bash

# This script provides a full, clean setup for the project.
# USAGE: ./setup.sh

set -e # Exit immediately if a command exits with a non-zero status.

# --- 0. Capture Git SHA (CRITICAL FIX) ---
# We export this so Docker Compose can see it
export GIT_SHA=$(git rev-parse --short HEAD)
echo "🐙 Captured Git SHA: $GIT_SHA"

echo "🚀 Starting the complete project setup..."

# --- 1. Stop and Clean Up Everything (With Confirmation) ---
echo ""
read -p "⚠️  Do you want to stop existing containers and delete volumes (clean start)? [y/N] " -n 1 -r
echo "" # Move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Stopping existing containers and removing old volumes..."
    docker compose down -v
else
    echo "⏩ Skipping cleanup (keeping existing volumes/data)..."
fi

# --- 2. Build and Start All Containers ---
echo "🏗️ Building fresh container images..."
# Docker will automatically pick up the exported GIT_SHA variable here
docker compose build

echo "🚢 Starting all services in the background..."
docker compose up -d

# --- 3. Wait for the Database to be Ready ---
echo "⏳ Waiting for the PostgreSQL database to be ready..."
# We use a loop to check if the DB is actually accepting connections
until docker compose exec db pg_isready -U vijay -d constrisk -q; do
  echo "Database is unavailable - sleeping for 2 seconds..."
  sleep 2
done
echo "✅ Database is ready to accept connections."

# --- 4. Run Migrations (The Architect) ---
echo "🏗️ Running database migrations to create tables..."
docker compose exec api alembic upgrade head
echo "✅ Tables created."

# --- 5. Seed the Database (The Movers) ---
echo "🌱 Running the Python ingestion script to load data..."
docker compose exec api python ml/scripts/ingest_data.py
echo "✅ Database has been seeded with FRED data."

# --- 6. Train Models (The Factory) ---
echo "🧠 Training models and populating Registry..."
docker compose exec api python ml/scripts/train_all_models.py
echo "✅ Models trained and registered."

echo "🎉 All done! Your project environment is running and ready."