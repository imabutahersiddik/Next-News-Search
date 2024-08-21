import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences

# Initialize database and create table
create_table()

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

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
st.title("Next News Search")

# Load the API key from the database
api_key = load_api_key()

# User input for API key with session state support
if api_key is None:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        save_api_key(api_key)  # Save the API key to the database

# User input for search keywords
search_word = st.text_input("Enter keywords to search for news articles:")

# Menu options for filtering news
menu_options = ["Recent News", "Trending News", "Breaking News", "Oldest News", "Custom Date Range"]
selected_menu = st.selectbox("Filter News By:", menu_options)

# Date range selection
if selected_menu == "Custom Date Range":
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date:", value=datetime.now() - timedelta(days=30))
    with col2:
        to_date = st.date_input("To Date:", value=datetime.now())
else:
    from_date = None
    to_date = None

# Advanced filters for language and sources
language = st.selectbox("Select Language:", options=["", "en", "es", "fr", "de", "it", "zh", "ar"], index=0)

# Fetch available sources from the API
if api_key:
    sources_list = fetch_sources(api_key)
    source_options = [source['id'] for source in sources_list]
else:
    source_options = []

sources = st.multiselect("Select Sources:", options=source_options)

# Number of articles to fetch
num_articles = st.number_input("Number of articles to fetch:", min_value=1, max_value=100, value=19)

# Output options for displaying content
output_options = [
    "Title and Description",
    "Title Only",
    "Description Only",
    "Content Only",
    "Title, Description and Content"
]
selected_output = st.selectbox("Select output format:", output_options)

# Initialize session state variables
if "results" not in st.session_state:
    st.session_state.results = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# Load user preferences from the database
user_preferences = load_user_preferences()
if user_preferences:
    language = user_preferences.get('language', language)
    sources = user_preferences.get('sources', sources)
    selected_output = user_preferences.get('output_format', selected_output)

# Button to fetch news
if st.button("Search"):
    if api_key and search_word:
        with st.spinner("Fetching news articles..."):
            if selected_menu == "Recent News":
                sort_by = 'publishedAt'
            elif selected_menu == "Trending News":
                sort_by = 'popularity'
            elif selected_menu == "Breaking News":
                sort_by = 'relevancy'
            elif selected_menu == "Oldest News":
                sort_by = 'publishedAt'
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                to_date = datetime.now().strftime('%Y-%m-%d')
            else:
                sort_by = 'relevancy'
            
            # Fetch articles for the current page
            sources_str = ",".join(sources) if sources else None
            data = fetch_news(api_key, search_word, sort_by, from_date, to_date, num_articles, st.session_state.current_page, language, sources_str)
            
        if data and 'articles' in data and len(data['articles']) > 0:
            articles = data['articles']
            results = ""  # Initialize a string to hold all results

            for article in articles:
                if selected_output == "Title and Description":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['description'])  # Display the description
                    results += f"**{article['title']}**\n{article['description']}\n\n"
                elif selected_output == "Title Only":
                    st.subheader(article['title'])  # Display the title as a subheader
                    results += f"**{article['title']}**\n\n"
                elif selected_output == "Description Only":
                    st.write(article['description'])  # Display the description
                    results += f"{article['description']}\n\n"
                elif selected_output == "Content Only":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['content'])  # Display the content only
                    results += f"**{article['title']}**\n{article['content']}\n\n"
                elif selected_output == "Title, Description and Content":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['description'])  # Display the description
                    st.write(article['content'])  # Display the full content
                    results += f"**{article['title']}**\n{article['description']}\n{article['content']}\n\n"

                st.write("-" * 20)  # Separator line between articles

            # Store results in session state
            st.session_state.results = results

            # Show results in an expander
            with st.expander("Save Results", expanded=False):
                st.text_area("Copy Results", value=st.session_state.results, height=300)

            # Add to search history
            st.session_state.search_history.append((search_word, sort_by, from_date, to_date, language, sources_str))

            if "show_date" in st.session_state and st.session_state.show_date:
                for article in articles:
                    st.write(f"Published: {article['publishedAt']}")
                st.write("-" * 19)

        else:
            st.warning("No articles found for your search query.")
    else:
        st.warning("Please enter both your API key and search keywords.")

# Pagination controls
if st.session_state.current_page > 1:
    if st.button("Previous Page"):
        st.session_state.current_page -= 1

if data and 'totalResults' in data:
    total_pages = (data['totalResults'] // num_articles) + (1 if data['totalResults'] % num_articles > 0 else 0)
    if st.session_state.current_page < total_pages:
        if st.button("Next Page"):
            st.session_state.current_page += 1

# Display search history
if st.button("Show Search History"):
    if st.session_state.search_history:
        st.write("### Search History")
        for i, (word, sort, from_d, to_d, lang, src) in enumerate(st.session_state.search_history):
            st.write(f"{i + 1}. Keywords: **{word}**, Sort By: **{sort}**, From: **{from_d}**, To: **{to_d}**, Language: **{lang}**, Sources: **{src}**")
    else:
        st.write("No search history available.")

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

# Save user preferences when the search button is clicked
if st.button("Search"):
    user_preferences = {
        'language': language,
        'sources': sources,
        'output_format': selected_output
    }
    save_user_preferences(user_preferences)
