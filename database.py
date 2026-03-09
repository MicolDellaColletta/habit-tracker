import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = "habit_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, name)
        );

        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_on TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, completed_on)
        );
    """)
    conn.commit()
    conn.close()

# --- User functions ---

def create_user(username, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), date.today().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def verify_password(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password"], password):
        return user
    return None

# --- Habit functions ---

def get_all_habits(user_id):
    conn = get_connection()
    habits = conn.execute(
        "SELECT * FROM habits WHERE user_id = ? ORDER BY name",
        (user_id,)
    ).fetchall()
    conn.close()
    return habits

def add_habit(user_id, name):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO habits (user_id, name, created_at) VALUES (?, ?, ?)",
            (user_id, name, date.today().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_habit(habit_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    conn.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
    conn.commit()
    conn.close()

def mark_complete(habit_id):
    conn = get_connection()
    today = date.today().isoformat()
    try:
        conn.execute(
            "INSERT INTO completions (habit_id, completed_on) VALUES (?, ?)",
            (habit_id, today)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def unmark_complete(habit_id):
    conn = get_connection()
    today = date.today().isoformat()
    conn.execute(
        "DELETE FROM completions WHERE habit_id = ? AND completed_on = ?",
        (habit_id, today)
    )
    conn.commit()
    conn.close()

def get_completions(habit_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT completed_on FROM completions WHERE habit_id = ?",
        (habit_id,)
    ).fetchall()
    conn.close()
    return [row["completed_on"] for row in rows]

def calcola_streak(date_list):
    if not date_list:
        return 0
    dates = sorted([date.fromisoformat(d) for d in date_list], reverse=True)
    streak = 0
    giorno = date.today()
    for d in dates:
        if d == giorno:
            streak += 1
            giorno -= timedelta(days=1)
        else:
            break
    return streak

def get_stats(habit_id):
    completions = get_completions(habit_id)
    streak = calcola_streak(completions)
    total = len(completions)
    last_7 = [
        (date.today() - timedelta(days=i)).isoformat()
        for i in range(7)
    ]
    weekly = sum(1 for d in last_7 if d in completions)
    percentage = int((weekly / 7) * 100)
    return {"streak": streak, "total": total, "weekly_percentage": percentage}