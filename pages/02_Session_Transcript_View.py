import streamlit as st
from typing import Optional, List, Dict, Any
import sys
import os
import pandas # Not strictly needed for this page, but good to have if manipulating turn data

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from dashboard_data_manager import load_xapi_statements, get_turns_for_session, get_session_summaries
except ImportError:
    st.error("Could not import DashboardDataManager. Ensure it's in the correct path.")
    def load_xapi_statements(filepath=""): return []
    def get_turns_for_session(statements, session_id): return []
    def get_session_summaries(statements): return []


st.set_page_config(page_title="Session Transcript", layout="wide")
st.title("Session Transcript Viewer")

statements = load_xapi_statements()

if not statements:
    st.warning("No xAPI statements loaded. Transcript view cannot be displayed.")
    st.stop()

all_session_summaries = get_session_summaries(statements)

if not all_session_summaries:
    st.info("No sessions found in the loaded data.")
    st.stop()

# Session selection in the main area for this page
formatted_session_options = [
    f"{s['session_id']} (Student: {s['student_id']}, Time: {s['start_timestamp']})" for s in all_session_summaries
]
# Ensure there's a default if options are available, otherwise index might be an issue
default_index = 0 if formatted_session_options else None # Or handle case of no options more explicitly

# Create mapping from formatted option string back to original session_id
option_to_id_map = {formatted_option: summary["session_id"]
                    for formatted_option, summary in zip(formatted_session_options, all_session_summaries)}


selected_formatted_option = st.selectbox(
    "Select a Session to view its transcript:",
    options=formatted_session_options, # Use the formatted list
    index=default_index
)

if selected_formatted_option:
    selected_session_id = option_to_id_map[selected_formatted_option] # Get actual ID from map

    current_session_info = next((s for s in all_session_summaries if s["session_id"] == selected_session_id), None)
    student_id_display = current_session_info["student_id"] if current_session_info else "N/A"

    dialogue_turns = get_turns_for_session(statements, selected_session_id)

    aita_persona_display = "N/A"
    active_lo_display = "N/A"
    content_item_id_display = "N/A"

    # Extract context from the first turn that has it (usually an AITA turn)
    # This assumes context like persona, LO, content_item_id is consistent per session,
    # which is true for current xAPI logging strategy.
    first_contextual_turn = next((turn for turn in dialogue_turns if turn.get("aita_persona") != "N/A" and turn.get("active_lo") != "N/A"), None)
    if not first_contextual_turn and dialogue_turns: # Fallback to first turn if specific not found
        first_contextual_turn = dialogue_turns[0]

    if first_contextual_turn:
        aita_persona_display = first_contextual_turn.get("aita_persona", "N/A")
        active_lo_display = first_contextual_turn.get("active_lo", "N/A")
        content_item_id_display = first_contextual_turn.get("content_item_id", "N/A")

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
            # Determine role for chat_message, default to "assistant" if not "user"
            role = "user" if turn.get("speaker", "").lower() == "user" else "assistant"

            with st.chat_message(name=role):
                speaker_display_name = turn.get('speaker', 'Unknown').capitalize()
                st.markdown(f"**{speaker_display_name}** (at {turn.get('timestamp', 'N/A')}):")
                st.markdown(turn.get("utterance", "*No utterance recorded*"))

                # Input Moderation Details (typically for user turns)
                if turn.get("input_moderation"):
                    mod_details = turn["input_moderation"]
                    if isinstance(mod_details, dict) and not mod_details.get("is_safe", True):
                        st.error(f"⚠️ Input flagged! Categories: {mod_details.get('flagged_categories', [])}")
                    with st.expander("Input Moderation Details", expanded=False):
                        st.json(mod_details)

                # Output Moderation & Reasoner Details (for AITA turns)
                if role == "assistant": # Check if it's an AITA turn
                    if turn.get("output_moderation"):
                        mod_details = turn["output_moderation"]
                        if isinstance(mod_details, dict) and not mod_details.get("is_safe", True):
                            st.warning(f"⚠️ AITA output was moderated/replaced! Original flagged: {mod_details.get('flagged_categories', [])}")
                        with st.expander("Output Moderation Details (AITA Raw)", expanded=False):
                            st.json(mod_details)
                            if turn.get("raw_llm_response") and turn.get("raw_llm_response") != turn.get("utterance"):
                                st.text_area("Original LLM Response (before safeguard override):", value=turn["raw_llm_response"], height=100, disabled=True)

                    # Display AITA Reasoner fields (NEW FOR THIS SUBTASK)
                    if turn.get("aita_turn_narrative_rationale"):
                        st.markdown(f"**AITA's Rationale:** _{turn['aita_turn_narrative_rationale']}_")

                    if turn.get("pedagogical_notes"):
                        with st.expander("Detailed Pedagogical Notes", expanded=False):
                            if isinstance(turn["pedagogical_notes"], list) and turn["pedagogical_notes"]:
                                for note in turn["pedagogical_notes"]:
                                    st.markdown(f"- {note}")
                            elif isinstance(turn["pedagogical_notes"], str): # Handle if it's a single string by mistake
                                st.markdown(f"- {turn['pedagogical_notes']}")
                            else:
                                st.markdown("No detailed pedagogical notes provided for this turn.")

                if role == "assistant" and turn.get("full_llm_prompt"): # Full prompt for AITA turns
                    with st.expander("Full Prompt to LLM (for this AITA turn)", expanded=False):
                        st.text_area("Prompt:", value=turn["full_llm_prompt"], height=150, disabled=True)
else:
    st.info("Please select a session from the dropdown to view its transcript.")
