import streamlit as st
import sys
import os
import pandas as pd # Ensure pandas is imported

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, analyze_misconceptions
except ImportError:
    st.error("Could not import DashboardDataManager. Critical error.")
    # Fallback dummy functions if import fails, to allow app to run somewhat
    def load_xapi_statements(filepath=""): return []
    def analyze_misconceptions(statements, selected_lo=None): return pd.DataFrame(columns=["Misconception Pattern", "Frequency", "Example Session IDs"])


st.set_page_config(page_title="Misconception Analysis", layout="wide")
st.title("Misconception Analysis Prototype")

statements = load_xapi_statements()

if statements:
    available_los_for_misconceptions = ["RC.4.LO1.MainIdea.Narrative", "MATH.5.NF.A.1 (Placeholder)", "ECO.7.LO.FoodWeb (Placeholder)"]
    selected_lo = st.selectbox(
        "Select a Learning Objective to analyze for misconceptions:",
        options=available_los_for_misconceptions,
        index=0
    )

    if selected_lo:
        misconception_data = analyze_misconceptions(statements, selected_lo) # Pass statements

        if not misconception_data.empty:
            st.subheader(f"Common Misconception Patterns for LO: {selected_lo}")
            st.dataframe(misconception_data, use_container_width=True)
        else:
            st.info(f"No (mock) misconception data currently available for LO: {selected_lo}")
    else:
        st.info("Please select a Learning Objective to view potential misconception patterns.")
else:
    st.warning("No xAPI statements loaded. Cannot perform misconception analysis.")
    st.info("Ensure `xapi_statements.jsonl` is present or check data loading functions in `dashboard_data_manager.py`.")
