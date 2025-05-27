# To run: streamlit run teacher_dashboard_prototype.py
import streamlit as st
import json
import datetime
import pandas as pd
from typing import List, Dict, Any, Optional

# --- Placeholder Data (if xapi_statements.jsonl not found) ---
PLACEHOLDER_XAPI_STATEMENTS_CONTENT = """
{"id": "uuid1_turn1", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What is the story about?"}}}, "result": {"response": "AITA: It's about a little kitten named Lily who gets lost. What else happens in the story?", "duration": "PT10.50S", "extensions": {"input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.1}, "model_used": "dummy_moderation_service"}, "output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.05}, "model_used": "dummy_moderation_service"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What is the story about?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:05Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid1_turn2", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/2", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "She finds her home."}}}, "result": {"response": "AITA: That's right! So the main idea is about a lost kitten who finds her home. Great job!", "duration": "PT8.20S", "extensions": {"input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.02}, "model_used": "dummy_moderation_service"}, "output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.01}, "model_used": "dummy_moderation_service"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>She finds her home.<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:20Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid2_turn1", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student002"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session2/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Why Leaves Change Color' on LO: RC.4.LO.Vocabulary"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What does pigment mean?"}}}, "result": {"response": "AITA: Good question! The passage says 'chlorophyll, the green pigment'. What do you think 'pigment' might mean there?", "duration": "PT12.00S", "extensions": {"input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.03}, "model_used": "dummy_moderation_service"}, "output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.04}, "model_used": "dummy_moderation_service"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_leaves_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session2", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO.Vocabulary", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What does pigment mean?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:05:00Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
"""

# --- Data Loading and Processing Functions ---

def load_xapi_statements(filepath: str = "xapi_statements.jsonl") -> List[Dict[str, Any]]:
    """Loads statements from the JSON Lines file."""
    statements = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    statements.append(json.loads(line))
                except json.JSONDecodeError as e:
                    st.error(f"Error decoding JSON from a line in {filepath}: {e}")
        return statements
    except FileNotFoundError:
        st.warning(f"Log file '{filepath}' not found. Using placeholder data for demonstration.")
        placeholder_lines = PLACEHOLDER_XAPI_STATEMENTS_CONTENT.strip().split('\n')
        for line in placeholder_lines:
            try:
                statements.append(json.loads(line))
            except json.JSONDecodeError as e:
                st.error(f"Error decoding placeholder JSON: {e}")
        return statements
    except Exception as e:
        st.error(f"An unexpected error occurred while loading {filepath}: {e}")
        return []


def get_session_summaries(statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Processes statements to identify unique sessions and summarize them."""
    sessions: Dict[str, Dict[str, Any]] = {}
    for stmt in statements:
        session_id = stmt.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/session_id")
        if not session_id:
            continue

        if session_id not in sessions:
            sessions[session_id] = {
                "session_id": session_id,
                "student_id": stmt.get("actor", {}).get("account", {}).get("name", "Unknown Student"),
                "start_timestamp": stmt.get("timestamp"),
                "turn_count": 0,
                "first_user_utterance": "N/A"
            }
        
        sessions[session_id]["turn_count"] += 1
        # Update start_timestamp if this statement is earlier
        if stmt.get("timestamp") and sessions[session_id]["start_timestamp"] > stmt.get("timestamp"):
             sessions[session_id]["start_timestamp"] = stmt.get("timestamp")

        if sessions[session_id]["first_user_utterance"] == "N/A" and \
           stmt.get("object", {}).get("definition", {}).get("extensions", {}).get("http://example.com/xapi/extensions/user_utterance_raw"):
            sessions[session_id]["first_user_utterance"] = stmt["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/user_utterance_raw"]
            
    # Sort sessions by timestamp, most recent first
    sorted_sessions = sorted(sessions.values(), key=lambda s: s.get("start_timestamp", ""), reverse=True)
    return sorted_sessions


def get_dialogue_turns_for_session(statements: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
    """Filters and formats statements for a given session's dialogue display."""
    session_statements = [s for s in statements if s.get("context", {}).get("extensions", {}).get("http://example.com/xapi/extensions/session_id") == session_id]
    
    dialogue_turns = []
    for stmt in session_statements:
        turn_data: Dict[str, Any] = {
            "timestamp": stmt.get("timestamp"),
            "speaker": "Unknown", # Will try to infer
            "utterance": "N/A",
            "input_moderation": stmt.get("result", {}).get("extensions", {}).get("http://example.com/xapi/extensions/input_moderation_details"),
            "output_moderation": stmt.get("result", {}).get("extensions", {}).get("http://example.com/xapi/extensions/output_moderation_details"),
            "raw_llm_response": stmt.get("object",{}).get("definition",{}).get("extensions",{}).get("http://example.com/xapi/extensions/aita_response_raw"),
            "full_llm_prompt": stmt.get("context",{}).get("extensions",{}).get("http://example.com/xapi/extensions/full_prompt_to_llm")
        }
        
        user_utterance = stmt.get("object", {}).get("definition", {}).get("extensions", {}).get("http://example.com/xapi/extensions/user_utterance_raw")
        aita_response = stmt.get("result", {}).get("response")

        if user_utterance: # This statement primarily logs a user's action
            turn_data["speaker"] = "user"
            turn_data["utterance"] = user_utterance
        elif aita_response: # This statement primarily logs AITA's response
            turn_data["speaker"] = "assistant" # Using Streamlit's "assistant" role
            turn_data["utterance"] = aita_response
        
        dialogue_turns.append(turn_data)
        
    # Sort turns by timestamp
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

    session_summaries = get_session_summaries(statements)

    if not session_summaries:
        st.info("No sessions found in the loaded statements.")
        return

    # Sidebar for Session Selection
    st.sidebar.header("Session Navigation")
    session_options = ["Overview"] + [s["session_id"] for s in session_summaries]
    # Format option to show more info in selectbox: Session ID (Student ID - Start Time)
    formatted_session_options = ["Overview"] + [
        f"{s['session_id']} (Student: {s['student_id']}, Time: {s['start_timestamp']})" for s in session_summaries
    ]
    
    # Use a dictionary to map formatted options back to original session_id
    option_to_id_map = {"Overview": "Overview"}
    for i, summary in enumerate(session_summaries):
        option_to_id_map[formatted_session_options[i+1]] = summary["session_id"]

    selected_formatted_option = st.sidebar.selectbox(
        "Select a Session (or Overview):",
        options=formatted_session_options,
        index=0 # Default to "Overview"
    )
    
    selected_session_id = option_to_id_map[selected_formatted_option]


    # Main Area Display
    if selected_session_id == "Overview":
        st.header("Recent Session Overview")
        # Prepare data for dataframe display
        overview_data = [{
            "Session ID": s["session_id"],
            "Student ID": s["student_id"],
            "Start Time (UTC)": s["start_timestamp"],
            "Turn Count": s["turn_count"],
            "First User Utterance": s["first_user_utterance"][:100] + "..." if len(s["first_user_utterance"]) > 100 else s["first_user_utterance"]
        } for s in session_summaries]
        
        if overview_data:
            st.dataframe(pd.DataFrame(overview_data), use_container_width=True)
        else:
            st.info("No session data to display for overview.")

    else:
        st.header(f"Dialogue Transcript: Session {selected_session_id}")
        
        # Find the student ID for the selected session for display
        current_session_student_id = "Unknown Student"
        for summary in session_summaries:
            if summary["session_id"] == selected_session_id:
                current_session_student_id = summary["student_id"]
                break
        st.subheader(f"Student ID: {current_session_student_id}")

        dialogue_turns = get_dialogue_turns_for_session(statements, selected_session_id)

        if not dialogue_turns:
            st.warning("No dialogue turns found for this session.")
            return

        for turn in dialogue_turns:
            role = turn["speaker"] if turn["speaker"] in ["user", "assistant"] else "assistant" # Default to assistant if speaker is unusual
            with st.chat_message(name=role): # name should be "user" or "assistant"
                st.markdown(f"**{turn['speaker'].capitalize()}** (at {turn['timestamp']}):")
                st.markdown(turn["utterance"])

                # Display moderation details if available
                if turn["input_moderation"]:
                    with st.expander("Input Moderation Details", expanded=False):
                        st.json(turn["input_moderation"])
                if turn["output_moderation"] and role == "assistant": # Output moderation is for AITA's response
                     with st.expander("Output Moderation Details (AITA Raw)", expanded=False):
                        st.json(turn["output_moderation"])
                        if turn["raw_llm_response"] and turn["raw_llm_response"] != turn["utterance"]:
                            st.text_area("Original LLM Response (before safeguard override):", value=turn["raw_llm_response"], height=100, disabled=True)
                
                # Optionally show full LLM prompt for AITA turns
                if role == "assistant" and turn["full_llm_prompt"]:
                    with st.expander("Full Prompt to LLM (for this AITA turn)", expanded=False):
                        st.text_area("", value=turn["full_llm_prompt"], height=150, disabled=True)


if __name__ == "__main__":
    render_dashboard()
