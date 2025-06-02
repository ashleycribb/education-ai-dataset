import streamlit as st
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime # Required for date comparisons if any
import os # For checking if file exists

# --- Placeholder Data (if xapi_statements.jsonl not found) ---
PLACEHOLDER_XAPI_STATEMENTS_CONTENT_FOR_MANAGER = """
{"id": "uuid1_turn1", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What is the story about?"}}}, "result": {"response": "AITA: It's about a little kitten named Lily who gets lost. What else happens in the story?", "duration": "PT10.50S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.1}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.05}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What is the story about?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:05Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid1_turn2_input_flagged", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/2", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "This is stupid and I hate it."}}}, "result": {"response": "AITA: I'm sorry, I can't process that request. Let's stick to our reading task or try phrasing it differently.", "duration": "PT0.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": false, "flagged_categories": ["insult", "toxic"], "scores": {"insult": 0.85, "toxic": 0.92}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": ""}}, "timestamp": "2024-07-31T10:00:15Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid2_turn1_output_flagged", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student002"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session2/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Why Leaves Change Color' on LO: RC.4.LO.Vocabulary"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What does pigment mean?", "http://example.com/xapi/extensions/aita_response_raw": "A pigment is like, you know, the stuff that makes things colored, sometimes it's kinda gross stuff."}}}, "result": {"response": "AITA: I was about to say something that might not be quite right for our lesson. Let's try a different way! How about you tell me what you found most interesting in the text?", "duration": "PT12.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.03}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": false, "flagged_categories": ["potentially_inappropriate_language"], "scores": {"inappropriate": 0.88, "toxic": 0.5}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_leaves_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session2", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO.Vocabulary", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What does pigment mean?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:05:00Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
"""

@st.cache_data # Cache the raw data loading
def load_xapi_statements(filepath: str = "xapi_statements.jsonl") -> List[Dict[str, Any]]:
    """Loads statements from the JSON Lines file. Uses @st.cache_data for caching."""
    statements = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    statements.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"WARNING: Skipping malformed line {line_number} in {filepath}: {e}")
        if not statements and os.path.exists(filepath) and os.path.getsize(filepath) > 0: 
             print(f"WARNING: Log file '{filepath}' was not empty but contained no valid JSON lines. Using placeholder data.")
             raise FileNotFoundError 
        elif not statements and not os.path.exists(filepath): # File doesn't exist
             raise FileNotFoundError # Trigger fallback
        return statements
    except FileNotFoundError:
        print(f"WARNING: Log file '{filepath}' not found or was effectively empty. Using placeholder data for demonstration.")
        placeholder_lines = PLACEHOLDER_XAPI_STATEMENTS_CONTENT_FOR_MANAGER.strip().split('\n')
        for line_number, line in enumerate(placeholder_lines, 1):
            try:
                statements.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARNING: Skipping malformed placeholder line {line_number}: {e}")
        return statements
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while loading {filepath}: {e}")
        return []

@st.cache_data
def get_session_summaries(_all_statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processes statements to identify unique sessions and summarize them."""
    sessions: Dict[str, Dict[str, Any]] = {}
    for i, stmt in enumerate(_all_statements):
        # Robust session_id extraction
        session_id_path = stmt.get("context", {}).get("extensions", {})
        session_id = session_id_path.get("http://example.com/xapi/extensions/session_id", f"unknown_session_stmt{i}") if isinstance(session_id_path, dict) else f"unknown_session_stmt{i}"
        
        # Robust student_id extraction
        actor_account = stmt.get("actor", {}).get("account", {})
        student_id = actor_account.get("name", "Unknown Student") if isinstance(actor_account, dict) else "Unknown Student"

        if session_id not in sessions:
            sessions[session_id] = {
                "session_id": session_id, "student_id": student_id,
                "start_timestamp": stmt.get("timestamp", "N/A"), "turn_count": 0,
                "first_user_utterance": "N/A", "flagged_input_count": 0, "flagged_output_count": 0
            }
        
        sessions[session_id]["turn_count"] += 1
        current_stmt_timestamp = stmt.get("timestamp", "N/A")
        if current_stmt_timestamp != "N/A" and \
           (sessions[session_id]["start_timestamp"] == "N/A" or \
            current_stmt_timestamp < sessions[session_id]["start_timestamp"]):
             sessions[session_id]["start_timestamp"] = current_stmt_timestamp

        user_utterance_key = "http://example.com/xapi/extensions/user_utterance_raw"
        object_def_ext = stmt.get("object", {}).get("definition", {}).get("extensions", {})
        if isinstance(object_def_ext, dict) and sessions[session_id]["first_user_utterance"] == "N/A" and \
           object_def_ext.get(user_utterance_key):
            sessions[session_id]["first_user_utterance"] = object_def_ext[user_utterance_key]
        
        result_ext = stmt.get("result", {}).get("extensions", {})
        if isinstance(result_ext, dict):
            input_mod_key = "http://example.com/xapi/extensions/input_moderation_details"
            input_mod = result_ext.get(input_mod_key, {})
            if isinstance(input_mod, dict) and input_mod.get("is_safe") is False: 
                sessions[session_id]["flagged_input_count"] += 1
                
            output_mod_key = "http://example.com/xapi/extensions/output_moderation_details"
            output_mod = result_ext.get(output_mod_key, {})
            if isinstance(output_mod, dict) and output_mod.get("is_safe") is False: 
                sessions[session_id]["flagged_output_count"] += 1
            
    return sorted(sessions.values(), key=lambda s: s.get("start_timestamp", ""), reverse=True)

@st.cache_data
def get_turns_for_session(_all_statements: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
    """Filters and formats statements for a given session's dialogue display."""
    session_statements = [s for s in _all_statements if s.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/session_id") == session_id]
    dialogue_turns = []
    for stmt in session_statements:
        result_extensions = stmt.get("result", {}).get("extensions", {})
        input_moderation = result_extensions.get("http://example.com/xapi/extensions/input_moderation_details") if isinstance(result_extensions, dict) else None
        output_moderation = result_extensions.get("http://example.com/xapi/extensions/output_moderation_details") if isinstance(result_extensions, dict) else None
        
        object_definition_extensions = stmt.get("object",{}).get("definition",{}).get("extensions",{})
        user_utterance = object_definition_extensions.get("http://example.com/xapi/extensions/user_utterance_raw") if isinstance(object_definition_extensions, dict) else None
        aita_raw_response = object_definition_extensions.get("http://example.com/xapi/extensions/aita_response_raw") if isinstance(object_definition_extensions, dict) else None
        
        context_extensions = stmt.get("context",{}).get("extensions",{})
        full_llm_prompt = context_extensions.get("http://example.com/xapi/extensions/full_prompt_to_llm") if isinstance(context_extensions, dict) else None
        aita_persona = context_extensions.get("http://example.com/xapi/extensions/aita_persona", "N/A") if isinstance(context_extensions, dict) else "N/A"
        active_lo = context_extensions.get("http://example.com/xapi/extensions/learning_objective_active", "N/A") if isinstance(context_extensions, dict) else "N/A"
        
        parent_activity_list = stmt.get("context", {}).get("contextActivities", {}).get("parent", [])
        content_item_id = parent_activity_list[0].get("id", "N/A") if parent_activity_list and isinstance(parent_activity_list, list) and len(parent_activity_list)>0 and isinstance(parent_activity_list[0], dict) else "N/A"

        turn_data: Dict[str, Any] = {
            "timestamp": stmt.get("timestamp", "N/A"), "speaker": "Unknown", "utterance": "N/A",
            "input_moderation": input_moderation if isinstance(input_moderation, dict) else None,
            "output_moderation": output_moderation if isinstance(output_moderation, dict) else None,
            "raw_llm_response": aita_raw_response,
            "full_llm_prompt": full_llm_prompt,
            "aita_persona": aita_persona,
            "active_lo": active_lo,
            "content_item_id": content_item_id
        }
        
        aita_response = stmt.get("result", {}).get("response")
        if user_utterance: 
            turn_data["speaker"] = "user"; turn_data["utterance"] = user_utterance
        elif aita_response: 
            turn_data["speaker"] = "assistant"; turn_data["utterance"] = aita_response
        
        dialogue_turns.append(turn_data)
    return sorted(dialogue_turns, key=lambda t: t.get("timestamp", ""))

@st.cache_data
def analyze_misconceptions(_all_statements: List[Dict[str, Any]], selected_lo: Optional[str] = None) -> pd.DataFrame:
    if selected_lo == "RC.4.LO1.MainIdea.Narrative": 
        mock_data = [
            {"Misconception Pattern": "Student provides a detail instead of main idea", "Frequency": 8, "Example Session IDs": "session1, session_abc (mock)"},
            {"Misconception Pattern": "Student summarizes only part of the text (e.g., only beginning or end)", "Frequency": 4, "Example Session IDs": "session2 (mock)"},
            {"Misconception Pattern": "Confuses character actions with the overall message", "Frequency": 2, "Example Session IDs": "session_xyz (mock)"}
        ]
        return pd.DataFrame(mock_data)
    return pd.DataFrame(columns=["Misconception Pattern", "Frequency", "Example Session IDs"])

@st.cache_data
def get_student_lo_interaction_summary(_all_statements: List[Dict[str, Any]], student_id: str) -> pd.DataFrame:
    student_statements = [s for s in _all_statements if s.get("actor", {}).get("account", {}).get("name") == student_id]
    lo_interactions: Dict[str, Dict[str, Any]] = {}
    
    for stmt in student_statements:
        context_ext = stmt.get("context", {}).get("extensions", {})
        lo_id = context_ext.get("http://example.com/xapi/extensions/learning_objective_active") if isinstance(context_ext, dict) else None
        timestamp = stmt.get("timestamp", "")
        
        if not lo_id or lo_id == "N/A": continue
            
        if lo_id not in lo_interactions:
            lo_interactions[lo_id] = {"Learning Objective ID": lo_id, "Interaction Count": 0, "Last Interaction Date": "N/A"}
        
        lo_interactions[lo_id]["Interaction Count"] += 1
        if timestamp and (lo_interactions[lo_id]["Last Interaction Date"] == "N/A" or timestamp > lo_interactions[lo_id]["Last Interaction Date"]):
            lo_interactions[lo_id]["Last Interaction Date"] = timestamp
            
    if not lo_interactions:
        return pd.DataFrame(columns=["Learning Objective ID", "Interaction Count", "Last Interaction Date"])
        
    return pd.DataFrame(list(lo_interactions.values()))

@st.cache_data
def get_unique_student_ids(_all_statements: List[Dict[str, Any]]) -> List[str]:
    """Extracts and returns a sorted list of unique student IDs."""
    student_ids = set()
    for stmt in _all_statements:
        actor_account = stmt.get("actor", {}).get("account", {})
        if isinstance(actor_account, dict):
            student_id = actor_account.get("name")
            if student_id and student_id != "Unknown Student":
                student_ids.add(student_id)
    return sorted(list(student_ids))

```
The `pages/` directory was confirmed to be created in the previous turn.

**Step 3: Create `pages/03_Misconception_Analysis.py`**
```python
# pages/03_Misconception_Analysis.py
import streamlit as st
import sys
import os # For path manipulation
# Add parent directory to path to import dashboard_data_manager
# This assumes pages/ is a subdirectory of where teacher_dashboard_main.py and dashboard_data_manager.py are
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, analyze_misconceptions
except ImportError:
    # Fallback for environments where path manipulation might be tricky or for direct execution
    # This assumes dashboard_data_manager.py is in the same directory if the above fails.
    # This is less robust than setting PYTHONPATH or packaging properly.
    from dashboard_data_manager import load_xapi_statements, analyze_misconceptions


st.set_page_config(page_title="Misconception Analysis", layout="wide")
st.title("Misconception Analysis Prototype")

# Ensure data is loaded (using the cached function from data_manager)
# The file path for xapi_statements.jsonl is hardcoded in load_xapi_statements
# or can be passed as an argument if that function is modified.
statements = load_xapi_statements() 

if statements:
    # For prototype, use a hardcoded list of LOs that might have misconception data
    # In a real app, these could be dynamically populated from the data or a config
    available_los_for_misconceptions = ["RC.4.LO1.MainIdea.Narrative", "MATH.5.NF.A.1 (Placeholder)", "ECO.7.LO.FoodWeb (Placeholder)"]
    selected_lo = st.selectbox(
        "Select a Learning Objective to analyze for misconceptions:", 
        options=available_los_for_misconceptions,
        index=0 # Default to the first option
    )

    if selected_lo:
        # Pass all statements to the analysis function; it will filter or process as needed.
        misconception_data = analyze_misconceptions(statements, selected_lo)
        
        if not misconception_data.empty:
            st.subheader(f"Common Misconception Patterns for LO: {selected_lo}")
            st.dataframe(misconception_data, use_container_width=True)
        else:
            st.info(f"No (mock) misconception data currently available for LO: {selected_lo}")
    else:
        st.info("Please select a Learning Objective to view potential misconception patterns.")
else:
    st.warning("No xAPI statements loaded. Cannot perform misconception analysis.")
    st.info("Ensure `xapi_statements.jsonl` is present or check data loading functions.")

```

**Step 4: Create `pages/04_Student_LO_Progress.py`**
```python
# pages/04_Student_LO_Progress.py
import streamlit as st
import sys
import os # For path manipulation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_student_lo_interaction_summary, get_unique_student_ids
except ImportError:
    from dashboard_data_manager import load_xapi_statements, get_student_lo_interaction_summary, get_unique_student_ids


st.set_page_config(page_title="Student LO Progress", layout="wide")
st.title("Student Learning Objective Interaction (Prototype)")

statements = load_xapi_statements()

if statements:
    student_ids = get_unique_student_ids(statements)
    if not student_ids:
        st.warning("No student IDs found in the loaded data.")
    else:
        selected_student_id = st.selectbox("Select a Student ID:", options=student_ids)
        
        if selected_student_id:
            st.subheader(f"LO Interaction Summary for Student: {selected_student_id}")
            # Pass all statements to the summary function; it will filter by student_id.
            progress_data = get_student_lo_interaction_summary(statements, selected_student_id)
            
            if not progress_data.empty:
                st.dataframe(progress_data, use_container_width=True)
            else:
                st.info(f"No Learning Objective interaction data found for student: {selected_student_id}")
        else:
            st.info("Please select a student to view their LO interaction summary.")
else:
    st.warning("No xAPI statements loaded. Cannot display student progress.")
    st.info("Ensure `xapi_statements.jsonl` is present or check data loading functions.")

```

**Step 5: Create/Update `teacher_dashboard_main.py`**
This involves renaming `teacher_dashboard_prototype.py` to `teacher_dashboard_main.py` and making it minimal.
First, I'll rename the old file.
Then, I'll overwrite `teacher_dashboard_main.py` with the new minimal content.

```python
# teacher_dashboard_main.py
import streamlit as st
# Ensure dashboard_data_manager can be imported.
# If dashboard_data_manager.py is in the same directory, this is fine.
# If pages/ scripts need it, they use sys.path.append as shown.
# from dashboard_data_manager import load_xapi_statements 

st.set_page_config(
    page_title="AITA Teacher Dashboard V2", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.sidebar.title("AITA Dashboard V2") 
st.sidebar.image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", width=100) # Placeholder image

# The main app runner (this script) doesn't need to load all data itself
# if each page calls the cached data loading functions from dashboard_data_manager.
# This keeps the main app script clean and focused on overall setup.
# The @st.cache_data decorator in dashboard_data_manager.py handles the caching.

st.title("Welcome to the AITA Teacher Dashboard V2")
st.markdown("""
This dashboard provides insights into student interactions with AI Tutors (AITAs). 
Use the sidebar to navigate to different views:

*   **Overview Dashboard**: See a summary of recent sessions and filter by student or date.
*   **Session Transcript View**: Dive into detailed dialogue transcripts for specific sessions.
*   **Misconception Analysis**: (Prototype) View common misconceptions for selected Learning Objectives.
*   **Student LO Progress**: (Prototype) See a summary of a student's interactions per Learning Objective.

All data is loaded from `xapi_statements.jsonl`. If the file is not found, placeholder data is used for demonstration.
""")

st.info("Select a page from the navigation sidebar to begin.")

```

**Step 6 & 7 (Adapting original prototype into pages)**
Now, I need to get the content of the original `teacher_dashboard_prototype.py` (from Turn 63, which I have from the last `read_files` call) and adapt its relevant parts into `pages/01_Overview_Dashboard.py` and `pages/02_Session_Transcript_View.py`.

**Step 6: Create `pages/01_Overview_Dashboard.py`**
```python
# pages/01_Overview_Dashboard.py
import streamlit as st
import pandas as pd
import datetime
from typing import Optional, List, Dict, Any # Added for type hints consistency
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_session_summaries
except ImportError:
    from dashboard_data_manager import load_xapi_statements, get_session_summaries

st.set_page_config(page_title="Session Overview", layout="wide") # Each page can set its own title
st.title("Session Overview & Filters")

# Load data using the centralized data manager function
# This relies on @st.cache_data within dashboard_data_manager.py
statements = load_xapi_statements()

if not statements:
    st.warning("No xAPI statements loaded. Overview cannot be displayed.")
    st.stop()

# Get all session summaries first for filter population
all_session_summaries = get_session_summaries(statements)
if not all_session_summaries:
    st.info("No sessions found in the loaded data.")
    st.stop()

# Filters in the main area for this page, or could be in sidebar if preferred for all pages
st.header("Filters")
col1_filter, col2_filter = st.columns(2)

with col1_filter:
    # Populate student ID options from all sessions
    all_student_ids = sorted(list(set(s["student_id"] for s in all_session_summaries if s["student_id"] != "Unknown Student")))
    filter_student_id = st.selectbox(
        "Filter by Student ID:", 
        options=["All Students"] + all_student_ids, 
        index=0
    ).strip()
    if filter_student_id == "All Students":
        filter_student_id = "" # Clear filter

with col2_filter:
    filter_date_val: Optional[datetime.date] = st.date_input(
        "Filter by Date (shows sessions from this date):", 
        value=None,
        key="overview_date_picker"
    )

# Apply filters
session_summaries_for_display = all_session_summaries
if filter_student_id:
    session_summaries_for_display = [
        s for s in session_summaries_for_display if s["student_id"].lower() == filter_student_id.lower()
    ]
if filter_date_val:
    filter_date_str = filter_date_val.isoformat()
    session_summaries_for_display = [
        s for s in session_summaries_for_display if s["start_timestamp"].startswith(filter_date_str)
    ]

st.divider()
st.header("Filtered Session Overview")

# Aggregate Stats
col1_agg, col2_agg, col3_agg = st.columns(3)
col1_agg.metric("Total Sessions Displayed", len(session_summaries_for_display))
total_turns_displayed = sum(s['turn_count'] for s in session_summaries_for_display)
col2_agg.metric("Total Interaction Turns (in displayed sessions)", total_turns_displayed)
total_flagged_inputs = sum(s.get('flagged_input_count', 0) for s in session_summaries_for_display)
col3_agg.metric("Total Flagged Inputs (in displayed sessions)", total_flagged_inputs)


if not session_summaries_for_display:
    st.info("No sessions match the current filter criteria.")
else:
    overview_data = [{
        "Session ID": s["session_id"],
        "Student ID": s["student_id"],
        "Start Time (UTC)": s["start_timestamp"],
        "Turn Count": s["turn_count"],
        "Flagged Inputs": s.get("flagged_input_count", 0),
        "Flagged Outputs": s.get("flagged_output_count", 0),
        "First User Utterance": s["first_user_utterance"][:100] + "..." if len(s["first_user_utterance"]) > 100 else s["first_user_utterance"]
    } for s in session_summaries_for_display]
    
    st.dataframe(pd.DataFrame(overview_data), use_container_width=True,
                 column_config={
                     "Session ID": st.column_config.TextColumn(width="small"),
                     "Student ID": st.column_config.TextColumn(width="small"),
                     "Turn Count": st.column_config.NumberColumn(width="small"),
                     "Flagged Inputs": st.column_config.NumberColumn(width="small"),
                     "Flagged Outputs": st.column_config.NumberColumn(width="small"),
                 })

```

**Step 7: Create `pages/02_Session_Transcript_View.py`**
```python
# pages/02_Session_Transcript_View.py
import streamlit as st
from typing import Optional, List, Dict, Any # Added for type hints consistency
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_turns_for_session, get_session_summaries # Need summaries for selectbox
except ImportError:
    from dashboard_data_manager import load_xapi_statements, get_turns_for_session, get_session_summaries


st.set_page_config(page_title="Session Transcript", layout="wide")
st.title("Session Transcript Viewer")

statements = load_xapi_statements()

if not statements:
    st.warning("No xAPI statements loaded. Transcript view cannot be displayed.")
    st.stop()

all_session_summaries = get_session_summaries(statements) # Get all summaries for the selectbox

if not all_session_summaries:
    st.info("No sessions found in the loaded data.")
    st.stop()

# Session selection in the main area for this page
formatted_session_options = [
    f"{s['session_id']} (Student: {s['student_id']}, Time: {s['start_timestamp']})" for s in all_session_summaries
]
option_to_id_map = {formatted_options: summary["session_id"] for formatted_options, summary in zip(formatted_session_options, all_session_summaries)}

selected_formatted_option = st.selectbox(
    "Select a Session to view its transcript:",
    options=formatted_session_options,
    index=0 if formatted_session_options else None
)

if selected_formatted_option:
    selected_session_id = option_to_id_map[selected_formatted_option]
    
    # Extract session-level context for display
    current_session_info = next((s for s in all_session_summaries if s["session_id"] == selected_session_id), None)
    student_id_display = current_session_info["student_id"] if current_session_info else "N/A"
    
    dialogue_turns = get_turns_for_session(statements, selected_session_id)

    # Extract AITA persona, LO, Content ID from the first relevant turn
    aita_persona_display = "N/A"
    active_lo_display = "N/A"
    content_item_id_display = "N/A"
    first_relevant_turn_data = dialogue_turns[0] if dialogue_turns else None # Use first turn as proxy for session context

    if first_relevant_turn_data:
        aita_persona_display = first_relevant_turn_data.get("aita_persona", "N/A")
        active_lo_display = first_relevant_turn_data.get("active_lo", "N/A")
        content_item_id_display = first_relevant_turn_data.get("content_item_id", "N/A")

    st.header(f"Dialogue Transcript: Session {selected_session_id}")
    st.markdown(f"""
    **Student ID:** `{student_id_display}`  
    **AITA Persona:** `{aita_persona_display}`  
    **Active Learning Objective:** `{active_lo_display}`  
    **Content Item ID:** `{content_item_id_display}`
    """)
    st.divider()

    if not dialogue_turns:
        st.warning("No dialogue turns found for this session.")
    else:
        for turn in dialogue_turns:
            role = turn["speaker"] if turn["speaker"] in ["user", "assistant"] else "assistant"
            with st.chat_message(name=role): # Use role for chat_message avatar
                # Display speaker role explicitly if it's not 'user' or 'assistant', or for clarity
                speaker_display_name = turn['speaker'].capitalize()
                st.markdown(f"**{speaker_display_name}** (at {turn['timestamp']}):")
                st.markdown(turn["utterance"])

                if turn["input_moderation"]:
                    mod_details = turn["input_moderation"]
                    if isinstance(mod_details, dict) and not mod_details.get("is_safe", True):
                        st.error(f"⚠️ Input flagged! Categories: {mod_details.get('flagged_categories', [])}")
                    with st.expander("Input Moderation Details", expanded=False):
                        st.json(mod_details)
                
                if turn["output_moderation"] and role == "assistant":
                    mod_details = turn["output_moderation"]
                    if isinstance(mod_details, dict) and not mod_details.get("is_safe", True):
                        st.warning(f"⚠️ AITA output was moderated/replaced! Original flagged: {mod_details.get('flagged_categories', [])}")
                    with st.expander("Output Moderation Details (AITA Raw)", expanded=False):
                        st.json(mod_details)
                        if turn["raw_llm_response"] and turn["raw_llm_response"] != turn["utterance"]:
                            st.text_area("Original LLM Response (before safeguard override):", value=turn["raw_llm_response"], height=100, disabled=True)
                
                if role == "assistant" and turn["full_llm_prompt"]:
                    with st.expander("Full Prompt to LLM (for this AITA turn)", expanded=False):
                        st.text_area("Prompt:", value=turn["full_llm_prompt"], height=150, disabled=True)
else:
    st.info("Please select a session from the dropdown to view its transcript.")

```
This multi-step approach should correctly set up the new dashboard structure. I've refined the data manager functions slightly for robustness and ensured the page scripts correctly import and use them. The `sys.path.append` is a common way to handle imports from a parent directory in Streamlit multi-page apps when not using a formal package structure.I have already completed the main parts of this task in the previous extended turn (Turn 75), where I created `dashboard_data_manager.py`, the `pages/` directory, `pages/03_Misconception_Analysis.py`, `pages/04_Student_LO_Progress.py`, the minimal `teacher_dashboard_main.py`, and then `pages/01_Overview_Dashboard.py` and `pages/02_Session_Transcript_View.py` by adapting the original prototype logic.

**Summary of actions from Turn 75 that fulfill this subtask's requirements:**

1.  **`dashboard_data_manager.py` Created and Implemented**:
    *   Imports: `streamlit as st`, `json`, `pandas as pd`, `typing`, `datetime`.
    *   `load_xapi_statements`: Implemented with `@st.cache_data`, loads from file or placeholder.
    *   `get_session_summaries`: Implemented with `@st.cache_data`, processes statements into summaries (including robust extraction and new fields like `flagged_input_count`, `flagged_output_count`).
    *   `get_turns_for_session`: Implemented with `@st.cache_data`, formats turns for a specific session (including robust extraction of moderation details and context).
    *   **New Function `analyze_misconceptions`**: Implemented with `@st.cache_data`. Returns mock Pandas DataFrame for "RC.4.LO1.MainIdea.Narrative" and an empty DataFrame otherwise.
    *   **New Function `get_student_lo_interaction_summary`**: Implemented with `@st.cache_data`. Filters statements by `student_id`, groups by `learning_objective_active`, counts interactions, finds the last interaction date, and returns a Pandas DataFrame.
    *   **New Function `get_unique_student_ids`**: Implemented with `@st.cache_data` to extract unique student IDs.

2.  **`pages/` Directory Created**: The `mkdir -p pages` command was executed.

3.  **`pages/03_Misconception_Analysis.py` Created**:
    *   Imports `streamlit as st` and necessary functions from `dashboard_data_manager`.
    *   Sets page config and title.
    *   Loads statements using `load_xapi_statements()`.
    *   Provides a `st.selectbox` for LO selection (with hardcoded options for demo).
    *   Calls `analyze_misconceptions()` and displays the resulting DataFrame or an info message.

4.  **`pages/04_Student_LO_Progress.py` Created**:
    *   Imports `streamlit as st` and necessary functions from `dashboard_data_manager`.
    *   Sets page config and title.
    *   Loads statements.
    *   Uses `get_unique_student_ids()` to populate a student selection `st.selectbox`.
    *   Calls `get_student_lo_interaction_summary()` for the selected student.
    *   Displays the resulting DataFrame or an info message.

5.  **`teacher_dashboard_main.py` Created (by modifying `teacher_dashboard_prototype.py`)**:
    *   The script `teacher_dashboard_main.py` was created to be minimal, setting the main page config, title, and a welcome message.
    *   It relies on Streamlit's multi-page app feature to create sidebar navigation from files in the `pages/` directory.
    *   It correctly assumes that data loading via `@st.cache_data` in `dashboard_data_manager.py` will be handled efficiently when called from individual page scripts.

6.  **`pages/01_Overview_Dashboard.py` and `pages/02_Session_Transcript_View.py` Created**:
    *   These files were created by adapting the logic from the original `teacher_dashboard_prototype.py`.
    *   `01_Overview_Dashboard.py` handles the display of session summaries, including filters for student ID and date, and aggregate statistics.
    *   `02_Session_Transcript_View.py` handles the display of detailed session transcripts, including selection of a session and rendering of dialogue turns with moderation details in expanders.

All specified components and functionalities for this subtask have been implemented in the previous turn. The `sys.path.append` logic was included in the page scripts for robust importing of the `dashboard_data_manager`. The placeholder data in `dashboard_data_manager.py` was also updated to include examples of flagged moderation for testing.

No further file modifications are needed for this subtask based on the plan.
