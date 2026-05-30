#!/bin/bash
# Run this from your local machine to seed Railway database
# Usage: bash seed_railway.sh "postgresql://user:pass@host:port/db"

if [ -z "$1" ]; then
  echo "Usage: bash seed_railway.sh \"YOUR_RAILWAY_DATABASE_URL\""
  echo ""
  echo "Get your URL from:"
  echo "  Railway dashboard → PostgreSQL service → Connect tab → Postgres Connection URL"
  exit 1
fi

export DATABASE_URL="$1"
pip install sqlalchemy asyncpg aiosqlite -q
python3 seed.py
