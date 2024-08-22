import streamlit as st
from styles import get_styles
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences
from news_sources import NEWS_SOURCES  # Import the predefined news sources

# Initialize database and create table
create_table()

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

# Streamlit app layout
st.markdown("<h1 style='text-align: center;'>Next News Search</h1>", unsafe_allow_html=True)

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
        "sources": [],
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": "Title and Description"  # Default output format
    }

# Initialize session state for "show_date" if not already done
if "show_date" not in st.session_state:
    st.session_state.show_date = False

# Search Tab
with tabs[0]:
    
    # User input for search keywords
    search_word = st.text_input("", placeholder="Search the news...", key="search_input")
    
    # Button to fetch news (icon on right)
    if st.button("Search", key="search_button"):
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

    # Advanced filters for language and sources
    st.session_state.filters['language'] = st.selectbox(
        "Select Language:", 
        options=[""] + list(LANGUAGES.keys()), 
        format_func=lambda x: LANGUAGES.get(x, x),  # Display readable names
        key="language_select"
    )

    # Use predefined sources from news_sources.py
    source_options = [source['id'] for source in NEWS_SOURCES]
    source_names =
