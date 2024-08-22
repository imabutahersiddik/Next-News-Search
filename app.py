import streamlit as st
from styles import get_styles
import requests
import json
from datetime import datetime, timedelta
from database import create_table, save_api_key, load_api_key, save_user_preferences, load_user_preferences
from translations import TRANSLATIONS  # Import translations

# Initialize database and create table
create_table()

# Set the page title and layout
st.set_page_config(page_title=TRANSLATIONS["en"].get("app_title", "News App"), layout="wide")

st.markdown(get_styles(), unsafe_allow_html=True)

# Add meta description
st.markdown(
    f'<meta name="description" content="{TRANSLATIONS["en"].get("app_title", "News App")} is a user-friendly application that allows you to search for the latest news articles using the News API. Enter your keywords and API key to fetch relevant news articles effortlessly." />',
    unsafe_allow_html=True
)

# Load the API key from the database
api_key = load_api_key()

# Load user preferences from the database
user_preferences = load_user_preferences()
if user_preferences:
    st.session_state.filters = {
        "language": user_preferences.get('language', None),
        "sources": user_preferences.get('sources', []),
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": user_preferences.get('output_format', "Title and Description")  # Default if None
    }
else:
    st.session_state.filters = {
        "language": None,
        "sources": [],
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": "Title and Description"  # Default output format
    }

# Initialize session state for language and show_date if not already done
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"  # Default language

if "show_date" not in st.session_state:
    st.session_state.show_date = False  # Default value for show_date

# Streamlit app layout
st.markdown(
    f"<h1 style='text-align: center;'>{TRANSLATIONS[st.session_state.selected_language].get('app_title', 'News App')}</h1>",
    unsafe_allow_html=True
)

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
        st.error(TRANSLATIONS[st.session_state.selected_language].get("no_articles_found", "No articles found."))
        return None

# Function to fetch available sources
def fetch_sources(api_key):
    url = f"https://newsapi.org/v2/sources?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)['sources']
    else:
        st.error(TRANSLATIONS[st.session_state.selected_language].get("no_articles_found", "No sources found."))
        return []

# Streamlit app layout
tabs = st.tabs([
    TRANSLATIONS[st.session_state.selected_language].get("search_tab", "Search"), 
    TRANSLATIONS[st.session_state.selected_language].get("filters_tab", "Filters"), 
    TRANSLATIONS[st.session_state.selected_language].get("about_tab", "About"), 
    TRANSLATIONS[st.session_state.selected_language].get("settings_tab", "Settings")
])

# Search Tab
with tabs[0]:
    
    # User input for search keywords
    search_word = st.text_input("", placeholder=TRANSLATIONS[st.session_state.selected_language].get("search_placeholder", "Search..."), key="search_input")
    
    # Button to fetch news (text only)
    if st.button(TRANSLATIONS[st.session_state.selected_language].get("search_button", "Search"), key="search_button"):
        if api_key and search_word:
            with st.spinner(TRANSLATIONS[st.session_state.selected_language].get("fetching_news", "Fetching news...")):
                # Use filters from session state
                language = st.session_state.filters['language'] or st.session_state.selected_language  # Use selected language
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
                    st.subheader(article['title'])
                    st.write(article['description'])
                    results += f"**{article['title']}**\n{article['description']}\n\n"

                    if st.session_state.show_date:
                        st.write(f"Published: {article['publishedAt']}")

                    st.write("-" * 20)

                # Show results in an expander
                with st.expander(TRANSLATIONS[st.session_state.selected_language].get("save_results", "Save Results"), expanded=False):
                    st.text_area(TRANSLATIONS[st.session_state.selected_language].get("copy_results", "Copy Results"), value=results, height=300)

            else:
                st.error(TRANSLATIONS[st.session_state.selected_language].get("no_articles_found", "No articles found."))
        else:
            st.warning(TRANSLATIONS[st.session_state.selected_language].get("please_enter_valid_api_key", "Please enter a valid API key."))

# Filters Tab
with tabs[1]:
    st.header(TRANSLATIONS[st.session_state.selected_language].get("filter_news_by", "Filter News By"))
    
    # Menu options for filtering news
    menu_options = [
        TRANSLATIONS[st.session_state.selected_language].get("recent_news", "Recent News"), 
        TRANSLATIONS[st.session_state.selected_language].get("trending_news", "Trending News"), 
        TRANSLATIONS[st.session_state.selected_language].get("breaking_news", "Breaking News"), 
        TRANSLATIONS[st.session_state.selected_language].get("oldest_news", "Oldest News"), 
        TRANSLATIONS[st.session_state.selected_language].get("custom_date_range", "Custom Date Range")
    ]
    selected_menu = st.selectbox(TRANSLATIONS[st.session_state.selected_language].get("filter_news_by", "Filter News By"), menu_options)

    # Date range selection
    if selected_menu == TRANSLATIONS[st.session_state.selected_language].get("custom_date_range", "Custom Date Range"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.filters['from_date'] = st.date_input(TRANSLATIONS[st.session_state.selected_language].get("from_date", "From Date"), value=st.session_state.filters['from_date'])
        with col2:
            st.session_state.filters['to_date'] = st.date_input(TRANSLATIONS[st.session_state.selected_language].get("to_date", "To Date"), value=st.session_state.filters['to_date'])
    else:
        st.session_state.filters['from_date'] = None
        st.session_state.filters['to_date'] = None

    # Fetch available sources from the API
    if api_key:
        sources_list = fetch_sources(api_key)
        source_options = [source['id'] for source in sources_list]
    else:
        source_options = []

    st.session_state.filters['sources'] = st.multiselect(TRANSLATIONS[st.session_state.selected_language].get("select_sources", "Select Sources"), options=source_options)

    # Number of articles to fetch
    st.session_state.filters['num_articles'] = st.number_input(TRANSLATIONS[st.session_state.selected_language].get("num_articles", "Number of Articles"), min_value=1, max_value=100, value=st.session_state.filters['num_articles'])

    # Output format selection
    output_options = [
        TRANSLATIONS[st.session_state.selected_language].get("title_and_description", "Title and Description"),
        TRANSLATIONS[st.session_state.selected_language].get("title_only", "Title Only"),
        TRANSLATIONS[st.session_state.selected_language].get("description_only", "Description Only"),
        TRANSLATIONS[st.session_state.selected_language].get("content_only", "Content Only"),
        TRANSLATIONS[st.session_state.selected_language].get("title_description_content", "Title, Description, and Content")
    ]
    st.session_state.filters['output_format'] = st.selectbox(TRANSLATIONS[st.session_state.selected_language].get("output_format", "Output Format"), output_options)

    # Move Show Published Date checkbox to the bottom of the Filters tab
    show_date = st.checkbox(TRANSLATIONS[st.session_state.selected_language].get("show_published_date", "Show Published Date"), value=st.session_state.show_date)
    st.session_state.show_date = show_date

# About Tab
with tabs[2]:
    st.write(f"""
    **{TRANSLATIONS[st.session_state.selected_language].get("about_next_news", "About Next News")}**
    
    {TRANSLATIONS[st.session_state.selected_language].get("welcome_message", "Welcome to the News App!")}
    """)

# Settings Tab
with tabs[3]:
    st.header(TRANSLATIONS[st.session_state.selected_language].get("settings_tab", "Settings"))
    
    if api_key:
        st.write(TRANSLATIONS[st.session_state.selected_language].get("current_api_key", "Current API Key") + ": **" + api_key + "**")
        
        # Option to update or remove the API key
        new_api_key = st.text_input(TRANSLATIONS[st.session_state.selected_language].get("update_api_key", "Update API Key"), placeholder=TRANSLATIONS[st.session_state.selected_language].get("enter_api_key", "Enter API Key"))
        
        if st.button(TRANSLATIONS[st.session_state.selected_language].get("update_api_key", "Update API Key")):
            if new_api_key:
                save_api_key(new_api_key)
                st.success(TRANSLATIONS[st.session_state.selected_language].get("api_key_updated", "API Key updated."))
                api_key = new_api_key  # Update the local variable
            else:
                st.warning(TRANSLATIONS[st.session_state.selected_language].get("please_enter_valid_api_key", "Please enter a valid API key."))
        
        if st.button(TRANSLATIONS[st.session_state.selected_language].get("remove_api_key", "Remove API Key")):
            save_api_key(None)  # Remove the API key
            api_key = None  # Clear the local variable
            st.success(TRANSLATIONS[st.session_state.selected_language].get("api_key_removed", "API Key removed."))
    else:
        st.write(TRANSLATIONS[st.session_state.selected_language].get("no_api_key_found", "No API key found."))
        new_api_key = st.text_input(TRANSLATIONS[st.session_state.selected_language].get("enter_api_key", "Enter API Key"))
        if st.button(TRANSLATIONS[st.session_state.selected_language].get("save_api_key", "Save API Key")):
            if new_api_key:
                save_api_key(new_api_key)
                st.success(TRANSLATIONS[st.session_state.selected_language].get("api_key_saved", "API Key saved."))
                api_key = new_api_key  # Update the local variable
            else:
                st.warning(TRANSLATIONS[st.session_state.selected_language].get("please_enter_valid_api_key", "Please enter a valid API key."))

    # Language selection moved to the settings tab
    selected_language = st.selectbox(
        TRANSLATIONS[st.session_state.selected_language].get("select_language", "Select Language"),
        options=list(TRANSLATIONS.keys()),
        format_func=lambda x: TRANSLATIONS[x].get("language_name", x)  # Use the "language_name" key for display
    )
    st.session_state.selected_language = selected_language  # Save selected language in session state

# Modal feature
if "modal_enabled" not in st.session_state:
    st.session_state.modal_enabled = True

# Function to close the modal
def close_modal():
    st.session_state.modal_enabled = False

# Modal display using expander
if st.session_state.modal_enabled:
    with st.expander(TRANSLATIONS[st.session_state.selected_language].get("welcome_message", "Welcome!"), expanded=True):
        st.write(TRANSLATIONS[st.session_state.selected_language].get("welcome_message", "Welcome to the News App!"))
        st.markdown("[Get your API Key here!](https://newsapi.org/register)")
        if st.button(TRANSLATIONS[st.session_state.selected_language].get("close", "Close")):
            close_modal()
