import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, name)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id SERIAL PRIMARY KEY,
            habit_id INTEGER NOT NULL REFERENCES habits(id),
            completed_on TEXT NOT NULL,
            UNIQUE(habit_id, completed_on)
        );
    """)
    conn.commit()
    conn.close()

# --- User functions ---

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)",
            (username, generate_password_hash(password), date.today().isoformat())
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
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
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM habits WHERE user_id = %s ORDER BY name",
        (user_id,)
    )
    habits = cursor.fetchall()
    conn.close()
    return habits

def add_habit(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habits (user_id, name, created_at) VALUES (%s, %s, %s)",
            (user_id, name, date.today().isoformat())
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        conn.close()

def delete_habit(habit_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM completions WHERE habit_id = %s", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = %s AND user_id = %s", (habit_id, user_id))
    conn.commit()
    conn.close()

def mark_complete(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    try:
        cursor.execute(
            "INSERT INTO completions (habit_id, completed_on) VALUES (%s, %s)",
            (habit_id, today)
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    finally:
        conn.close()

def unmark_complete(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute(
        "DELETE FROM completions WHERE habit_id = %s AND completed_on = %s",
        (habit_id, today)
    )
    conn.commit()
    conn.close()

def get_completions(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT completed_on FROM completions WHERE habit_id = %s",
        (habit_id,)
    )
    rows = cursor.fetchall()
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