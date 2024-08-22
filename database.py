import sqlite3

def create_user_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            full_name TEXT,
            country TEXT,
            email TEXT UNIQUE,
            password TEXT,
            api_keys TEXT,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def create_admin_table():
    conn = sqlite3.connect('admins.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_table():
    create_user_table()
    create_admin_table()

def save_api_key(username, api_keys):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET api_keys=? WHERE username=?', (api_keys, username))
    conn.commit()
    conn.close()

def load_api_keys(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT api_keys FROM users WHERE username=?', (username,))
    api_keys = cursor.fetchone()
    conn.close()
    return api_keys[0].split(",") if api_keys and api_keys[0] else []
