import sqlite3
import secrets
from datetime import datetime, timedelta

DATABASE_PATH = "news_app.db"  # Path to your SQLite database file

def create_table():
    """Creates the users and sessions tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            last_activity DATETIME
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def get_user(username):
    """Retrieves a user from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_session_id(session_id, username):
    """Saves the session ID and last activity timestamp for a user."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO sessions (session_id, username, last_activity) VALUES (?, ?, ?)",
                   (session_id, username, datetime.now()))
    conn.commit()
    conn.close()

def get_user_by_session_id(session_id):
    """Retrieves the user associated with a given session ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM sessions WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_last_activity(session_id):
    """Retrieves the last activity timestamp for a given session ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_activity FROM sessions WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_last_activity(session_id):
    """Updates the last activity timestamp for a given session ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET last_activity = ? WHERE session_id = ?", (datetime.now(), session_id))
    conn.commit()
    conn.close()

def remove_session_id(session_id):
    """Removes the session ID from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

# Create tables if they don't exist
create_table()
