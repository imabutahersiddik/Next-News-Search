import sqlite3
import hashlib

# Function to create a database and tables
def create_table():
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    # Create table for storing users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT,
            country TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'free'
        )
    ''')
    
    # Create table for storing API keys
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            key TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create table for storing user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            language TEXT,
            sources TEXT,
            output_format TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create table for storing searches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            keyword TEXT,
            api_key TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to register a user
def register_user(username, full_name, country, email, password):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, full_name, country, email, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, full_name, country, email, hash_password(password)))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username or email already exists.")
    finally:
        conn.close()

# Function to login a user
def login_user(username, password):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return True
    return False

# Function to save API key
def save_api_key(username, api_key):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        cursor.execute('DELETE FROM api_keys WHERE user_id = ?', (user_id[0],))  # Clear existing API keys
        cursor.execute('INSERT INTO api_keys (user_id, key) VALUES (?, ?)', (user_id[0], api_key))
        conn.commit()
    conn.close()

# Function to load API keys for a user
def load_api_keys(username):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        cursor.execute('SELECT key FROM api_keys WHERE user_id = ?', (user_id[0],))
        results = cursor.fetchall()
        return [row[0] for row in results]
    
    conn.close()
    return []

# Function to load a single API key for a user (if needed)
def load_api_key(username):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        cursor.execute('SELECT key FROM api_keys WHERE user_id = ?', (user_id[0],))
        result = cursor.fetchone()
        return result[0] if result else None
    
    conn.close()
    return None

# Function to save user preferences
def save_user_preferences(username, preferences):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, language, sources, output_format)
            VALUES (?, ?, ?, ?)
        ''', (user_id[0], preferences['language'], ','.join(preferences['sources']), preferences['output_format']))
        conn.commit()
    
    conn.close()

# Function to load user preferences
def load_user_preferences(username):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()
    
    if user_id:
        cursor.execute('SELECT language, sources, output_format FROM user_preferences WHERE user_id = ?', (user_id[0],))
        result = cursor.fetchone()
        
        if result:
            return {
                'language': result[0],
                'sources': result[1].split(',') if result[1] else [],
                'output_format': result[2]
            }
    
    return {
        'language': None,
        'sources': [],
        'output_format': None
    }

# Function to save search details
def save_search(user_id, keyword, api_key):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO searches (user_id, keyword, api_key)
        VALUES (?, ?, ?)
    ''', (user_id, keyword, api_key))
    conn.commit()
    conn.close()
