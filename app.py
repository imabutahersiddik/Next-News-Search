import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key

# Initialize database and create table
create_table()

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

# Streamlit app layout
st.title("Next News Search")

# Load the API key from the database
api_key = load_api_key()

# User input for API key with session state support
if api_key is None:
    api_key = st.text_input("Enter your News API key:")
    if api_key:
        save_api_key(api_key)  # Save the API key to the database
else:
    st.write("API Key loaded from database.")

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

# Number of articles to fetch
num_articles = st.number_input("Number of articles to fetch:", min_value=1, max_value=100, value=19)

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
            
            data = fetch_news(api_key, search_word, sort_by, from_date, to_date, num_articles)
            
        if data and 'articles' in data and len(data['articles']) > 0:
            for article in data['articles']:
                # Here we modify the output to match the old app's look
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
            <div id="modal" style="display: flex; position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                                 background-color: rgba(0, 0, 0, 0.7); color: white; 
                                 justify-content: center; align-items: center; 
                                 z-index: 1000;">
                <div style="text-align: center; background: #333; padding: 20px; border-radius: 8px;">
                    <h2>Welcome to Next News Search!</h2>
                    <p>Use this application to find the latest news articles.</p>
                    <a href="https://newsapi.org/register" style="color: #00ffcc;">Get your API Key here!</a>
                    <br><br>
                    <button style="padding: 10px; background-color: #00ffcc; border: none; border-radius: 5px; cursor: pointer;" 
                            onclick="document.getElementById('modal').style.display='none'; window.location.reload();">Close</button>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
