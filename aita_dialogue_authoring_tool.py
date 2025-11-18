import streamlit as st
import json
import datetime
from typing import List, Dict, Any, Optional
import uuid

# --- Helper Function: New Dialogue Template ---
def get_new_dialogue_template() -> Dict[str, Any]:
    """Returns a blank, fully structured enhanced AITA JSON object."""
    now_utc_iso = datetime.datetime.utcnow().isoformat() + "Z"
    dialogue_uuid = uuid.uuid4().hex

    # Default LO for the list
    default_lo = {"id": "Example.LO.ID.1", "text": "Example Learning Objective Description"}

    return {
        "dialogue_id": f"dialogue_{dialogue_uuid}",
        "version": "1.5_AITA_AuthoringTool_V1", # Updated version
        "creation_timestamp_utc": now_utc_iso,
        "last_updated_timestamp_utc": now_utc_iso,
        "metadata": {
            "original_source_content_id": "",
            "original_source_dataset": "",
            "tags": [], # Initialize as empty list for tag input
            "tool_source": "AITA_Authoring_Tool_V1"
        },
        "aita_profile": {
            "subject": "",
            "grade_level": "",
            "persona_name": "",
            "target_audience_description": ""
        },
        "pedagogical_intent": {
            "interaction_type": "",
            "learning_objectives": [default_lo], # Initialize with one example LO
            "expected_student_thinking_process": "",
            "keywords": [], # Initialize as empty list
            "difficulty_level": ""
        },
        "context_provided_to_aita": {
            "user_id": "authoring_tool_user",
            "session_id": f"authoring_session_{dialogue_uuid}",
            "prior_knowledge_level": "unknown",
            "prior_performance_summary": "",
            "learning_context_description": "",
            "content_item_id": "",
            "content_item_title": "",
            "content_item_text": "", # Main passage text
            "potential_grade_level_of_content": ""
        },
        "dialogue_turns": [], # Initialize as empty list
        "final_assessment_of_student_understanding": {
            "summary_of_understanding": "",
            "mastery_level_per_lo": [{"lo_id": "Example.LO.ID.1", "level": "not_assessed"}],
            "next_steps_recommendation": ""
        },
        "session_metadata_for_teacher_oversight": {
            "session_duration_seconds": 0,
            "engagement_metrics": {"total_turns": 0, "student_turns": 0, "aita_turns": 0},
            "flags_for_teacher_review": [], # Initialize as empty list
            "session_summary_notes": ""
        }
    }

# --- Session State Initialization ---
if "current_dialogue" not in st.session_state:
    st.session_state.current_dialogue = get_new_dialogue_template()

# --- Callback Functions for Turn Management ---
def add_turn_callback(speaker_type: str):
    dialogue = st.session_state.current_dialogue
    turn_number = len(dialogue["dialogue_turns"]) + 1
    new_turn = {
        "turn_id": f"{dialogue.get('dialogue_id', 'dialogue')}_turn_{turn_number}",
        "speaker": speaker_type,
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "utterance_modality": "text",
        "utterance": "",
        "pedagogical_notes": [],
        "safeguard_tags": [],
        "ontology_concept_tags": [],
        "xapi_verb_id": "",
        "xapi_object_id": ""
    }
    if speaker_type == "AITA":
        new_turn["confidence_score_aita"] = None # Optional field

    dialogue["dialogue_turns"].append(new_turn)
    dialogue["last_updated_timestamp_utc"] = datetime.datetime.utcnow().isoformat() + "Z"

def delete_turn_callback(turn_idx: int):
    dialogue = st.session_state.current_dialogue
    if 0 <= turn_idx < len(dialogue["dialogue_turns"]):
        del dialogue["dialogue_turns"][turn_idx]
        # Re-assign turn_ids to maintain sequence if needed, or keep original unique IDs
        for i, turn in enumerate(dialogue["dialogue_turns"]):
            turn["turn_id"] = f"{dialogue.get('dialogue_id', 'dialogue')}_turn_{i + 1}"
        dialogue["last_updated_timestamp_utc"] = datetime.datetime.utcnow().isoformat() + "Z"

def update_dialogue_field(path: List[str], value: Any):
    """Updates a nested field in the session state dialogue using a path."""
    d = st.session_state.current_dialogue
    for key in path[:-1]:
        d = d.setdefault(key, {})
    d[path[-1]] = value
    st.session_state.current_dialogue["last_updated_timestamp_utc"] = datetime.datetime.utcnow().isoformat() + "Z"

def update_turn_field(turn_idx: int, field_path: List[str], value: Any):
    """Updates a field within a specific dialogue turn."""
    turn = st.session_state.current_dialogue["dialogue_turns"][turn_idx]
    d = turn
    for key in field_path[:-1]:
        d = d.setdefault(key, {})
    d[field_path[-1]] = value
    st.session_state.current_dialogue["last_updated_timestamp_utc"] = datetime.datetime.utcnow().isoformat() + "Z"


# --- Main UI Rendering Function ---
def render_authoring_tool():
    st.set_page_config(page_title="AITA Dialogue Authoring Tool", layout="wide")
    st.title("AITA Dialogue Authoring Tool (V1 Prototype)")

    # Ensure dialogue is initialized
    if "current_dialogue" not in st.session_state or not st.session_state.current_dialogue:
        st.session_state.current_dialogue = get_new_dialogue_template()

    dialogue_data = st.session_state.current_dialogue

    # --- File Operations (Sidebar) ---
    with st.sidebar:
        st.header("File Operations")
        uploaded_file = st.file_uploader("Load AITA Dialogue JSON", type=["json"], key="file_uploader")
        if uploaded_file is not None:
            try:
                loaded_data = json.load(uploaded_file)
                # Basic validation: check for a few key top-level fields
                if "dialogue_id" in loaded_data and "dialogue_turns" in loaded_data:
                    st.session_state.current_dialogue = loaded_data
                    st.success("Dialogue loaded successfully!")
                    st.rerun() # Rerun to update the UI with loaded data
                else:
                    st.error("Invalid AITA JSON structure. Missing 'dialogue_id' or 'dialogue_turns'.")
            except json.JSONDecodeError:
                st.error("Error: Could not decode JSON from the uploaded file.")
            except Exception as e:
                st.error(f"An unexpected error occurred during file loading: {e}")

        # Ensure dialogue_id is available for file_name, even if it's the default from template
        file_name_id = dialogue_data.get("dialogue_id", "new_dialogue")
        if not file_name_id or not isinstance(file_name_id, str) or file_name_id.strip() == "":
            file_name_id = "dialogue" # Fallback if dialogue_id is somehow invalid

        st.download_button(
            label="Save Dialogue as JSON",
            data=json.dumps(dialogue_data, indent=2),
            file_name=f"{file_name_id}.json",
            mime="application/json"
        )

        if st.button("Create New Dialogue"):
            st.session_state.current_dialogue = get_new_dialogue_template()
            st.rerun()

    # --- Main Editing Area with Tabs ---
    tab1, tab2, tab3 = st.tabs(["Global Dialogue Info", "Dialogue Turns Editor", "Assessment & Session Metadata"])

    with tab1:
        st.subheader("Global Dialogue Information")
        # Using a function to update nested dicts in session_state to ensure changes are registered

        # Global Dialogue ID & Version
        update_dialogue_field(["dialogue_id"], st.text_input("Dialogue ID", value=dialogue_data.get("dialogue_id", ""), key="dialogue_id_main"))
        update_dialogue_field(["version"], st.text_input("Schema Version", value=dialogue_data.get("version", "1.5_AITA_AuthoringTool_V1"), key="version_main"))

        with st.expander("Metadata", expanded=True):
            update_dialogue_field(["metadata", "original_source_content_id"], st.text_input("Source Content ID", value=dialogue_data.get("metadata", {}).get("original_source_content_id", ""), key="meta_src_id"))
            update_dialogue_field(["metadata", "original_source_dataset"], st.text_input("Source Dataset Name", value=dialogue_data.get("metadata", {}).get("original_source_dataset", ""), key="meta_src_dataset"))
            tags_str = st.text_input("Tags (comma-separated)", value=", ".join(dialogue_data.get("metadata", {}).get("tags", [])), key="meta_tags")
            update_dialogue_field(["metadata", "tags"], [t.strip() for t in tags_str.split(',') if t.strip()])

        with st.expander("AITA Profile", expanded=True):
            update_dialogue_field(["aita_profile", "subject"], st.text_input("Subject", value=dialogue_data.get("aita_profile", {}).get("subject", ""), key="ap_subject"))
            update_dialogue_field(["aita_profile", "grade_level"], st.text_input("Grade Level", value=dialogue_data.get("aita_profile", {}).get("grade_level", ""), key="ap_grade"))
            update_dialogue_field(["aita_profile", "persona_name"], st.text_input("Persona Name", value=dialogue_data.get("aita_profile", {}).get("persona_name", ""), key="ap_persona"))
            update_dialogue_field(["aita_profile", "target_audience_description"], st.text_area("Target Audience Description", value=dialogue_data.get("aita_profile", {}).get("target_audience_description", ""), key="ap_audience"))

        with st.expander("Pedagogical Intent", expanded=True):
            update_dialogue_field(["pedagogical_intent", "interaction_type"], st.text_input("Interaction Type", value=dialogue_data.get("pedagogical_intent", {}).get("interaction_type", ""), key="pi_interaction"))
            # For simplicity, LOs are handled as a single text area for JSON editing in V1
            # A more advanced tool would have dynamic list input for LO objects
            los_json_str = st.text_area("Learning Objectives (JSON list of objects with 'id' and 'text')",
                                        value=json.dumps(dialogue_data.get("pedagogical_intent", {}).get("learning_objectives", [{"id":"", "text":""}]), indent=2),
                                        height=150, key="pi_los")
            try: update_dialogue_field(["pedagogical_intent", "learning_objectives"], json.loads(los_json_str))
            except json.JSONDecodeError: st.warning("Learning Objectives JSON is invalid.", icon="⚠️")

            update_dialogue_field(["pedagogical_intent", "expected_student_thinking_process"], st.text_area("Expected Student Thinking", value=dialogue_data.get("pedagogical_intent", {}).get("expected_student_thinking_process", ""), key="pi_thinking"))
            keywords_str = st.text_input("Keywords (comma-separated)", value=", ".join(dialogue_data.get("pedagogical_intent", {}).get("keywords", [])), key="pi_keywords")
            update_dialogue_field(["pedagogical_intent", "keywords"], [k.strip() for k in keywords_str.split(',') if k.strip()])
            update_dialogue_field(["pedagogical_intent", "difficulty_level"], st.text_input("Difficulty Level", value=dialogue_data.get("pedagogical_intent", {}).get("difficulty_level", ""), key="pi_difficulty"))

        with st.expander("Context Provided to AITA (Passage, etc.)", expanded=True):
            update_dialogue_field(["context_provided_to_aita", "content_item_id"], st.text_input("Content Item ID (e.g., Passage ID)", value=dialogue_data.get("context_provided_to_aita", {}).get("content_item_id", ""), key="ctx_item_id"))
            update_dialogue_field(["context_provided_to_aita", "content_item_title"], st.text_input("Content Item Title", value=dialogue_data.get("context_provided_to_aita", {}).get("content_item_title", ""), key="ctx_item_title"))
            update_dialogue_field(["context_provided_to_aita", "content_item_text"], st.text_area("Content Item Text (e.g., Full Passage)", value=dialogue_data.get("context_provided_to_aita", {}).get("content_item_text", ""), height=300, key="ctx_item_text"))
            # Other context fields can be added similarly or via a JSON text area for advanced users

    with tab2:
        st.subheader("Dialogue Turns Editor")

        # Display turns for editing
        for idx, turn_data in enumerate(dialogue_data.get("dialogue_turns", [])):
            with st.expander(f"Turn {idx + 1}: {turn_data.get('speaker', 'N/A')} - \"{turn_data.get('utterance', '')[:30]}...\"", expanded=False):
                col1, col2 = st.columns([3,1]) # Give more space to utterance
                with col1:
                    new_utterance = st.text_area("Utterance", value=turn_data.get("utterance", ""), key=f"utterance_{idx}")
                    if new_utterance != turn_data.get("utterance"):
                        update_turn_field(idx, ["utterance"], new_utterance)
                with col2:
                    new_speaker = st.selectbox("Speaker", ["AITA", "student"], index=0 if turn_data.get("speaker") == "AITA" else 1, key=f"speaker_{idx}")
                    if new_speaker != turn_data.get("speaker"):
                        update_turn_field(idx, ["speaker"], new_speaker)
                    st.button("Delete Turn", key=f"delete_turn_{idx}", on_click=delete_turn_callback, args=(idx,))

                if turn_data.get("speaker") == "AITA":
                    st.markdown("--- AITA Specific Fields ---")
                    ped_notes_current = "\n".join(turn_data.get("pedagogical_notes", []))
                    new_ped_notes_str = st.text_area("Pedagogical Notes (one note per line)", value=ped_notes_current, key=f"ped_notes_{idx}")
                    if new_ped_notes_str != ped_notes_current:
                        update_turn_field(idx, ["pedagogical_notes"], [note.strip() for note in new_ped_notes_str.split('\n') if note.strip()])

                    sg_tags_current = ",".join(turn_data.get("safeguard_tags", []))
                    new_sg_tags_str = st.text_input("Safeguard Tags (comma-sep)", value=sg_tags_current, key=f"sg_tags_{idx}")
                    if new_sg_tags_str != sg_tags_current:
                         update_turn_field(idx, ["safeguard_tags"], [t.strip() for t in new_sg_tags_str.split(',') if t.strip()])

                    ont_tags_current = ",".join(turn_data.get("ontology_concept_tags", []))
                    new_ont_tags_str = st.text_input("Ontology Concept Tags (comma-sep)", value=ont_tags_current, key=f"ont_tags_{idx}")
                    if new_ont_tags_str != ont_tags_current:
                        update_turn_field(idx, ["ontology_concept_tags"], [t.strip() for t in new_ont_tags_str.split(',') if t.strip()])

                    # Conceptual fields as simple text inputs
                    new_xapi_verb = st.text_input("xAPI Verb ID (URI)", value=turn_data.get("xapi_verb_id", ""), key=f"xapi_verb_{idx}")
                    if new_xapi_verb != turn_data.get("xapi_verb_id"): update_turn_field(idx, ["xapi_verb_id"], new_xapi_verb)

                    new_xapi_obj = st.text_input("xAPI Object ID (URI)", value=turn_data.get("xapi_object_id", ""), key=f"xapi_obj_{idx}")
                    if new_xapi_obj != turn_data.get("xapi_object_id"): update_turn_field(idx, ["xapi_object_id"], new_xapi_obj)

                    new_conf_score = st.number_input("AITA Confidence (0.0-1.0)", min_value=0.0, max_value=1.0, value=turn_data.get("confidence_score_aita", 0.95) if turn_data.get("confidence_score_aita") is not None else 0.95, step=0.01, key=f"conf_{idx}")
                    if new_conf_score != turn_data.get("confidence_score_aita"): update_turn_field(idx, ["confidence_score_aita"], new_conf_score)


        # Add turn buttons
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            st.button("Add Student Turn", on_click=add_turn_callback, args=("student",), use_container_width=True)
        with col_add2:
            st.button("Add AITA Turn", on_click=add_turn_callback, args=("AITA",), use_container_width=True)

    with tab3:
        st.subheader("Final Assessment & Session Metadata")
        with st.expander("Final Assessment of Student Understanding", expanded=True):
            update_dialogue_field(["final_assessment_of_student_understanding", "summary_of_understanding"],
                                  st.text_area("Summary of Understanding", value=dialogue_data.get("final_assessment_of_student_understanding", {}).get("summary_of_understanding", ""), key="assess_summary"))

            mastery_json_str = st.text_area("Mastery Levels (JSON list of objects with 'lo_id' and 'level')",
                                            value=json.dumps(dialogue_data.get("final_assessment_of_student_understanding", {}).get("mastery_level_per_lo", [{"lo_id":"", "level":""}]), indent=2),
                                            height=100, key="assess_mastery")
            try: update_dialogue_field(["final_assessment_of_student_understanding", "mastery_level_per_lo"], json.loads(mastery_json_str))
            except json.JSONDecodeError: st.warning("Mastery Levels JSON is invalid.", icon="⚠️")

            update_dialogue_field(["final_assessment_of_student_understanding", "next_steps_recommendation"],
                                  st.text_area("Next Steps Recommendation", value=dialogue_data.get("final_assessment_of_student_understanding", {}).get("next_steps_recommendation", ""), key="assess_next_steps"))

        with st.expander("Session Metadata for Teacher Oversight", expanded=True):
            # These are mostly runtime, but can be set conceptually for the authored scenario
            update_dialogue_field(["session_metadata_for_teacher_oversight", "session_duration_seconds"],
                                  st.number_input("Conceptual Session Duration (seconds)", value=dialogue_data.get("session_metadata_for_teacher_oversight", {}).get("session_duration_seconds", 0), key="meta_duration"))

            flags_str = st.text_input("Flags for Teacher Review (comma-separated)", value=", ".join(dialogue_data.get("session_metadata_for_teacher_oversight", {}).get("flags_for_teacher_review", [])), key="meta_flags")
            update_dialogue_field(["session_metadata_for_teacher_oversight", "flags_for_teacher_review"], [f.strip() for f in flags_str.split(',') if f.strip()])

            update_dialogue_field(["session_metadata_for_teacher_oversight", "session_summary_notes"],
                                  st.text_area("Session Summary Notes (for teacher)", value=dialogue_data.get("session_metadata_for_teacher_oversight", {}).get("session_summary_notes", ""), key="meta_summary_notes"))


# --- Running the App ---
if __name__ == "__main__":
    render_authoring_tool()
