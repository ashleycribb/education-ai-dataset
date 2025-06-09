import streamlit as st
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime # Required for date comparisons if any
import os # For checking if file exists

# --- Placeholder Data (if xapi_statements.jsonl not found) ---
# Updated to include pedagogical_notes and aita_turn_narrative_rationale
PLACEHOLDER_XAPI_STATEMENTS_CONTENT_FOR_MANAGER = """
{"id": "uuid1_turn1_aita", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/responded", "display": {"en-US": "responded to AITA"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What is the story about?", "http://example.com/xapi/extensions/pedagogical_notes": ["Greet student and present passage.", "Ask open-ended question to elicit initial thoughts on main idea."], "http://example.com/xapi/extensions/aita_turn_narrative_rationale": "AITA initiated the dialogue by presenting the story and asking a broad question to gauge the student's initial comprehension of the main idea."}}}, "result": {"response": "AITA: It's about a little kitten named Lily who gets lost. What else happens in the story?", "duration": "PT10.50S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.1}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.05}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What is the story about?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:00:05Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid1_turn2_student", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student001"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session1/turn/2", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Lily the Lost Kitten' on LO: RC.4.LO1.MainIdea.Narrative"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "This is stupid and I hate it."}}}, "result": {"response": "AITA: I'm sorry, I can't process that request. Let's stick to our reading task or try phrasing it differently.", "duration": "PT0.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": false, "flagged_categories": ["insult", "toxic"], "scores": {"insult": 0.85, "toxic": 0.92}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.05}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_kitten_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session1", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO1.MainIdea.Narrative", "http://example.com/xapi/extensions/full_prompt_to_llm": ""}}, "timestamp": "2024-07-31T10:00:15Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
{"id": "uuid2_turn1_aita_output_flagged", "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": "student002"}}, "verb": {"id": "http://adlnet.gov/expapi/verbs/responded", "display": {"en-US": "responded to AITA"}}, "object": {"objectType": "Activity", "id": "http://example.com/aita_pilot/session/session2/turn/1", "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": "Interaction with Reading Explorer AITA about 'Why Leaves Change Color' on LO: RC.4.LO.Vocabulary"}, "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {"http://example.com/xapi/extensions/user_utterance_raw": "What does pigment mean?", "http://example.com/xapi/extensions/aita_response_raw": "A pigment is like, you know, the stuff that makes things colored, sometimes it's kinda gross stuff.", "http://example.com/xapi/extensions/pedagogical_notes": ["Attempt to define 'pigment'.", "Use informal language."], "http://example.com/xapi/extensions/aita_turn_narrative_rationale": "AITA attempts to define 'pigment' using informal language after student query."}}}, "result": {"response": "AITA: I was about to say something that might not be quite right for our lesson. Let's try a different way! How about you tell me what you found most interesting in the text?", "duration": "PT12.00S", "extensions": {"http://example.com/xapi/extensions/input_moderation_details": {"is_safe": true, "flagged_categories": [], "scores": {"toxic": 0.03}, "model_used": "dummy_moderation_service_v1"}, "http://example.com/xapi/extensions/output_moderation_details": {"is_safe": false, "flagged_categories": ["potentially_inappropriate_language"], "scores": {"inappropriate": 0.88, "toxic": 0.5}, "model_used": "dummy_moderation_service_v1"}}}, "context": {"contextActivities": {"parent": [{"id": "http://example.com/aita_pilot/passage/passage_leaves_001"}]}, "extensions": {"http://example.com/xapi/extensions/session_id": "session2", "http://example.com/xapi/extensions/aita_persona": "Reading Explorer AITA", "http://example.com/xapi/extensions/learning_objective_active": "RC.4.LO.Vocabulary", "http://example.com/xapi/extensions/full_prompt_to_llm": "<|system|>...</|user|>What does pigment mean?<|end|><|assistant|>"}}, "timestamp": "2024-07-31T10:05:00Z", "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}}
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
        session_id_path = stmt.get("context", {}).get("extensions", {})
        session_id = session_id_path.get("http://example.com/xapi/extensions/session_id", f"unknown_session_stmt{i}") if isinstance(session_id_path, dict) else f"unknown_session_stmt{i}"

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
        # New fields for reasoner
        pedagogical_notes = object_definition_extensions.get("http://example.com/xapi/extensions/pedagogical_notes") if isinstance(object_definition_extensions, dict) else None
        aita_turn_narrative_rationale = object_definition_extensions.get("http://example.com/xapi/extensions/aita_turn_narrative_rationale") if isinstance(object_definition_extensions, dict) else None

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
            "content_item_id": content_item_id,
            "pedagogical_notes": pedagogical_notes if isinstance(pedagogical_notes, list) else None, # Ensure it's a list or None
            "aita_turn_narrative_rationale": aita_turn_narrative_rationale if isinstance(aita_turn_narrative_rationale, str) else None # Ensure it's a string or None
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
Now, I will update `pages/02_Session_Transcript_View.py`.
