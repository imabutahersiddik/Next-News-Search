def get_styles():
    return """
    <style>
    /* General body styles */
    body {
        background-color: #f0f4f8;
        color: #333;
        font-family: 'Arial', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
    }

    /* Title styles */
    .stTitle {
        font-size: 2.5em;
        color: #4CAF50;
        font-weight: bold;
        margin-bottom: 20px;
    }

    /* Search form styles */
    .search-container {
        position: relative;
        width: 100%;
        max-width: 600px;
        margin-bottom: 20px;
    }

    /* Input styles */
    .search-input {
        width: 100%;
        padding: 15px 45px 15px 15px; /* Right padding for icon */
        border: 2px solid #4CAF50;
        border-radius: 5px;
        font-size: 1.2em;
    }

    /* Icon styles */
    .search-icon {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        width: 24px; /* Adjust size as needed */
        height: 24px; /* Adjust size as needed */
    }

    /* Expander styles */
    .stExpander {
        background-color: #e8f5e9;
        border-radius: 5px;
        padding: 10px;
    }

    /* Checkbox styles */
    .stCheckbox {
        margin-bottom: 20px;
    }

    /* Footer styles */
    .stFooter {
        text-align: center;
        padding: 20px;
        font-size: 0.8em;
        color: #777;
    }
    </style>
    """
