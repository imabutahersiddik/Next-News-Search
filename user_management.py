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

def save_user_preferences(preferences):
    conn = sqlite3.connect('users.db')
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

def load_user_preferences():
    conn = sqlite3.connect('users.db')
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
