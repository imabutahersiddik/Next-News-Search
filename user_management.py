import sqlite3

def register_user(username, full_name, country, email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, full_name, country, email, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, full_name, country, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user  # Returns user details if login is successful

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
