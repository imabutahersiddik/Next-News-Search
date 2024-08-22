import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import secrets
from database import create_table, save_api_key, load_api_key
from news_sources import NEWS_SOURCES
from countries import COUNTRIES
from categories import CATEGORIES
from authors import AUTHORS
import user_database

# Database setup
DATABASE_PATH = "news_app.db"  # Path to your SQLite database file
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Initialize database and create tables
create_table()
user_database.create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

# Static list of languages with readable names
LANGUAGES = {
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "zh": "Chinese",
    "ar": "Arabic"
}

# Function to fetch news articles
def fetch_news(api_key, search_word, sort_by='relevancy', from_date=None, to_date=None, page_size=19, page=1, language=None, country=None, category=None, author=None, sources=None):
    url = f"https://newsapi.org/v2/everything?q={search_word}&apiKey={api_key}&sortBy={sort_by}&pageSize={page_size}&page={page}"
    
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"
    
    if language:
        url += f"&language={language}"
    
    if country:
        url += f"&country={country}"
    
    if category:
        url += f"&category={category}"
    
    if author:
        url += f"&author={author}"
    
    if sources:
        url += f"&sources={sources}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Failed to fetch news articles. Please check your API key and try again.")
        return None

# User Authentication with SQLite Database (using cookies)
def user_authentication():
    st.sidebar.header("User Authentication")

    # Generate a unique session ID
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = secrets.token_urlsafe(512)

    # Check if the user is logged in (based on session ID)
    if 'username' in st.session_state:
        username = st.session_state['username']
        # Check if the session ID matches in the database
        user = user_database.get_user_by_session_id(st.session_state['session_id'])
        if user and user[0] == username:
            # Check if the session is still active
            last_activity = user_database.get_last_activity(st.session_state['session_id'])
            if last_activity:
                # Calculate time since last activity
                time_elapsed = datetime.now() - last_activity
                # Set session timeout to 30 days
                session_timeout = timedelta(days=30)  
                if time_elapsed > session_timeout:
                    st.session_state['is_logged_in'] = False
                    st.session_state['username'] = ''
                    st.sidebar.write("Session expired. Please log in again.")
                else:
                    # Update last activity timestamp
                    user_database.save_last_activity(st.session_state['session_id'])
                    st.session_state['is_logged_in'] = True
                    st.sidebar.write(f"Logged in as: {username}")
                    if st.sidebar.button("Logout"):
                        st.session_state['is_logged_in'] = False
                        st.session_state['username'] = ''
                        st.sidebar.write("Logged out successfully.")
        else:
            # Session ID mismatch or user not found
            st.session_state['is_logged_in'] = False
            st.session_state['username'] = ''
            st.sidebar.write("Session expired. Please log in again.")
    else:
        # User is not logged in
        st.session_state['is_logged_in'] = False
        if 'username' not in st.session_state:
            st.session_state['username'] = ''

        menu = ["Login", "Register"]
        choice = st.sidebar.selectbox("Select Action", menu)

        if choice == "Login":
            username = st.sidebar.text_input("Username", key="login_username")
            password = st.sidebar.text_input("Password", type='password', key="login_password")
            if st.sidebar.button("Login"):
                user = user_database.get_user(username)
                if user and user[1] == password:
                    st.success("Logged in successfully!")
                    st.session_state['username'] = username
                    st.session_state['is_logged_in'] = True
                    # Save session ID in the database
                    user_database.save_session_id(st.session_state['session_id'], username)
                else:
                    st.error("Invalid username or password.")

        elif choice == "Register":
            username = st.sidebar.text_input("Choose a Username", key="register_username")
            password = st.sidebar.text_input("Choose a Password", type='password', key="register_password")
            if st.sidebar.button("Register"):
                if user_database.get_user(username) is None:
                    user_database.add_user(username, password)
                    st.success("Registration completed! You can now log in.")
                else:
                    st.error("Username already exists. Please choose a different one.")

    return st.session_state['is_logged_in']

# Call the user authentication function
authentication_status = user_authentication()

# Load the API key from the database
api_key = load_api_key()

# Prompt for API key if not available
if not api_key:
    st.warning("Please enter your API key to use the application.")
    new_api_key = st.text_input("Enter your News API key:", key="new_api_key_input")
    if st.button("Save API Key", key="save_api_key_button"):
        if new_api_key:
            save_api_key(new_api_key)
            st.success("API Key saved successfully!")
            api_key = new_api_key  # Update the local variable
        else:
            st.warning("Please enter a valid API key.")

# Create tabs for Search, Filters, About, and Settings
tabs = st.tabs(["Search", "Filters", "About", "Settings"])

# Initialize session state for filters if not already done
if "filters" not in st.session_state:
    st.session_state.filters = {
        "language": "",
        "country": "",
        "category": "",
        "author": "",
        "sources": [],
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": "Title and Description"  # Default output format
    }

# Initialize session state for "show_date" if not already done
if "show_date" not in st.session_state:
    st.session_state.show_date = False

# Check if user is logged in
if not authentication_status:
    st.warning("Please log in to access the application.")
else:
    # Search Tab
    with tabs[0]:
        st.markdown("<h1 style='text-align: center;'>Next News Search</h1>", unsafe_allow_html=True)

        # User input for search keywords
        search_word = st.text_input("Search the news...", placeholder="Enter keywords here...", key="search_input")

        # Button to fetch news
        if st.button("Search", key="search_button"):
            if api_key and search_word:
                with st.spinner("Fetching news articles..."):
                    # Use filters from session state
                    language = st.session_state.filters['language']
                    country = st.session_state.filters['country']
                    category = st.session_state.filters['category']
                    author = st.session_state.filters['author']
                    sources = st.session_state.filters['sources']
                    from_date = st.session_state.filters['from_date']
                    to_date = st.session_state.filters['to_date']
                    num_articles = st.session_state.filters['num_articles']

                    # Convert dates to string format
                    from_date_str = from_date.strftime('%Y-%m-%d') if from_date else None
                    to_date_str = to_date.strftime('%Y-%m-%d') if to_date else None

                    # Fetch articles
                    sources_str = ",".join(sources) if sources else None
                    data = fetch_news(api_key, search_word, 'relevancy', from_date_str, to_date_str, num_articles, 1, language, country, category, author, sources_str)

                    # Check if data is not None and contains 'articles'
                    if data and 'articles' in data:
                        articles = data['articles']
                        results = ""

                        for article in articles:
                            if st.session_state.filters['output_format'] == "Title and Description":
                                st.subheader(article['title'])
                                st.write(article['description'])
                                results += f"**{article['title']}**\n{article['description']}\n\n"
                            # ... (other output formats)

                        # Show results in an expander
                        with st.expander("Save Results", expanded=False):
                            st.text_area("Copy Results", value=results, height=300)

                    else:
                        st.warning("No articles found for your search query or an error occurred.")
            else:
                st.warning("Please enter both your API key and search keywords.")

    # Filters Tab
    with tabs[1]:
        st.header("Filter News")

        # Advanced filters for language, country, category, author, and sources
        st.session_state.filters['language'] = st.selectbox(
            "Select Language:",
            options=[""] + list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES.get(x, x),  # Display readable names
            key="language_select"
        )

        # ... (other filters)

    # About Tab
    with tabs[2]:
        st.write("""
        **About Next News Search**
        
        This application allows you to search for news articles using the News API. 
        You can enter your API key to fetch articles based on your search keywords. 
        Your API key will be saved in the current session.
        
        Explore the latest news articles effortlessly and customize your search with various filters!
        """)

    # Settings Tab
    with tabs[3]:
        st.header("Settings")

        if api_key:
            st.write("Current API Key: **" + api_key + "**")

            # Option to update or remove the API key
            new_api_key = st.text_input("Update API Key:", placeholder="Enter new API key here", key="update_api_key_input")

            if st.button("Update API Key", key="update_api_key_button"):
                if new_api_key:
                    save_api_key(new_api_key)
                    st.success("API Key updated successfully!")
                    api_key = new_api_key  # Update the local variable
                else:
                    st.warning("Please enter a valid API key.")

            if st.button("Remove API Key", key="remove_api_key_button"):
                save_api_key(None)  # Remove the API key
                api_key = None  # Clear the local variable
                st.success("API Key removed successfully!")
        else:
            st.write("No API Key found.")
            new_api_key = st.text_input("Enter your News API key:", key="new_api_key_input_2")
            if st.button("Save API Key", key="save_api_key_button_2"):
                if new_api_key:
                    save_api_key(new_api_key)
                    st.success("API Key saved successfully!")
                    api_key = new_api_key  # Update the local variable
                else:
                    st.warning("Please enter a valid API key.")

# Close the database connection
conn.close()
