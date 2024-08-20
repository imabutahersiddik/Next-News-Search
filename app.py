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
    st.write("")

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

# Output options for displaying content
output_options = [
    "Title and Description",
    "Title Only",
    "Description Only",
    "Content Only",
    "Title, Description and Content"
]
selected_output = st.selectbox("Select output format:", output_options)

# Initialize a session state variable to hold results
if "results" not in st.session_state:
    st.session_state.results = ""

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
            articles = data['articles']
            results = ""  # Initialize a string to hold all results

            for article in articles:
                if selected_output == "Title and Description":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['description'])  # Display the description
                elif selected_output == "Title Only":
                    st.subheader(article['title'])  # Display the title as a subheader
                elif selected_output == "Description Only":
                    st.write(article['description'])  # Display the description
                elif selected_output == "Content Only":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['content'])  # Display the content only
                elif selected_output == "Title, Description and Content":
                    st.subheader(article['title'])  # Display the title as a subheader
                    st.write(article['description'])  # Display the description
                    st.write(article['content'])  # Display the full content

                st.write("-" * 20)  # Separator line between articles

            # Store results in session state
            st.session_state.results = results

            # Show results in an expander
            with st.expander("Save Results", expanded=True):
                st.text_area("Copy Results", value=st.session_state.results, height=300)

            if "show_date" in st.session_state and st.session_state.show_date:
                for article in articles:
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
