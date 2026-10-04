import sqlite3
import json
from pathlib import Path

DB_PATH = Path("gym.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS gym_sessions (
        id TEXT PRIMARY KEY,
        date TEXT,
        mode TEXT,
        score INTEGER,
        total INTEGER,
        xp_earned INTEGER,
        duration_sec INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS gym_results (
        id TEXT PRIMARY KEY,
        session_id TEXT,
        exercise_id TEXT,
        type TEXT,
        topic TEXT,
        difficulty TEXT,
        correct BOOLEAN,
        hints_used INTEGER,
        attempts INTEGER,
        time_sec INTEGER,
        answer_text TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS gym_progress (
        id TEXT PRIMARY KEY,
        xp_total INTEGER,
        level INTEGER,
        streak_days INTEGER,
        last_active_date TEXT,
        rest_day_used_week BOOLEAN
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS gym_badges (
        badge_id TEXT PRIMARY KEY,
        earned_date TEXT
    )""")
    conn.commit()
    conn.close()


if not DB_PATH.exists():
    init_db()
