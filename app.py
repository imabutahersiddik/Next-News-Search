import streamlit as st
from styles import get_styles
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences

# Initialize database and create table
create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

st.markdown(get_styles(), unsafe_allow_html=True)

# Add meta description
st.markdown('<meta name="description" content="Next News Search is a user-friendly application that allows you to search for the latest news articles using the News API. Enter your keywords and API key to fetch relevant news articles effortlessly." />', unsafe_allow_html=True)

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

# Streamlit app layout
st.markdown("<h1 style='text-align: center;'>Next News Search</h1>", unsafe_allow_html=True)

# Load the API key from the database
api_key = load_api_key()

# Create tabs for Search, Filters, About, and Settings
tabs = st.tabs(["Search", "Filters", "About", "Settings"])

# Initialize session state for filters if not already done
if "filters" not in st.session_state:
    st.session_state.filters = {
        "language": "",
        "sources": [],
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": "Title and Description"  # Default output format
    }

# Initialize session state for "show_date" if not already done
if "show_date" not in st.session_state:
    st.session_state.show_date = False

# Initialize session state for "search" if not already done
if "search" not in st.session_state:
    st.session_state.search = False

# Search Tab
with tabs[0]:
    
    # User input for search keywords with enter to search functionality
    search_word = st.text_input("", placeholder="Search the news...", key="search_input", on_change=lambda: st.session_state.on_search_change())
    
    # Button to fetch news (icon on right)
    if st.button("🔍", key="search_button") or st.session_state.search:
        if api_key and search_word:
            with st.spinner("Fetching news articles..."):
                # Use filters from session state
                language = st.session_state.filters['language']
                sources = st.session_state.filters['sources']
                from_date = st.session_state.filters['from_date']
                to_date = st.session_state.filters['to_date']
                num_articles = st.session_state.filters['num_articles']
                
                # Convert dates to string format
                from_date_str = from_date.strftime('%Y-%m-%d') if from_date else None
                to_date_str = to_date.strftime('%Y-%m-%d') if to_date else None
                
                # Fetch articles
                sources_str = ",".join(sources) if sources else None
                data = fetch_news(api_key, search_word, 'relevancy', from_date_str, to_date_str, num_articles, 1, language, sources_str)
                
            # Check if data is not None and contains 'articles'
            if data and 'articles' in data:
                articles = data['articles']
                results = ""

                for article in articles:
                    if st.session_state.filters['output_format'] == "Title and Description":
                        st.subheader(article['title'])
                        st.write(article['description'])
                        results += f"**{article['title']}**\n{article['description']}\n\n"
                    # ... (rest of the code remains the same)

        # Reset the search flag
        st.session_state.search = False

# ... (rest of the code remains the same)

# Function to handle search change
def on_search_change():
    st.session_state.search = True
