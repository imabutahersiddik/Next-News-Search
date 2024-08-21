import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences

# Initialize database and create table
create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

# Function to fetch news articles
def fetch_news(api_key, search_word, sort_by='relevancy', from_date=None, to_date=None, page_size=19, page=1, language=None, sources=None):
    url = f"https://newsapi.org/v2/everything?q={search_word}&apiKey={api_key}&sortBy={sort_by}&pageSize={page_size}&page={page}"
    
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"
    
    if language:
        url += f"&language={language}"
    
    if sources:
        url += f"&sources={sources}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Failed to fetch news articles. Please check your API key and try again.")
        return None

# Function to fetch available sources
def fetch_sources(api_key):
    url = f"https://newsapi.org/v2/sources?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)['sources']
    else:
        st.error("Failed to fetch sources. Please check your API key and try again.")
        return []

# Function to get styles
def get_styles():
    return """
    <style>
    /* General body styles */
    body {
        background-color: #f0f4f8;
        color: #333;
        font-family: 'Arial', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
    }

    /* Title styles */
    .stTitle {
        font-size: 2.5em;
        color: #4CAF50;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Search form styles */
    .search-container {
        position: relative;
        width: 100%;
        max-width: 600px;
        margin-bottom: 20px;
    }

    /* Input styles */
    .search-input {
        width: 100%;
        padding: 15px 45px 15px 15px; /* Right padding for icon */
        border: 2px solid #4CAF50;
        border-radius: 5px;
        font-size: 1.2em;
    }

    /* Icon styles */
    .search-icon {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        width: 24px; /* Adjust size as needed */
        height: 24px; /* Adjust size as needed */
    }

    /* Expander styles */
    .stExpander {
        background-color: #e8f5e9;
        border-radius: 5px;
        padding: 10px;
    }

    /* Checkbox styles */
    .stCheckbox {
        margin-bottom: 20px;
    }

    /* Footer styles */
    .stFooter {
        text-align: center;
        padding: 20px;
        font-size: 0.8em;
        color: #777;
    }
    </style>
    """

# Streamlit app layout
st.title("Next News Search")

# Load the API key from the database
api_key = load_api_key()

# User input for API key with session state support
if api_key is None:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        save_api_key(api_key)

# Add custom CSS for styling
st.markdown(get_styles(), unsafe_allow_html=True)

# Create a search container
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)

    # User input for search keywords
    search_word = st.text_input("Enter keywords to search for news articles:", placeholder="Search for news...", key="search_input")

    # Add the search icon
    st.markdown("""
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Magnifying_glass_icon.svg/1024px-Magnifying_glass_icon.svg.png" 
             class="search-icon" 
             alt="Search" 
             onclick="document.getElementById('search_input').dispatchEvent(new Event('change'));" 
             style="cursor: pointer;" />
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Handle the search action
    if st.session_state.search_input:
        if api_key:
            with st.spinner("Fetching news articles..."):
                # Fetch articles based on the search_word and api_key
                data = fetch_news(api_key, st.session_state.search_input)  # Assuming fetch_news is defined
                # Handle the response...
                if data and 'articles' in data:
                    articles = data['articles']
                    for article in articles:
                        st.subheader(article['title'])
                        st.write(article['description'])
                        st.write("-" * 20)
                else:
                    st.warning("No articles found for your search query or an error occurred.")
        else:
            st.warning("Please enter your API key.")

# About page
if st.button("About"):
    st.write("""
    This application allows you to search for news articles using the News API. 
    You can enter your API key to fetch articles based on your search keywords. 
    Your API key will be saved in the current session.
    """)

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

# Toggle to show/hide published date
if "show_date" not in st.session_state:
    st.session_state.show_date = False

show_date = st.checkbox("Show Published Date", value=st.session_state.show_date)
st.session_state.show_date = show_date
