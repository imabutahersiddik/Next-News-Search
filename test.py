# app.py
import streamlit as st
from styles import get_styles
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences
from news_sources import NEWS_SOURCES
from countries import COUNTRIES
from categories import CATEGORIES
from authors import AUTHORS
import user_database
import secrets
import sqlite3
import yaml
from streamlit.components.v1 import html

# Load configuration from YAML file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Database setup
DATABASE_PATH = "news_app.db"  # Path to your SQLite database file
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Initialize database and create tables
create_table()
user_database.create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

st.markdown(get_styles(), unsafe_allow_html=True)

# Add meta description
st.markdown('<meta name="description" content="Next News Search is a user-friendly application that allows you to search for the latest news articles using the News API. Enter your keywords and API key to fetch relevant news articles effortlessly." />', unsafe_allow_html=True)

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

# Function to fetch news articles (from old main file)
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

# User Authentication with SQLite Database and Cookies
def user_authentication():
    st.sidebar.header("User Authentication")

    # Generate a unique session ID
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = secrets.token_urlsafe(32)

    # Check if a cookie exists
    if 'username' in st.cookies:
        username = st.cookies['username']
        # Check if the session ID matches in the database
        user = user_database.get_user_by_session_id(st.session_state['session_id'])
        if user and user[0] == username:
            # Check if the session is still active
            last_activity = user_database.get_last_activity(st.session_state['session_id'])
            if last_activity:
                # Calculate time since last activity
                time_elapsed = datetime.now() - last_activity
                # Set session timeout to 9999 days (NOT RECOMMENDED)
                session_timeout = timedelta(days=9999)  
                if time_elapsed > session_timeout:
                    st.session_state['is_logged_in'] = False
                    st.session_state['username'] = ''
                    st.sidebar.write("Session expired. Please log in again.")
                else:
                    # Update last activity timestamp
                    user_database.save_last_activity(st.session_state['session_id'])
                    st.session_state['is_logged_in'] = True
                    st.session_state['username'] = username
                    st.sidebar.write(f"Logged in as: {username}")
                    if st.sidebar.button("Logout"):
                        # Delete the cookie
                        st.cookies.delete('username')
                        st.session_state['is_logged_in'] = False
                        st.session_state['username'] = ''
                        st.sidebar.write("Logged out successfully.")
        else:
            # Session ID mismatch or user not found
            st.session_state['is_logged_in'] = False
            st.session_state['username'] = ''
            st.sidebar.write("Session expired. Please log in again.")
    else:
        # No cookie found
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
                    # Set the cookie
                    st.cookies['username'] = username
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

# Call the user authentication function
user_authentication()

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
if not st.session_state['is_logged_in']:
    st.warning("Please log in to access the application.")
else:
    # Search Tab
    with tabs[0]:
        st.markdown("<h1 style='text-align: center;'>Next News Search</h1>", unsafe_allow_html=True)

        # User input for search keywords
        search_word = st.text_input("Search the news...", placeholder="Enter keywords here...", key="search_input")

        # Button to fetch news (icon on right)
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

                    # Fetch articles (using the function from old main file)
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
                            elif st.session_state.filters['output_format'] == "Title Only":
                                st.subheader(article['title'])
                                results += f"**{article['title']}**\n\n"
                            elif st.session_state.filters['output_format'] == "Description Only":
                                st.write(article['description'])
                                results += f"{article['description']}\n\n"
                            elif st.session_state.filters['output_format'] == "Content Only":
                                st.subheader(article['title'])
                                st.write(article['content'])
                                results += f"**{article['title']}**\n{article['content']}\n\n"
                            elif st.session_state.filters['output_format'] == "Title, Description and Content":
                                st.subheader(article['title'])
                                st.write(article['description'])
                                st.write(article['content'])
                                results += f"**{article['title']}**\n{article['description']}\n{article['content']}\n\n"

                            if st.session_state.show_date:
                                st.write(f"Published: {article['publishedAt']}")

                            st.write("-" * 20)

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

        # Menu options for filtering news
        menu_options = ["Recent News", "Trending News", "Breaking News", "Oldest News", "Custom Date Range"]
        selected_menu = st.selectbox("Filter News By:", menu_options, key="filter_menu")

        # Date range selection
        if selected_menu == "Custom Date Range":
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.filters['from_date'] = st.date_input("From Date:", value=st.session_state.filters['from_date'], key="from_date_input")
            with col2:
                st.session_state.filters['to_date'] = st.date_input("To Date:", value=st.session_state.filters['to_date'], key="to_date_input")
        else:
            st.session_state.filters['from_date'] = None
            st.session_state.filters['to_date'] = None

        # Advanced filters for language, country, category, author, and sources
        st.session_state.filters['language'] = st.selectbox(
            "Select Language:",
            options=[""] + list(LANGUAGES.keys()),
            format_func=lambda x: LANGUAGES.get(x, x),  # Display readable names
            key="language_select"
        )

        st.session_state.filters['country'] = st.selectbox(
            "Select Country:",
            options=[""] + list(COUNTRIES.keys()),
            format_func=lambda x: COUNTRIES.get(x, x),  # Display readable country names
            key="country_select"
        )

        st.session_state.filters['category'] = st.selectbox(
            "Select Category:",
            options=[""] + list(CATEGORIES.keys()),
            format_func=lambda x: CATEGORIES.get(x, x),  # Display readable category names
            key="category_select"
        )

        st.session_state.filters['author'] = st.selectbox(
            "Select Author:",
            options=[""] + list(AUTHORS.keys()),
            key="author_select"
        )

        # Use predefined sources from news_sources.py
        source_options = [source['id'] for source in NEWS_SOURCES]
        source_names = [source['name'] for source in NEWS_SOURCES]

        st.session_state.filters['sources'] = st.multiselect("Select Sources:", options=source_options, format_func=lambda x: source_names[source_options.index(x)], key="source_select")

        # Number of articles to fetch
        st.session_state.filters['num_articles'] = st.number_input("Number of articles to fetch:", min_value=1, max_value=100, value=st.session_state.filters['num_articles'], key="num_articles_input")

        # Output format selection
        output_options = [
            "Title and Description",
            "Title Only",
            "Description Only",
            "Content Only",
            "Title, Description and Content"
        ]
        st.session_state.filters['output_format'] = st.selectbox("Select Output Format:", output_options, key="output_format_select")

        # Move Show Published Date checkbox to the bottom of the Filters tab
        show_date = st.checkbox("Show Published Date", value=st.session_state.show_date, key="show_date_checkbox")
        st.session_state.show_date = show_date

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

    # Modal feature
    if "modal_enabled" not in st.session_state:
        st.session_state.modal_enabled = True

    # Function to close the modal
    def close_modal():
        st.session_state.modal_enabled = False

    # Modal display using expander
    if st.session_state.modal_enabled:
        with st.expander("Welcome to Next News Search!", expanded=True):
            st.write("Use this application to find the latest news articles.")
            st.markdown("[Get your API Key here!](https://newsapi.org/register)")
            if st.button("Close"):
                close_modal()

# Close the database connection
conn.close()
