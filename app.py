import streamlit as st
import requests
import json
from datetime import datetime, timedelta

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

# Function to fetch news articles
def fetch_news(api_key, search_word, sort_by='relevancy', from_date=None, to_date=None):
    url = f"https://newsapi.org/v2/everything?q={search_word}&apiKey={api_key}&sortBy={sort_by}"
    
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Failed to fetch news articles. Please check your API key and try again.")
        return None

# Streamlit app layout
st.title("Next News Search")

# User input for API key with session state support
if "api_key" not in st.session_state:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        st.session_state.api_key = api_key
else:
    api_key = st.session_state.api_key

# User input for search keywords
search_word = st.text_input("Enter keywords to search for news articles:")

# Menu options
menu_options = ["Recent News", "Trending News", "Breaking News", "Oldest News", "Custom Date Range"]
selected_menu = st.selectbox("Filter News By:", menu_options)

# Date range selection
if selected_menu == "Custom Date Range":
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date:")
    with col2:
        to_date = st.date_input("To Date:")
else:
    from_date = None
    to_date = None

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
            
            data = fetch_news(api_key, search_word, sort_by, from_date, to_date)
            
        if data and 'articles' in data and len(data['articles']) > 0:
            for article in data['articles']:
                st.write(f"**{article['title']}**")
                st.write(f"{article['description']}")
                if "show_date" in st.session_state and st.session_state.show_date:
                    st.write(f"Published: {article['publishedAt']}")
                st.write("-" * 19)
        else:
            st.warning("No articles found for your search query.")
    else:
        st.warning("Please enter both your API key and search keywords.")

# About page
if st.button("About"):
    st.write("""
    This application allows you to search for news articles using the News API. 
    You can enter your API key to fetch articles based on your search keywords. 
    Your API key will be saved in the current session.
    
    Save your API keys securely, in Erath 
    [Click to continue in Erath](https://erath.vercel.app).
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
