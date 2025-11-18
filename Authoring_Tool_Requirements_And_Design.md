# Interactive Scenario Authoring Tool for AITA Training Dialogues

## 1. Introduction

### Purpose of the Authoring Tool
The primary purpose of this Interactive Scenario Authoring Tool is to empower educators, curriculum specialists, subject matter experts (SMEs), and AI trainers to easily create, edit, and manage high-quality training dialogues for AI Tutors (AITAs). This tool aims to:
*   **Ensure Quality and Consistency**: Facilitate the creation of dialogues that adhere to the defined enhanced AITA JSON structure and pedagogical principles.
*   **Scale Dataset Creation**: Streamline the process of generating diverse and pedagogically rich datasets for fine-tuning AITAs for various subjects, grade levels, and learning objectives.
*   **Lower Technical Barrier**: Provide a user-friendly interface that does not require deep JSON editing skills, making AITA content creation more accessible.

### Target Users
*   **Educators (Teachers)**: Creating or adapting dialogues for their specific classroom needs or to target particular student challenges.
*   **Curriculum Specialists**: Designing sequences of dialogues aligned with curriculum standards and learning progressions.
*   **Subject Matter Experts (SMEs)**: Ensuring the factual accuracy and domain-specific pedagogical soundness of AITA interactions.
*   **AI Trainers / Dialogue Authors**: Focused on crafting detailed dialogue flows and annotating them with rich metadata for model fine-tuning.

## 2. User Stories

1.  **As an educator, I want to create a new AITA dialogue from scratch, associating it with a specific passage of text and a clear learning objective, so I can tailor content for my students.**
2.  **As a curriculum specialist, I want to load an existing AITA dialogue (in JSON format), edit its turns (both student and AITA utterances), and refine its pedagogical notes and conceptual ontology tags, so I can improve and standardize existing training data.**
3.  **As an SME, I want to easily add multiple distinct `pedagogical_notes` to an AITA turn, each explaining a different facet of the teaching strategy, to provide comprehensive guidance for AI model training.**
4.  **As a content creator, I want a clear visual distinction between 'student' and 'AITA' turns in the editor, and to easily edit their respective utterances and metadata.**
5.  **As an author, I want to save my work progressively and finally export the complete dialogue as a single, valid AITA JSON file that conforms to the project's defined enhanced schema.**
6.  **As an AI trainer, I want to specify placeholder values or examples for fields like `xapi_verb_id`, `ontology_concept_tags`, and `safeguard_tags` within AITA turns, to guide future automated tagging or to provide context for model behavior.**
7.  **As an educator, I want to input or paste the full text of a reading passage directly into the tool when creating a dialogue related to that passage.**

## 3. Core Features & Functionality

### Dialogue Management
*   **Create New Dialogue**: Start a blank dialogue structure based on the enhanced AITA JSON schema.
*   **Load Dialogue**: Import an existing AITA JSON file into the tool for editing.
*   **Save Dialogue**: Export the current dialogue in the tool to a valid AITA JSON file.
*   **Auto-Save/Drafts (Future)**: Periodically save drafts locally to prevent data loss.
*   **List/Browse Dialogues (Conceptual - V2+ Tool)**: Interface to browse and manage a collection of dialogue files within a project directory.

### Context Definition Section
This section allows users to define the overall context and metadata for the dialogue.
*   **Global Dialogue Metadata**:
    *   `dialogue_id`: (Editable Text Input, with suggestion for unique ID)
    *   `version`: (Text Input, e.g., "1.4_enhanced_authoring_tool_v1")
    *   `metadata.original_source_content_id`: (Text Input, e.g., passage ID from a source database)
    *   `metadata.original_source_dataset`: (Text Input, e.g., "Project Gutenberg Custom Selection")
    *   `metadata.tags`: (Comma-separated Text Input or Tagging UI)
    *   `metadata.tool_source`: (Read-only or pre-filled, e.g., "AITA_Authoring_Tool_V1")
*   **`aita_profile`**:
    *   `subject`: (Text Input or Dropdown)
    *   `grade_level`: (Text Input or Dropdown)
    *   `persona_name`: (Text Input)
    *   `target_audience_description`: (Text Area)
*   **`pedagogical_intent`**:
    *   `interaction_type`: (Text Input or Dropdown of common types)
    *   `learning_objectives`: (Dynamic List of Objects) Each LO with:
        *   `id`: (Text Input, e.g., "RC.4.LO1.MainIdea")
        *   `text`: (Text Area for LO description)
    *   `expected_student_thinking_process`: (Text Area)
    *   `keywords`: (Comma-separated Text Input or Tagging UI)
    *   `difficulty_level`: (Text Input or Dropdown)
*   **`context_provided_to_aita`**:
    *   `user_id`: (Text Input, placeholder for typical use, e.g., "generic_student_for_authoring")
    *   `session_id`: (Text Input, placeholder, e.g., "authoring_session_datetime")
    *   `content_item_id`: (Text Input, maps to passage ID)
    *   `content_item_title`: (Text Input)
    *   `content_item_text`: (Large Text Area for pasting or typing full passage text)
    *   Other fields like `prior_knowledge_level`, `prior_performance_summary` as text areas for conceptual input.

### Dialogue Turn Editor
A dynamic interface to construct the sequence of utterances.
*   **Controls**: Buttons to "Add AITA Turn," "Add Student Turn," "Delete Selected Turn," "Move Turn Up/Down."
*   **Turn Display**: Turns listed sequentially, perhaps with alternating visual styles for AITA and student.
*   **For each turn**:
    *   `turn_id`: (Read-only, automatically generated, e.g., `dialogue_id_turn_N`)
    *   `speaker`: (Dropdown: "AITA" / "student")
    *   `timestamp_utc`: (Read-only, placeholder like "YYYY-MM-DDTHH:MM:SSZ_AUTHORING")
    *   `utterance_modality`: (Fixed to "text" for V1)
    *   `utterance`: (Text Area, main input for what the speaker says)
    *   **AITA Turn Specific Fields** (only visible if speaker is "AITA"):
        *   `pedagogical_notes`: (Text Area, supporting multi-line input. Future: allow adding multiple distinct notes with IDs).
        *   `confidence_score_aita`: (Optional Float Input, 0.0-1.0)
        *   `safeguard_tags`: (Comma-separated Text Input or basic Tagging UI)
        *   `xapi_verb_id`: (Text Input, placeholder for URI)
        *   `xapi_object_id`: (Text Input, placeholder for URI)
        *   `ontology_concept_tags`: (Comma-separated Text Input or basic Tagging UI)

### Metadata & Assessment Sections
Input fields for concluding sections of the AITA JSON.
*   **`final_assessment_of_student_understanding`**:
    *   `summary_of_understanding`: (Text Area)
    *   `mastery_level_per_lo`: (Text Area - for V1, user manually types LO ID and level; Future: link to LOs defined above).
    *   `next_steps_recommendation`: (Text Area)
*   **`session_metadata_for_teacher_oversight`**:
    *   `session_duration_seconds`: (Integer Input - conceptual, as this is runtime data)
    *   `flags_for_teacher_review`: (Comma-separated Text Input or Tagging UI)
    *   `session_summary_notes`: (Text Area)

### Validation
*   **Conceptual**: Note that future versions should include client-side validation (e.g., checking for required fields, basic format of URIs for xAPI fields, JSON validity before export). For V1, primary validation is on export to valid JSON.

## 4. UI/UX Design (Conceptual Description)

A potential layout for a web-based Streamlit application (or a more dedicated web app):

*   **Layout**: A multi-column layout could be effective.
    *   **Left Column (or Tab 1)**: **Dialogue Metadata Panel**. Contains all input fields for global dialogue information: `dialogue_id`, `metadata`, `aita_profile`, `pedagogical_intent`, and `context_provided_to_aita` (including the large text area for `content_item_text`).
    *   **Center/Right Column (or Tab 2)**: **Turns Editor Panel**.
        *   Displays the list of dialogue turns. Each turn could be a card-like element showing speaker, utterance snippet, and an "Edit" button.
        *   Controls for adding/reordering turns would be above or below this list.
        *   Clicking "Edit" on a turn or "Add Turn" could open a modal dialog or an inline expandable form for editing that turn's details (speaker, utterance, and AITA-specific fields if applicable).
    *   **Right Column (or Tab 3)**: **Assessment & Session Notes Panel**. Contains input fields for `final_assessment_of_student_understanding` and `session_metadata_for_teacher_oversight`.

*   **AITA Turn Specific Fields**: When editing an AITA turn, the modal/form would clearly show dedicated text areas for `pedagogical_notes`. Fields like `safeguard_tags`, `xapi_verb_id`, `ontology_concept_tags` would be simple text inputs for V1.
*   **Passage Input**: The `content_item_text` field within the `context_provided_to_aita` section will be a large `st.text_area` allowing authors to paste or type the full passage text.
    *   *Future Concept*: A "Passage Library" feature could allow users to select from pre-loaded or previously entered passages.
*   **Ontology/Keyword Tagging UI (Conceptual for V1)**:
    *   For fields like `metadata.tags`, `pedagogical_intent.keywords`, and `dialogue_turns[X].ontology_concept_tags`, a simple comma-separated text input is sufficient for V1.
    *   *Future Concept*: These could be enhanced with auto-suggestion features if linked to a live ontology or keyword database, or a multi-select dropdown populated from a predefined list.

*   **Workflow**:
    1.  **Start**: User clicks "Create New Dialogue" or "Load Dialogue from JSON".
    2.  **Edit Metadata**: User fills in/edits information in the Dialogue Metadata Panel. The `content_item_text` (passage) is a key part of this.
    3.  **Author Turns**: User adds and edits AITA and student turns in the Turns Editor Panel.
    4.  **Add Assessment Info**: User fills in the conceptual `final_assessment_of_student_understanding` and `session_metadata_for_teacher_oversight`.
    5.  **Save/Export**: User clicks "Save Dialogue to JSON" to export the complete AITA JSON file.

## 5. Data Model for Tool & Export Format

*   **Internal Data Model**: The authoring tool will internally manage the dialogue data using a Python dictionary (or a class structure) that directly mirrors the **enhanced AITA JSON structure** as defined in `DataStrategy.md` and refined in `data_processing_scripts.py`.
*   **Export Format**: The primary (and only, for V1) export format will be the exact AITA JSON structure. This ensures that the output of the tool is directly usable as training data for fine-tuning AITAs and is compatible with other components of the ecosystem (e.g., for analysis or simulation).

This conceptual design provides a foundation for building a user-friendly tool that empowers educators to contribute directly to the creation of rich, pedagogically sound AITA training data.
