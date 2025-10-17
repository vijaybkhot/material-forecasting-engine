#!/bin/bash

# This script provides a full, clean setup for the project.
#
# USAGE:
# 1. Make this script executable (only need to do this once):
#    chmod +x setup.sh
#
# 2. Run the script from your project root:
#    ./setup.sh
# This will set up the entire environment from scratch.
# It stops old containers, removes volumes, builds fresh images,
# starts the services, and seeds the database with initial data.

set -e # Exit immediately if a command exits with a non-zero status.

echo "🚀 Starting the complete project setup..."

# --- 1. Stop and Clean Up Everything ---
echo "🧹 Stopping existing containers and removing old volumes..."
docker compose down -v

# --- 2. Build and Start All Containers ---
echo "🏗️ Building fresh container images..."
docker compose build

echo "🚢 Starting all services in the background..."
docker compose up -d

# --- 3. Wait for the Database to be Ready ---
echo "⏳ Waiting for the PostgreSQL database to be ready..."
until docker compose exec db pg_isready -U vijay -d constrisk -q; do
  echo "Database is unavailable - sleeping for 2 seconds..."
  sleep 2
done
echo "✅ Database is ready to accept connections."

# --- 4. Seed the Database ---
echo "🌱 Running the Python ingestion script to create tables and load data..."
python ml/scripts/ingest_data.py
echo "✅ Database has been seeded."

echo "🎉 All done! Your project environment is running and ready."