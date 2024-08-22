import sqlite3

# Function to create a database and tables
def create_table():
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    # Create table for storing API key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_key (
            id INTEGER PRIMARY KEY,
            key TEXT NOT NULL
        )
    ''')
    
    # Create table for storing user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY,
            language TEXT,
            sources TEXT,
            output_format TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to save API key
def save_api_key(api_key):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM api_key')  # Clear existing API key
        cursor.execute('INSERT INTO api_key (key) VALUES (?)', (api_key,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while saving the API key: {e}")
    finally:
        conn.close()

# Function to load API key
def load_api_key():
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT key FROM api_key')
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"An error occurred while loading the API key: {e}")
        return None
    finally:
        conn.close()

# Function to save user preferences
def save_user_preferences(preferences):
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    try:
        # Check if there are any existing preferences
        cursor.execute('SELECT COUNT(*) FROM user_preferences')
        existing_preferences = cursor.fetchone()[0]
        
        if existing_preferences > 0:
            # Update existing preferences
            cursor.execute('''
                UPDATE user_preferences
                SET language = ?, sources = ?, output_format = ?
            ''', (preferences['language'], ','.join(preferences['sources']), preferences['output_format']))
        else:
            # Insert new preferences
            cursor.execute('''
                INSERT INTO user_preferences (language, sources, output_format)
                VALUES (?, ?, ?)
            ''', (preferences['language'], ','.join(preferences['sources']), preferences['output_format']))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while saving user preferences: {e}")
    finally:
        conn.close()

# Function to load user preferences
def load_user_preferences():
    conn = sqlite3.connect('news_search.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT language, sources, output_format FROM user_preferences')
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
        }  # Return default values if no preferences are found
    except sqlite3.Error as e:
        print(f"An error occurred while loading user preferences: {e}")
        return {
            'language': None,
            'sources': [],
            'output_format': None
        }
    finally:
        conn.close()
