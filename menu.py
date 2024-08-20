import streamlit as st

menu_options = {
    "Recent News": "recent_news",
    "Trending News": "trending_news",
    "Breaking News": "breaking_news",
    "Oldest News": "oldest_news",
    "Custom Date Range": "custom_date_range",
    "About": "about",
}

def render_menu():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(menu_options.keys()))
    
    if selection == "About":
        st.title("About")
        st.write("""
        This application allows you to search for news articles using the News API. 
        You can enter your API key to fetch articles based on your search keywords. 
        Your API key will be saved in the current session.
        """)
    else:
        st.session_state.page = menu_options[selection]
        st.experimental_rerun()
