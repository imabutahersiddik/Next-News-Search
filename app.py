import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from menu import render_menu

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

# Function to fetch news articles
def fetch_news(api_key, search_word, sort_by='relevancy', from_date=None, to_date=None, page_size=19):
    url = f"https://newsapi.org/v2/everything?q={search_word}&apiKey={api_key}&sortBy={sort_by}&pageSize={page_size}"
    
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Failed to fetch news articles. Please check your API key and try again.")
        return None

# Initialize session state for page
if "page" not in st.session_state:
    st.session_state.page = "recent_news"

# Render the menu
render_menu()

# User input for API key with session state support
if "api_key" not in st.session_state:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        st.session_state.api_key = api_key
else:
    api_key = st.session_state.api_key

# User input for search keywords
search_word = st.text_input("Enter keywords to search for news articles:")

# Initialize a session state variable to hold results
if "results" not in st.session_state:
    st.session_state.results = ""

# Button to fetch news
if st.button("Search"):
    if api_key and search_word:
        with st.spinner("Fetching news articles..."):
            sort_by = 'publishedAt'  # Default sort
            from_date, to_date = None, None
            
            if st.session_state.page == "recent_news":
                sort_by = 'publishedAt'
            elif st.session_state.page == "trending_news":
                sort_by = 'popularity'
            elif st.session_state.page == "breaking_news":
                sort_by = 'relevancy'
            elif st.session_state.page == "oldest_news":
                sort_by = 'publishedAt'
                from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                to_date = datetime.now().strftime('%Y-%m-%d')
            elif st.session_state.page == "custom_date_range":
                from_date = st.date_input("From Date:", value=datetime.now() - timedelta(days=30))
                to_date = st.date_input("To Date:", value=datetime.now())
            
            data = fetch_news(api_key, search_word, sort_by, from_date, to_date)

        if data and 'articles' in data and len(data['articles']) > 0:
            articles = data['articles']
            results = ""  # Initialize a string to hold all results

            for article in articles:
                result = f"**{article['title']}**\n{article['description']}\n---\n"
                results += result
                st.write(result)  # Display the result

            # Store results in session state
            st.session_state.results = results

            # Show results in an expander
            with st.expander("Save Results", expanded=True):
                st.text_area("Copy Results", value=st.session_state.results, height=300)
        else:
            st.warning("No articles found for your search query.")
    else:
        st.warning("Please enter both your API key and search keywords.")
