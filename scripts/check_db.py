"""
Check database connectivity using asyncpg.
Fails fast — no 30-second hang if PostgreSQL is not running.

Usage:
    venv/Scripts/python scripts/check_db.py
"""

import asyncio
import os
import sys

import asyncpg
from dotenv import load_dotenv

load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

# asyncpg uses postgresql://, not postgresql+asyncpg://
url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def check():
    try:
        conn = await asyncpg.connect(url)
        await conn.close()
        print(f"DB OK -- connected to {url.split('@')[-1]}")
    except Exception as e:
        print(f"DB FAILED -- {e}")
        sys.exit(1)


asyncio.run(check())
