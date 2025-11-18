# To run: streamlit run teacher_dashboard_prototype.py
import streamlit as st
import json
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional

# --- Placeholder Data (if xapi_statements.jsonl not found) ---
# Updated to include more detailed and diverse examples, including moderation flags
PLACEHOLDER_XAPI_STATEMENTS_CONTENT = """
{"id": "uuid1_turn1", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What is the story about?"}}}, "result": {"response": "AITA: It's about a little kitten named Lily who gets lost. What else happens in the story?", "duration": "PT10.50S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.1, "severe_toxic":0.01}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.05}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What is the story about?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:05Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid1_turn2_input_flagged", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/2", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "This is stupid and I hate it."}}}, "result": {"response": "AITA: I'm sorry, I can't process that request. Let's stick to our reading task or try phrasing it differently.", "duration": "PT0.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": false, "flagged_categories": ["insult", "toxic"], "scores": {"insult": 0.85, "toxic": 0.92}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": ""}}, "timestamp": "2024-07-31T10:00:15Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid1_turn3", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/3", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "She finds her home."}}}, "result": {"response": "AITA: That's right! So the main idea is about a lost kitten who finds her home. Great job!", "duration": "PT8.20S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.02}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.01}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>She finds her home.<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:20Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid2_turn1_output_flagged", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student002"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session2/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Why Leaves Change Color' on LO: RC.4.LO.Vocabulary"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What does pigment mean?", "http://example.com/xapi/extensions/aita_response_raw": "A pigment is like, you know, the stuff that makes things colored, sometimes it's kinda gross stuff."}}}, "result": {"response": "AITA: I was about to say something that might not be quite right for our lesson. Let's try a different way! How about you tell me what you found most interesting in the text?", "duration": "PT12.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.03}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": false, "flagged_categories": ["potentially_inappropriate_language"], "scores": {"inappropriate": 0.88, "toxic": 0.5}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_leaves_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session2", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO.Vocabulary", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What does pigment mean?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:05:00Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
"""

# --- Data Loading and Processing Functions ---

def load_xapi_statements(filepath: str = "xapi_statements.jsonl") -> List[Dict[str, Any]]:
    statements = []
    try:
        with open(filepath, 'r') as f:
            for line_number, line in enumerate(f, 1):
                try:
                    statements.append(json.loads(line))
                except json.JSONDecodeError as e:
                    st.warning(f"Skipping malformed line {line_number} in {filepath}: {e}") # Changed to st.warning
        return statements
    except FileNotFoundError:
        st.warning(f"Log file '{filepath}' not found. Using placeholder data for demonstration.")
        placeholder_lines = PLACEHOLDER_XAPI_STATEMENTS_CONTENT.strip().split('\n')
        for line_number, line in enumerate(placeholder_lines, 1):
            try:
                statements.append(json.loads(line))
            except json.JSONDecodeError as e:
                st.warning(f"Skipping malformed placeholder line {line_number}: {e}") # Changed for placeholder too
        return statements
    except Exception as e:
        st.error(f"An unexpected error occurred while loading {filepath}: {e}")
        return []


def get_session_summaries(statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sessions: Dict[str, Dict[str, Any]] = {}
    for i, stmt in enumerate(statements):
        # Robust session_id extraction
        session_id = stmt.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/session_id", f"unknown_session_stmt{i}")

        # Robust student_id extraction
        student_id = stmt.get("actor", {}).get("account", {}).get("name", "Unknown Student")

        if session_id not in sessions:
            sessions[session_id] = {
                "session_id": session_id,
                "student_id": student_id,
                "start_timestamp": stmt.get("timestamp", "N/A"),
                "turn_count": 0,
                "first_user_utterance": "N/A",
                "flagged_input_count": 0,
                "flagged_output_count": 0
            }

        sessions[session_id]["turn_count"] += 1
        if stmt.get("timestamp") and (sessions[session_id]["start_timestamp"] == "N/A" or sessions[session_id]["start_timestamp"] > stmt.get("timestamp")):
             sessions[session_id]["start_timestamp"] = stmt.get("timestamp")

        if sessions[session_id]["first_user_utterance"] == "N/A" and \
           stmt.get("object", {}).get("definition", {}).get("extensions", {}).get("http://example.com/xapi/extensions/user_utterance_raw"):
            sessions[session_id]["first_user_utterance"] = stmt["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/user_utterance_raw"]

        # Count moderation flags
        input_mod = stmt.get("result", {}).get("extensions", {}).get("http://example.com/xapi/extensions/input_moderation_details", {})
        if isinstance(input_mod, dict) and input_mod.get("is_safe") is False:
            sessions[session_id]["flagged_input_count"] += 1

        output_mod = stmt.get("result", {}).get("extensions", {}).get("http://example.com/xapi/extensions/output_moderation_details", {})
        if isinstance(output_mod, dict) and output_mod.get("is_safe") is False:
            sessions[session_id]["flagged_output_count"] += 1

    sorted_sessions = sorted(sessions.values(), key=lambda s: s.get("start_timestamp", ""), reverse=True)
    return sorted_sessions


def get_dialogue_turns_for_session(statements: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
    session_statements = [s for s in statements if s.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/session_id") == session_id]

    dialogue_turns = []
    for stmt in session_statements:
        # Robust extraction for moderation details
        result_extensions = stmt.get("result", {}).get("extensions", {})
        input_moderation = result_extensions.get("http://example.com/xapi/extensions/input_moderation_details")
        output_moderation = result_extensions.get("http://example.com/xapi/extensions/output_moderation_details")

        object_definition_extensions = stmt.get("object",{}).get("definition",{}).get("extensions",{})

        turn_data: Dict[str, Any] = {
            "timestamp": stmt.get("timestamp", "N/A"),
            "speaker": "Unknown",
            "utterance": "N/A",
            "input_moderation": input_moderation if isinstance(input_moderation, dict) else None,
            "output_moderation": output_moderation if isinstance(output_moderation, dict) else None,
            "raw_llm_response": object_definition_extensions.get("http://example.com/xapi/extensions/aita_response_raw"),
            "full_llm_prompt": stmt.get("context",{}).get("extensions",{}).get("http://example.com/xapi/extensions/full_prompt_to_llm"),
            "aita_persona": stmt.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/aita_persona", "N/A"),
            "active_lo": stmt.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/learning_objective_active", "N/A"),
            "content_item_id": stmt.get("context", {}).get("contextActivities", {}).get("parent", [{}])[0].get("id", "N/A")
        }

        user_utterance = object_definition_extensions.get("http://example.com/xapi/extensions/user_utterance_raw")
        aita_response = stmt.get("result", {}).get("response")

        if user_utterance:
            turn_data["speaker"] = "user"
            turn_data["utterance"] = user_utterance
        elif aita_response:
            turn_data["speaker"] = "assistant"
            turn_data["utterance"] = aita_response

        dialogue_turns.append(turn_data)

    dialogue_turns.sort(key=lambda t: t.get("timestamp", ""))
    return dialogue_turns

# --- Streamlit UI Layout ---
def render_dashboard():
    st.set_page_config(page_title="AITA Teacher Dashboard", layout="wide")
    st.title("AITA Teacher Oversight Dashboard (Prototype)")

    statements = load_xapi_statements()

    if not statements:
        st.info("No interaction logs found or loaded. Ensure 'xapi_statements.jsonl' exists or check error messages.")
        return

    session_summaries_all = get_session_summaries(statements)

    if not session_summaries_all:
        st.info("No sessions found in the loaded statements.")
        return

    # Sidebar for Session Selection & Filters
    st.sidebar.header("Filters & Navigation")

    # Filters for Overview Page
    filter_student_id = st.sidebar.text_input("Filter by Student ID (exact match):").strip()

    # Ensure date_input uses datetime.date or None
    filter_date_val: Optional[datetime.date] = st.sidebar.date_input(
        "Filter by Date (shows sessions from this date):",
        value=None, # No default date selected
        key="filter_date_picker"
    )

    # Apply filters
    session_summaries_for_display = session_summaries_all
    if filter_student_id:
        session_summaries_for_display = [
            s for s in session_summaries_for_display if s["student_id"].lower() == filter_student_id.lower()
        ]
    if filter_date_val:
        filter_date_str = filter_date_val.isoformat() # Convert date object to YYYY-MM-DD string
        session_summaries_for_display = [
            s for s in session_summaries_for_display if s["start_timestamp"].startswith(filter_date_str)
        ]

    # Session selection dropdown in sidebar
    if not session_summaries_for_display:
         # Display info message in sidebar if no sessions match filters for selection
        st.sidebar.info("No sessions match current filters for selection.")
        session_options_display = ["Overview"]
        option_to_id_map = {"Overview": "Overview"}
    else:
        session_options_display = ["Overview"] + [
            f"{s['session_id']} (Student: {s['student_id']}, Time: {s['start_timestamp']})" for s in session_summaries_for_display
        ]
        option_to_id_map = {"Overview": "Overview"}
        for i, summary in enumerate(session_summaries_for_display): # Use filtered list for map
            option_to_id_map[session_options_display[i+1]] = summary["session_id"]


    selected_formatted_option = st.sidebar.selectbox(
        "Select a Session (or Overview):",
        options=session_options_display,
        index=0
    )
    selected_session_id = option_to_id_map[selected_formatted_option]


    # Main Area Display
    if selected_session_id == "Overview":
        st.header("Recent Session Overview")

        # Aggregate Stats
        st.subheader("Overall Statistics (Filtered)")
        col1, col2 = st.columns(2)
        col1.metric("Total Sessions Displayed", len(session_summaries_for_display))
        # Calculate total turns for displayed sessions
        total_turns_displayed = sum(s['turn_count'] for s in session_summaries_for_display)
        col2.metric("Total Interaction Turns (in displayed sessions)", total_turns_displayed)

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
            st.dataframe(pd.DataFrame(overview_data), use_container_width=True)

    else: # Session Detail View
        dialogue_turns = get_dialogue_turns_for_session(statements, selected_session_id) # Use original statements for lookup

        # Extract session-level context for display
        current_session_info = next((s for s in session_summaries_all if s["session_id"] == selected_session_id), None)
        student_id_display = current_session_info["student_id"] if current_session_info else "N/A"

        # Extract AITA persona, LO, Content ID from the first relevant turn (usually an AITA turn)
        aita_persona_display = "N/A"
        active_lo_display = "N/A"
        content_item_id_display = "N/A"

        first_aita_turn_data = next((turn for turn in dialogue_turns if turn["speaker"] == "assistant" and turn.get("aita_persona")), None)
        if not first_aita_turn_data: # Fallback to any turn if no assistant turn with info
            first_aita_turn_data = dialogue_turns[0] if dialogue_turns else None

        if first_aita_turn_data:
            aita_persona_display = first_aita_turn_data.get("aita_persona", "N/A")
            active_lo_display = first_aita_turn_data.get("active_lo", "N/A")
            content_item_id_display = first_aita_turn_data.get("content_item_id", "N/A")

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
            return

        for turn in dialogue_turns:
            role = turn["speaker"] if turn["speaker"] in ["user", "assistant"] else "assistant"
            with st.chat_message(name=role):
                st.markdown(f"**{turn['speaker'].capitalize()}** (at {turn['timestamp']}):")
                st.markdown(turn["utterance"])

                if turn["input_moderation"]:
                    if not turn["input_moderation"]["is_safe"]:
                        st.error(f"⚠️ Input flagged by safeguard! Categories: {turn['input_moderation']['flagged_categories']}")
                    with st.expander("Input Moderation Details", expanded=False):
                        st.json(turn["input_moderation"])

                if turn["output_moderation"] and role == "assistant":
                    if not turn["output_moderation"]["is_safe"]:
                        st.warning(f"⚠️ AITA output was moderated/replaced! Original flagged categories: {turn['output_moderation']['flagged_categories']}")
                    with st.expander("Output Moderation Details (AITA Raw)", expanded=False):
                        st.json(turn["output_moderation"])
                        if turn["raw_llm_response"] and turn["raw_llm_response"] != turn["utterance"]:
                            st.text_area("Original LLM Response (before safeguard override):", value=turn["raw_llm_response"], height=100, disabled=True)

                if role == "assistant" and turn["full_llm_prompt"]:
                    with st.expander("Full Prompt to LLM (for this AITA turn)", expanded=False):
                        st.text_area("Prompt:", value=turn["full_llm_prompt"], height=150, disabled=True)

if __name__ == "__main__":
    render_dashboard()
