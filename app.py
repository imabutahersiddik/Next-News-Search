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
st.set_page_config(page_title=TRANSLATIONS["en"]["app_title"], layout="wide")

st.markdown(get_styles(), unsafe_allow_html=True)

# Add meta description
st.markdown(f'<meta name="description" content="{TRANSLATIONS["en"]["app_title"]} is a user-friendly application that allows you to search for the latest news articles using the News API. Enter your keywords and API key to fetch relevant news articles effortlessly." />', unsafe_allow_html=True)

# Load the API key from the database
api_key = load_api_key()

# Load user preferences from the database
user_preferences = load_user_preferences()
if user_preferences:
    st.session_state.filters = {
        "language": user_preferences['language'],
        "sources": user_preferences['sources'],
        "from_date": datetime.now() - timedelta(days=30),
        "to_date": datetime.now(),
        "num_articles": 19,
        "output_format": user_preferences['output_format'] or "Title and Description"  # Default if None
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

# Initialize session state for language if not already done
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"  # Default language

# Language selection
selected_language = st.selectbox(
    TRANSLATIONS[st.session_state.selected_language]["select_language"],
    options=list(TRANSLATIONS.keys()),
    format_func=lambda x: TRANSLATIONS[x]["select_language"]
)
st.session_state.selected_language = selected_language  # Save selected language in session state

# Streamlit app layout
st.markdown(f"<h1 style='text-align: center;'>{TRANSLATIONS[st.session_state.selected_language]['app_title']}</h1>", unsafe_allow_html=True)

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
        st.error(TRANSLATIONS[st.session_state.selected_language]["no_articles_found"])
        return None

# Function to fetch available sources
def fetch_sources(api_key):
    url = f"https://newsapi.org/v2/sources?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.text)['sources']
    else:
        st.error(TRANSLATIONS[st.session_state.selected_language]["no_articles_found"])
        return []

# Streamlit app layout
tabs = st.tabs([TRANSLATIONS[st.session_state.selected_language]["search_tab"], 
                TRANSLATIONS[st.session_state.selected_language]["filters_tab"], 
                TRANSLATIONS[st.session_state.selected_language]["about_tab"], 
                TRANSLATIONS[st.session_state.selected_language]["settings_tab"]])

# Search Tab
with tabs[0]:
    
    # User input for search keywords
    search_word = st.text_input("", placeholder=TRANSLATIONS[st.session_state.selected_language]["search_placeholder"], key="search_input")
    
    # Button to fetch news (text only)
    if st.button(TRANSLATIONS[st.session_state.selected_language]["search_button"], key="search_button"):
        if api_key and search_word:
            with st.spinner(TRANSLATIONS[st.session_state.selected_language]["fetching_news"]):
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
                with st.expander(TRANSLATIONS[st.session_state.selected_language]["save_results"], expanded=False):
                    st.text_area(TRANSLATIONS[st.session_state.selected_language]["copy_results"], value=results, height=300)

            else:
                st.error(TRANSLATIONS[st.session_state.selected_language]["no_articles_found"])
        else:
            st.warning(TRANSLATIONS[st.session_state.selected_language]["please_enter_valid_api_key"])

# Filters Tab
with tabs[1]:
    st.header(TRANSLATIONS[st.session_state.selected_language]["filter_news_by"])
    
    # Menu options for filtering news
    menu_options = [TRANSLATIONS[st.session_state.selected_language]["recent_news"], 
                    TRANSLATIONS[st.session_state.selected_language]["trending_news"], 
                    TRANSLATIONS[st.session_state.selected_language]["breaking_news"], 
                    TRANSLATIONS[st.session_state.selected_language]["oldest_news"], 
                    TRANSLATIONS[st.session_state.selected_language]["custom_date_range"]]
    selected_menu = st.selectbox(TRANSLATIONS[st.session_state.selected_language]["filter_news_by"], menu_options)

    # Date range selection
    if selected_menu == TRANSLATIONS[st.session_state.selected_language]["custom_date_range"]:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.filters['from_date'] = st.date_input(TRANSLATIONS[st.session_state.selected_language]["from_date"], value=st.session_state.filters['from_date'])
        with col2:
            st.session_state.filters['to_date'] = st.date_input(TRANSLATIONS[st.session_state.selected_language]["to_date"], value=st.session_state.filters['to_date'])
    else:
        st.session_state.filters['from_date'] = None
        st.session_state.filters['to_date'] = None

    # Advanced filters for language and sources
    st.session_state.filters['language'] = st.selectbox(TRANSLATIONS[st.session_state.selected_language]["select_language"], options=["", "en", "es", "fr", "de", "it", "zh", "ja", "ko", "hi", "ur", "ar", "bn", "ru"], index=0)

    # Fetch available sources from the API
    if api_key:
        sources_list = fetch_sources(api_key)
        source_options = [source['id'] for source in sources_list]
    else:
        source_options = []

    st.session_state.filters['sources'] = st.multiselect(TRANSLATIONS[st.session_state.selected_language]["select_sources"], options=source_options)

    # Number of articles to fetch
    st.session_state.filters['num_articles'] = st.number_input(TRANSLATIONS[st.session_state.selected_language]["num_articles"], min_value=1, max_value=100, value=st.session_state.filters['num_articles'])

    # Output format selection
    output_options = [
        TRANSLATIONS[st.session_state.selected_language]["title_and_description"],
        TRANSLATIONS[st.session_state.selected_language]["title_only"],
        TRANSLATIONS[st.session_state.selected_language]["description_only"],
        TRANSLATIONS[st.session_state.selected_language]["content_only"],
        TRANSLATIONS[st.session_state.selected_language]["title_description_content"]
    ]
    st.session_state.filters['output_format'] = st.selectbox(TRANSLATIONS[st.session_state.selected_language]["select_output_format"], output_options)

    # Move Show Published Date checkbox to the bottom of the Filters tab
    show_date = st.checkbox(TRANSLATIONS[st.session_state.selected_language]["show_published_date"], value=st.session_state.show_date)
    st.session_state.show_date = show_date

# About Tab
with tabs[2]:
    st.write(f"""
    **{TRANSLATIONS[st.session_state.selected_language]["about_next_news"]}**
    
    {TRANSLATIONS[st.session_state.selected_language]["welcome_message"]}
    """)

# Settings Tab
with tabs[3]:
    st.header(TRANSLATIONS[st.session_state.selected_language]["settings_tab"])
    
    if api_key:
        st.write(TRANSLATIONS[st.session_state.selected_language]["current_api_key"] + ": **" + api_key + "**")
        
        # Option to update or remove the API key
        new_api_key = st.text_input(TRANSLATIONS[st.session_state.selected_language]["update_api_key"], placeholder=TRANSLATIONS[st.session_state.selected_language]["enter_api_key"])
        
        if st.button(TRANSLATIONS[st.session_state.selected_language]["update_api_key"]):
            if new_api_key:
                save_api_key(new_api_key)
                st.success(TRANSLATIONS[st.session_state.selected_language]["api_key_updated"])
                api_key = new_api_key  # Update the local variable
            else:
                st.warning(TRANSLATIONS[st.session_state.selected_language]["please_enter_valid_api_key"])
        
        if st.button(TRANSLATIONS[st.session_state.selected_language]["remove_api_key"]):
            save_api_key(None)  # Remove the API key
            api_key = None  # Clear the local variable
            st.success(TRANSLATIONS[st.session_state.selected_language]["api_key_removed"])
    else:
        st.write(TRANSLATIONS[st.session_state.selected_language]["no_api_key_found"])
        new_api_key = st.text_input(TRANSLATIONS[st.session_state.selected_language]["enter_api_key"])
        if st.button(TRANSLATIONS[st.session_state.selected_language]["save_api_key"]):
            if new_api_key:
                save_api_key(new_api_key)
                st.success(TRANSLATIONS[st.session_state.selected_language]["api_key_saved"])
                api_key = new_api_key  # Update the local variable
            else:
                st.warning(TRANSLATIONS[st.session_state.selected_language]["please_enter_valid_api_key"])

# Modal feature
if "modal_enabled" not in st.session_state:
    st.session_state.modal_enabled = True

# Function to close the modal
def close_modal():
    st.session_state.modal_enabled = False

# Modal display using expander
if st.session_state.modal_enabled:
    with st.expander(TRANSLATIONS[st.session_state.selected_language]["welcome_message"], expanded=True):
        st.write(TRANSLATIONS[st.session_state.selected_language]["welcome_message"])
        st.markdown("[Get your API Key here!](https://newsapi.org/register)")
        if st.button(TRANSLATIONS[st.session_state.selected_language]["close"]):
            close_modal()
