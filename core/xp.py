import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("gym.db")
from core.gym import init_db
if not DB_PATH.exists():
    init_db()

LEVELS = [
    (0, "Seedling"), (100, "Sprout"), (300, "Rooted"), 
    (600, "Steady"), (1000, "Branching"), (1500, "Grounded"), 
    (2100, "Deep Rooted"), (2800, "Canopy"), (3600, "Grove"), (4500, "Old Growth")
]

def get_level(xp):
    for i in range(len(LEVELS)-1, -1, -1):
        if xp >= LEVELS[i][0]:
            next_xp = LEVELS[i+1][0] if i + 1 < len(LEVELS) else LEVELS[i][0]
            return i + 1, LEVELS[i][1], next_xp
    return 1, LEVELS[0][1], LEVELS[1][0]

def save_workout(session_id, date_str, mode, score, total, xp_earned, results):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO gym_sessions VALUES (?, ?, ?, ?, ?, ?, 0)",
              (session_id, date_str, mode, score, total, xp_earned))
              
    for r in results:
        c.execute("INSERT INTO gym_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
                  (r['id'], session_id, r['exercise_id'], r['type'], r['topic'], 
                   r['difficulty'], r['correct'], r['hints_used'], r['attempts'], r['answer']))
    
    # Update progress
    c.execute("SELECT xp_total, last_active_date, streak_days FROM gym_progress WHERE id='user'")
    row = c.fetchone()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    if not row:
        c.execute("INSERT INTO gym_progress VALUES ('user', ?, 1, 1, ?, 0)", (xp_earned, today))
    else:
        xp_total, last_date, streak = row
        new_xp = xp_total + xp_earned
        if last_date != today:
            # Simple streak logic: if yesterday, increment. If older, reset to 1 (ignoring rest day complex logic for brevity in this iteration)
            last = datetime.datetime.strptime(last_date, '%Y-%m-%d')
            curr = datetime.datetime.strptime(today, '%Y-%m-%d')
            if (curr - last).days <= 2: # Gives 1 rest day effectively
                streak += 1
            else:
                streak = 1
        c.execute("UPDATE gym_progress SET xp_total=?, streak_days=?, last_active_date=? WHERE id='user'",
                  (new_xp, streak, today))
    
    conn.commit()
    conn.close()

def get_progress():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT xp_total, streak_days FROM gym_progress WHERE id='user'")
    row = c.fetchone()
    conn.close()
    if not row:
        return 0, 0, 1, "Seedling", 100
    xp, streak = row
    lvl_num, lvl_name, next_xp = get_level(xp)
    return xp, streak, lvl_num, lvl_name, next_xp

def get_topic_mastery():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT topic, correct FROM gym_results ORDER BY rowid DESC LIMIT 200")
    rows = c.fetchall()
    conn.close()
    
    topics = {}
    for t, c_val in rows:
        if t not in topics:
            topics[t] = []
        if len(topics[t]) < 10:
            topics[t].append(c_val)
            
    mastery = {}
    for t, history in topics.items():
        mastery[t] = int((sum(history) / len(history)) * 100)
    return mastery
