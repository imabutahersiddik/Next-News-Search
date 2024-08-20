import sqlite3

def get_db_connection():
    conn = sqlite3.connect('api_keys.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_api_key(api_key):
    conn = get_db_connection()
    conn.execute('DELETE FROM api_keys')  # Clear existing key
    conn.execute('INSERT INTO api_keys (key) VALUES (?)', (api_key,))
    conn.commit()
    conn.close()

def load_api_key():
    conn = get_db_connection()
    key = conn.execute('SELECT key FROM api_keys').fetchone()
    conn.close()
    return key['key'] if key else None
