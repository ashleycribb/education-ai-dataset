import streamlit as st
import sys
import os
import pandas as pd # Ensure pandas is imported

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_student_lo_interaction_summary, get_unique_student_ids
except ImportError:
    st.error("Could not import DashboardDataManager. Critical error.")
    # Fallback dummy functions
    def load_xapi_statements(filepath=""): return []
    def get_student_lo_interaction_summary(statements, student_id): return pd.DataFrame(columns=["Learning Objective ID", "Interaction Count", "Last Interaction Date"])
    def get_unique_student_ids(statements): return []


st.set_page_config(page_title="Student LO Progress", layout="wide")
st.title("Student Learning Objective Interaction (Prototype)")

statements = load_xapi_statements()

if statements:
    student_ids = get_unique_student_ids(statements)
    if not student_ids:
        st.warning("No student IDs found in the loaded data.")
    else:
        selected_student_id = st.selectbox("Select a Student ID:", options=student_ids, index=0 if student_ids else None)

        if selected_student_id:
            st.subheader(f"LO Interaction Summary for Student: {selected_student_id}")
            progress_data = get_student_lo_interaction_summary(statements, selected_student_id) # Pass statements

            if not progress_data.empty:
                st.dataframe(progress_data, use_container_width=True)
            else:
                st.info(f"No Learning Objective interaction data found for student: {selected_student_id}")
        # Removed the "Please select a student" else block as selectbox always has a value if options exist.
        elif student_ids : # Only show if student_ids were available but none selected (should not happen with default index=0)
             st.info("Please select a student to view their LO interaction summary.")

else:
    st.warning("No xAPI statements loaded. Cannot display student progress.")
    st.info("Ensure `xapi_statements.jsonl` is present or check data loading functions in `dashboard_data_manager.py`.")
