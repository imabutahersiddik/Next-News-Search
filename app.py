import streamlit as st
import requests
import json

# Set the page title and layout
st.set_page_config(page_title="Next News Search", layout="wide")

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

# User input for API key with session state support
if "api_key" not in st.session_state:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        st.session_state.api_key = api_key
else:
    api_key = st.session_state.api_key

# User input for search keywords
search_word = st.text_input("Enter keywords to search for news articles:")

# Button to fetch news
if st.button("Search"):
    if api_key and search_word:
        with st.spinner("Fetching news articles..."):
            data = fetch_news(api_key, search_word)
            
        if data and 'articles' in data and len(data['articles']) > 0:
            for article in data['articles']:
                st.write(f"**{article['title']}**")
                st.write(f"{article['description']}")
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

# Instructions link for obtaining an API key
st.markdown("[Click here to get your News API key](https://newsapi.org/register)")

# Modal feature
if "modal_enabled" not in st.session_state:
    st.session_state.modal_enabled = True

# Function to close the modal
def close_modal():
    st.session_state.modal_enabled = False

# Modal display
if st.session_state.modal_enabled:
    modal = st.empty()
    with modal.container():
        st.markdown(
            """
            <div id="modal" style="display: block; position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                                 background-color: rgba(0, 0, 0, 0.7); color: white; 
                                 display: flex; justify-content: center; align-items: center; 
                                 z-index: 1000;">
                <div style="text-align: center; background: #333; padding: 20px; border-radius: 8px;">
                    <h2>Welcome to Next News Search!</h2>
                    <p>Use this application to find the latest news articles.</p>
                    <a href="https://newsapi.org/register" style="color: #00ffcc;">Get your API Key here!</a>
                    <br><br>
                    <button onclick="document.getElementById('modal').style.display='none'; window.location.href = window.location.href;">Close</button>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        # Close the modal when the button is clicked
        if st.button("Close Modal", key="close_modal", on_click=close_modal):
            pass
