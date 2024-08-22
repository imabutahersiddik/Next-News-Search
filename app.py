import streamlit as st
from styles import get_styles
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences, register_user, login_user, load_user, save_search, load_api_keys
from news_sources import NEWS_SOURCES
from countries import COUNTRIES
from categories import CATEGORIES
from authors import AUTHORS

# Initialize database and create table
create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

st.markdown(get_styles(), unsafe_allow_html=True)

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

# Streamlit app layout
st.markdown("<h1 style='text-align: center;'>Next News Search</h1>", unsafe_allow_html=True)

# User authentication
if "user" not in st.session_state:
    st.session_state.user = None

# Registration and Login
if st.session_state.user is None:
    st.sidebar.header("User Authentication")
    auth_option = st.sidebar.selectbox("Choose an option:", ["Login", "Register"])

    if auth_option == "Register":
        username = st.text_input("Username")
        full_name = st.text_input("Full Name")
        country = st.selectbox("Country", options=list(COUNTRIES.keys()))
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            register_user(username, full_name, country, email, password)
            st.success("Registration successful! You can now log in.")

    elif auth_option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.user = username
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")

# Load the API keys for the logged-in user
if st.session_state.user:
    api_keys = load_api_keys(st.session_state.user)

    # Prompt for API key if not available
    if not api_keys:
        st.warning("Please enter your API key to use the application.")
        new_api_key = st.text_input("Enter your News API key:", key="new_api_key_input")
        if st.button("Save API Key", key="save_api_key_button"):
            if new_api_key:
                save_api_key(st.session_state.user, new_api_key)
                st.success("API Key saved successfully!")
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
            "output_format": "Title and Description"
        }

    # Search Tab
    with tabs[0]:
        search_word = st.text_input("", placeholder="Search the news...", key="search_input")
        
        if st.button("Search", key="search_button"):
            if api_keys and search_word:
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
                    data = fetch_news(api_keys[0], search_word, 'relevancy', from_date_str, to_date_str, num_articles, 1, language, country, category, author, sources_str)
                    
                if data and 'articles' in data:
                    articles = data['articles']
                    results = ""

                    for article in articles:
                        st.subheader(article['title'])
                        st.write(article['description'])
                        results += f"**{article['title']}**\n{article['description']}\n\n"
                        st.write("-" * 20)

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
            format_func=lambda x: LANGUAGES.get(x, x), 
            key="language_select"
        )

        st.session_state.filters['country'] = st.selectbox(
            "Select Country:",
            options=[""] + list(COUNTRIES.keys()),
            format_func=lambda x: COUNTRIES.get(x, x), 
            key="country_select"
        )

        st.session_state.filters['category'] = st.selectbox(
            "Select Category:",
            options=[""] + list(CATEGORIES.keys()),
            format_func=lambda x: CATEGORIES.get(x, x), 
            key="category_select"
        )

        st.session_state.filters['author'] = st.selectbox(
            "Select Author:",
            options=[""] + list(AUTHORS.keys()),
            key="author_select"
        )

        source_options = [source['id'] for source in NEWS_SOURCES]
        source_names = [source['name'] for source in NEWS_SOURCES]
        
        st.session_state.filters['sources'] = st.multiselect("Select Sources:", options=source_options, format_func=lambda x: source_names[source_options.index(x)], key="source_select")

        st.session_state.filters['num_articles'] = st.number_input("Number of articles to fetch:", min_value=1, max_value=100, value=st.session_state.filters['num_articles'], key="num_articles_input")

        output_options = [
            "Title and Description",
            "Title Only",
            "Description Only",
            "Content Only",
            "Title, Description and Content"
        ]
        st.session_state.filters['output_format'] = st.selectbox("Select Output Format:", output_options, key="output_format_select")

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
        
        if api_keys:
            st.write("Current API Keys:")
            for key in api_keys:
                st.write(f"- {key}")
            
            new_api_key = st.text_input("Add New API Key:", placeholder="Enter new API key here", key="update_api_key_input")
            
            if st.button("Add API Key", key="add_api_key_button"):
                if new_api_key:
                    save_api_key(st.session_state.user, new_api_key)
                    st.success("API Key added successfully!")
                else:
                    st.warning("Please enter a valid API key.")
            
            if st.button("Remove Last API Key", key="remove_api_key_button"):
                if api_keys:
                    api_keys.pop()  # Remove the last API key
                    st.success("Last API Key removed successfully!")
                else:
                    st.warning("No API keys to remove.")
        else:
            st.write("No API Keys found.")

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
            close_modal())
