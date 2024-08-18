import streamlit as st
import requests
import json

# Function to fetch news articles
def fetch_news(api_key, search_word):
    url = f"https://newsapi.org/v2/everything?q={search_word}&apiKey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Failed to fetch news articles. Please check your API key and try again.")
        return None

# Streamlit app layout
st.title("Next News Search")

# User input for API key with cookie support
api_key = st.text_input("Enter your News API key:", type="password")
if api_key:
    st.session_state.api_key = api_key  # Save API key in session state

# User input for search keywords
search_word = st.text_input("Enter keywords to search for news articles:")

# Button to fetch news
if st.button("Search"):
    if 'api_key' in st.session_state and search_word:
        with st.spinner("Fetching news articles..."):
            data = fetch_news(st.session_state.api_key, search_word)
            
        if data and 'articles' in data and len(data['articles']) > 0:
            for article in data['articles']:
                st.write(f"**** {article['title']}")
                st.write(f"**** {article['description']}")
                st.write("-" * 19)
        else:
            st.warning("No articles found for your search query.")
    else:
        st.warning("Please enter both your API key and search keywords.")

# Instructions link for obtaining an API key
st.markdown("[Click here to get your News API key](https://newsapi.org/register)")
