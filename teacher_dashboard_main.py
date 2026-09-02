import streamlit as st
# No direct data loading needed in the main app runner for V2 multi-page structure
# Individual pages will call cached functions from dashboard_data_manager.py

st.set_page_config(
    page_title="AITA Teacher Dashboard V2",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar branding/title (optional but nice)
st.sidebar.title("AITA Dashboard V2")
# Placeholder for a logo or branding image in the sidebar
# st.sidebar.image("path/to/your/logo.png", width=100)
# Example using a generic link for testing if an actual image isn't available:
# st.sidebar.image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", width=100)


# Main landing page content
st.title("Welcome to the AITA Teacher Dashboard V2")
st.markdown("""
This dashboard provides insights into student interactions with AI Tutors (AITAs).
Use the sidebar to navigate to different views:

*   **Overview Dashboard**: See a summary of recent sessions and filter by student or date.
*   **Session Transcript View**: Dive into detailed dialogue transcripts for specific sessions, including pedagogical notes and AITA's reasoning.
*   **Misconception Analysis**: (Prototype) View common (mock) misconception patterns for selected Learning Objectives.
*   **Student LO Progress**: (Prototype) See a summary of a student's interactions per Learning Objective.

All data is loaded from `xapi_statements.jsonl`. If the file is not found, placeholder data is used for demonstration.
""")

st.info("Select a page from the navigation sidebar to begin.")

# Note: Streamlit automatically creates navigation in the sidebar
# for files placed in a 'pages/' subdirectory (e.g., 'pages/01_Overview_Dashboard.py').
# The numerical prefix in filenames (01_, 02_) helps control the order.
