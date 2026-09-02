import streamlit as st
import pandas as pd
import datetime
from typing import Optional, List, Dict, Any
import sys
import os

# Ensure dashboard_data_manager can be imported from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_session_summaries
except ImportError:
    # This fallback might be needed if the script is run in a way that sys.path modification doesn't work as expected
    # Or if dashboard_data_manager is not in the parent directory.
    # For this project structure, the sys.path.append should work.
    st.error("Could not import DashboardDataManager. Please ensure it's in the correct path.")
    # Provide dummy functions so the rest of the page can at least render without crashing immediately
    def load_xapi_statements(filepath=""): return []
    def get_session_summaries(statements): return []

st.set_page_config(page_title="Session Overview", layout="wide")
st.title("Session Overview & Filters")

# Load data using the centralized data manager function
# This relies on @st.cache_data within dashboard_data_manager.py
statements = load_xapi_statements() # Default filepath is used here

if not statements:
    st.warning("No xAPI statements loaded. Overview cannot be displayed. Ensure `xapi_statements.jsonl` exists or check data loading in `dashboard_data_manager.py`.")
    st.stop()

# Get all session summaries first for filter population
all_session_summaries = get_session_summaries(statements)
if not all_session_summaries:
    st.info("No sessions found in the loaded data. The log file might be empty or contain no processable sessions.")
    st.stop()

# Filters in the main area for this page
st.header("Filters")
col1_filter, col2_filter = st.columns(2)

with col1_filter:
    all_student_ids = sorted(list(set(s["student_id"] for s in all_session_summaries if s["student_id"] != "Unknown Student")))
    filter_student_id_options = ["All Students"] + all_student_ids

    selected_student_filter_option = st.selectbox(
        "Filter by Student ID:",
        options=filter_student_id_options,
        index=0
    )
    filter_student_id = ""
    if selected_student_filter_option != "All Students":
        filter_student_id = selected_student_filter_option.strip()


with col2_filter:
    filter_date_val: Optional[datetime.date] = st.date_input(
        "Filter by Date (shows sessions from this date):",
        value=None, # Changed from None to allow no default selection
        key="overview_date_picker"
    )

# Apply filters
session_summaries_for_display = all_session_summaries
if filter_student_id: # Only filter if a student ID is selected
    session_summaries_for_display = [
        s for s in session_summaries_for_display if s["student_id"].lower() == filter_student_id.lower()
    ]
if filter_date_val:
    filter_date_str = filter_date_val.isoformat()
    session_summaries_for_display = [
        s for s in session_summaries_for_display if s.get("start_timestamp", "").startswith(filter_date_str)
    ]

st.divider()
st.header("Filtered Session Overview")

# Aggregate Stats
col1_agg, col2_agg, col3_agg = st.columns(3)
col1_agg.metric("Total Sessions Displayed", len(session_summaries_for_display))
total_turns_displayed = sum(s.get('turn_count', 0) for s in session_summaries_for_display) # Added .get for safety
col2_agg.metric("Total Interaction Turns (in displayed sessions)", total_turns_displayed)
total_flagged_inputs = sum(s.get('flagged_input_count', 0) for s in session_summaries_for_display)
col3_agg.metric("Total Flagged Inputs (in displayed sessions)", total_flagged_inputs)


if not session_summaries_for_display:
    st.info("No sessions match the current filter criteria.")
else:
    overview_data = [{
        "Session ID": s.get("session_id", "N/A"),
        "Student ID": s.get("student_id", "N/A"),
        "Start Time (UTC)": s.get("start_timestamp", "N/A"),
        "Turn Count": s.get("turn_count", 0),
        "Flagged Inputs": s.get("flagged_input_count", 0),
        "Flagged Outputs": s.get("flagged_output_count", 0),
        "First User Utterance": (s.get("first_user_utterance", "")[:100] + "..." if len(s.get("first_user_utterance", "")) > 100 else s.get("first_user_utterance", ""))
    } for s in session_summaries_for_display]

    st.dataframe(pd.DataFrame(overview_data), use_container_width=True,
                 column_config={
                     "Session ID": st.column_config.TextColumn(width="small"),
                     "Student ID": st.column_config.TextColumn(width="small"),
                     "Turn Count": st.column_config.NumberColumn(width="small"),
                     "Flagged Inputs": st.column_config.NumberColumn(width="small"),
                     "Flagged Outputs": st.column_config.NumberColumn(width="small"),
                 })
