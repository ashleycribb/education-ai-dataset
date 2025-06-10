# AITA Ecosystem: Data Strategy and Interoperability

## 1. Introduction

### Purpose
This document details the key data structures, schemas, and interoperability strategies employed within the AI Tutor (AITA) ecosystem. It aims to provide a clear understanding of how data is organized, generated, logged, and utilized across different components of the project.

### Importance of Structured Data
Structured data is foundational to the AITA project for several reasons:
*   **Effective AITA Training**: Well-structured dialogue data allows for more effective fine-tuning of Small Language Models (SLMs) to create specialized AITAs that align with pedagogical goals.
*   **Interoperability**: Standardized data formats enable different components (AITA client, mock LMS, dashboard, future services) to communicate and exchange information reliably.
*   **Analytics and Research**: Consistent data logging (e.g., xAPI-like statements) facilitates learning analytics, educational research, and iterative improvement of AITA performance and pedagogical strategies.
*   **Scalability and Extensibility**: Clear data schemas allow the system to be extended to new subjects, grade levels, and functionalities more easily.

## 2. AITA Fine-Tuning Data Structure

The primary dataset for fine-tuning AITAs (e.g., `gold_standard_reading_compre_aita_data.json`, `eco_explorer_aita_sample_data.json`) uses an enhanced AITA JSON format. Each JSON object in this dataset represents a complete pedagogical dialogue.

**Main Top-Level Objects and Purpose:**

*   **`dialogue_id`**: (String) A unique identifier for the entire dialogue (e.g., "gold\_std\_kitten\_main\_idea\_001").
*   **`version`**: (String) Version of the AITA JSON schema being used (e.g., "1.3\_enhanced\_gold\_standard\_pilot").
*   **`creation_timestamp_utc`**: (String) ISO 8601 timestamp indicating when the dialogue data was created.
*   **`last_updated_timestamp_utc`**: (String) ISO 8601 timestamp for the last modification.
*   **`metadata`**: (Object) Information about the data record itself.
    *   `original_source_content_id`: ID of the base content item (e.g., passage ID).
    *   `original_source_dataset`: Name of the source dataset for the content.
    *   `tags`: List of keywords for categorizing and searching (e.g., "reading comprehension", "4th grade", "main idea").
    *   `tool_source`: Name of the script or process that generated this data object.
*   **`aita_profile`**: (Object) Describes the AITA persona and target audience.
    *   `subject`: (e.g., "Reading Comprehension", "Science").
    *   `grade_level`: (e.g., "4", "7").
    *   `persona_name`: (e.g., "ReaderAITA\_Explorer\_v1.3\_Pilot").
    *   `target_audience_description`: A brief description of the intended student.
*   **`pedagogical_intent`**: (Object) Defines the educational goals of the dialogue.
    *   `interaction_type`: Specific pedagogical approach (e.g., "guided\_discovery\_main\_idea\_narrative").
    *   `learning_objectives`: List of objects, each with `id` and `text` describing the LO.
    *   `expected_student_thinking_process`: Description of the cognitive steps the student is expected to take.
    *   `keywords`: Pedagogical and domain-specific keywords.
    *   `difficulty_level`: (e.g., "4th\_grade\_on\_level").
*   **`context_provided_to_aita`**: (Object) Information that would typically be provided to the AITA by an LMS or similar platform at the start of an interaction.
    *   `user_id`: Anonymized student identifier.
    *   `session_id`: Unique ID for the learning session.
    *   `prior_knowledge_level`, `prior_performance_summary`: Information about the student's past interactions.
    *   `learning_context_description`: Description of the current learning activity.
    *   `content_item_id`, `content_item_title`, `content_item_text`: Details of the specific educational content (e.g., a reading passage).
*   **`dialogue_turns`**: (List of Objects) The core of the dialogue, containing each turn of the conversation.
*   **`final_assessment_of_student_understanding`**: (Object) An overall assessment of the student's grasp of the learning objectives after the dialogue.
    *   `summary_of_understanding`: Textual summary.
    *   `mastery_level_per_lo`: List indicating mastery for each LO (e.g., "demonstrated\_with\_scaffolding").
    *   `next_steps_recommendation`: Suggested follow-up activities.
*   **`session_metadata_for_teacher_oversight`**: (Object) Information useful for teacher review.
    *   `session_duration_seconds`: Total duration of the interaction.
    *   `engagement_metrics`: Turn counts.
    *   `flags_for_teacher_review`: Any automated flags (e.g., "student\_struggled\_repeatedly").
    *   `session_summary_notes`: Brief notes for the teacher.

**Key Sub-fields within `dialogue_turns`:**
Each object in the `dialogue_turns` list represents one utterance and its associated metadata:
*   `turn_id`: (String) Unique identifier for the turn within the dialogue.
*   `speaker`: (String) "AITA" or "student".
*   `timestamp_utc`: (String) ISO 8601 timestamp for the turn.
*   `utterance_modality`: (String) Typically "text" for current SLMs.
*   `utterance`: (String) The text spoken by the speaker.
*   `confidence_score_aita`: (Float, Optional, for AITA turns) The AITA's confidence in its response (0.0-1.0).
*   `pedagogical_notes`: (List of Strings, for AITA turns) **Crucial field**. A list of notes, each explaining a specific teaching strategy, intent, or reasoning behind the AITA's utterance in that turn. Supports the "teach how to learn" philosophy by making the AITA's pedagogy explicit and allowing for multiple facets of a strategy to be documented for a single turn.
*   `aita_turn_narrative_rationale`: (String, for AITA turns, Optional) A concise (1-2 sentence) human-readable summary of the AITA's primary pedagogical intent or strategy for this specific turn. Useful for quick review in teacher dashboards and for potentially informing student-facing explanations of AITA reasoning.
*   `safeguard_tags`: (List of Strings, Conceptual) Tags indicating safety checks passed (e.g., "safe", "on-topic", "age\_appropriate\_language").
*   `xapi_verb_id`: (String, Conceptual) A URI for an xAPI verb representing the primary action of the turn (e.g., "http://adlnet.gov/expapi/verbs/asked", "http://adlnet.gov/expapi/verbs/responded").
*   `xapi_object_id`: (String, Conceptual) A unique URI for the object of the xAPI statement related to this turn.
*   `ontology_concept_tags`: (List of Strings, Conceptual) Tags linking the turn to concepts in the educational ontology (e.g., "main\_idea\_elicitation", "scaffolding\_question", "student\_identifies\_problem").

The `pedagogical_notes` and `aita_turn_narrative_rationale` fields are key components supporting the **AITA Reasoner** feature, which aims to provide transparency into the AITA's pedagogical decision-making.

This structured format is designed to:
*   Provide rich context for fine-tuning the SLM.
*   Explicitly encode pedagogical strategies in `pedagogical_notes`, aiding in training AITAs that "teach how to learn."
*   Support future integrations with xAPI-compliant LRSs and detailed analytics through fields like `xapi_verb_id` and `ontology_concept_tags`.

## 3. Conceptual Educational Ontology

A K-12 educational ontology is envisioned to provide a common vocabulary and semantic structure for various data elements within the AITA ecosystem. For the 4th Grade Reading Comprehension use case, this might include:

*   **Key Classes**:
    *   `LearningObjective`: Represents specific learning goals (e.g., "Identify the main idea," "Infer character feelings").
        *   Properties: `lo_id`, `lo_text_description`, `grade_level`, `subject`.
    *   `ReadingSkill` (or more general `Skill`): Specific skills targeted (e.g., "MainIdeaIdentification", "InferentialReasoning", "ContextualVocabulary").
        *   Properties: `skill_name`, `skill_description`.
        *   Relationship: `hasSubSkill`, `relatedSkill`.
    *   `Passage` (or more general `ContentItem`): Represents educational content.
        *   Properties: `passage_id`, `title`, `text_content`, `genre`, `lexile_level` (or other readability score).
        *   Relationship: `targetsLearningObjective`, `exemplifiesSkill`.
    *   `PedagogicalStrategy`: Types of teaching methods used by the AITA.
        *   Properties: `strategy_name` (e.g., "SocraticQuestioning", "Scaffolding", "ThinkAloudPrompt").
        *   Relationship: `appliesToLearningObjective`, `targetsSkill`.
    *   `StudentMisconception`: Common errors or misunderstandings.
        *   Properties: `misconception_description`, `subject_area`.
        *   Relationship: `relatedToLearningObjective`, `addressedByStrategy`.
    *   `DialogueTurnConcept`: Concepts from dialogue theory or pedagogy tagged in turns.
        *   Properties: `concept_name` (e.g., "open_question", "positive_feedback", "student_hypothesis").

*   **Key Properties and Relationships**:
    *   `dialogue_turn.ontology_concept_tags` would link specific utterances to instances or types from `PedagogicalStrategy`, `ReadingSkill`, `StudentMisconception`, or `DialogueTurnConcept`.
    *   `LearningObjective.hasSkill` could link LOs to the skills they aim to develop.
    *   `Passage.targetsLearningObjective` links content to LOs.

*   **Linking `ontology_concept_tags`**: The `ontology_concept_tags` field within each `dialogue_turn` in the AITA JSON is intended to be populated with URIs or standardized string identifiers that refer to concepts defined in this ontology. This allows for deeper semantic analysis of dialogues.

*   **Extensibility**: This ontology can be extended to other subjects (e.g., "ScienceSkill", "MathematicalConcept") and grade levels by adding new classes, properties, and instances. The core structure of linking content, pedagogy, and learning objectives remains applicable.

## 4. Conceptual Vertical Database Schema

A relational or document database would store educational content, such as reading passages and their metadata.

*   **Key Tables (Relational Example)**:
    *   `Passages` (or `ContentItems`):
        *   `passage_id` (Primary Key, e.g., "passage\_kitten\_001")
        *   `title` (String)
        *   `text_content` (Text)
        *   `genre_id` (Foreign Key to `Genres` table)
        *   `grade_level` (Integer)
        *   `readability_score` (Float, e.g., Flesch-Kincaid score)
        *   `source_dataset_id` (String, optional)
        *   `creation_date`, `last_modified_date`
    *   `Genres`:
        *   `genre_id` (Primary Key)
        *   `genre_name` (String, e.g., "Narrative", "Informational Text")
    *   `LearningObjectivesCatalog`:
        *   `lo_catalog_id` (Primary Key, e.g., "RC.4.LO1.MainIdea.Narrative")
        *   `lo_text` (String)
        *   `subject` (String)
        *   `grade_level` (Integer)
    *   `PassageLearningObjectivesLink`: (Many-to-many link table)
        *   `passage_id` (Foreign Key)
        *   `lo_catalog_id` (Foreign Key)
    *   Other tables for `Keywords`, `OntologyTagsPerPassage`, etc.

*   **Linking**: The `content_item_id` (or `passage_id`) used in the AITA JSON, xAPI statements, and MCP server context directly corresponds to `Passages.passage_id` in this database. This allows retrieval of the full passage text and its metadata when needed.

*   **Extensibility**: New tables for different content types (e.g., `MathProblems`, `ScienceSimulations`) can be added. The core idea of linking content items to learning objectives and other metadata remains consistent.

## 5. xAPI Statement Structure & LRS Integration

The `aita_mcp_client.py` script generates interaction data structured similarly to xAPI statements, logged to `xapi_statements.jsonl`.

**Key xAPI Components Used:**

*   **`id`**: (String) A unique UUID for each statement.
*   **`actor`**: (Object) Identifies the user performing the action.
    *   `objectType`: "Agent"
    *   `name`: User-friendly name (e.g., "cli\_user").
    *   `account`: Contains a unique identifier for the user.
        *   `homePage`: A URI for the system the account belongs to (e.g., "http://example.com/cli").
        *   `name`: The unique user ID (e.g., student ID like "student001").
*   **`verb`**: (Object) The action performed.
    *   `id`: A URI defining the verb (e.g., "http://adlnet.gov/expapi/verbs/interacted", "http://adlnet.gov/expapi/verbs/exited").
    *   `display`: A human-readable map of the verb (e.g., `{"en-US": "interacted_with_AITA_turn"}`).
*   **`object`**: (Object) The thing that was acted upon, typically an "Activity".
    *   `objectType`: "Activity"
    *   `id`: A unique URI for the activity (e.g., a specific interaction turn: "http://example.com/aita\_pilot/session/{session\_id}/turn/{turn\_number}").
    *   `definition`: Describes the activity.
        *   `name`: Human-readable name (e.g., `{"en-US": "AITA Interaction Turn"}`).
        *   `description`: More detailed description.
        *   `type`: A URI defining the activity type (e.g., "http://adlnet.gov/expapi/activities/interaction").
        *   `extensions`: Custom data, including `user_utterance_raw` and `aita_response_raw`.
*   **`result`**: (Object, Optional) Outcomes of the activity.
    *   `response`: The final AITA response shown to the user.
    *   `duration`: ISO 8601 formatted duration of the AITA's generation process (e.g., "PT3.15S").
    *   `extensions`: Custom data, including:
        *   `input_moderation_details`: Full JSON object from `ModerationService.check_text()` for user input.
        *   `output_moderation_details`: Full JSON object from `ModerationService.check_text()` for AITA's raw output.
*   **`context`**: (Object, Optional) Additional contextual information.
    *   `contextActivities`: Defines relationships with other activities.
        *   `parent`: List indicating parent activities (e.g., the passage being discussed: `[{"id": "http://example.com/aita_pilot/passage/{passage_id}"}]`).
    *   `extensions`: Custom data, including:
        *   `session_id`: Unique ID for the entire interaction session.
        *   `aita_persona`: Name of the AITA persona.
        *   `learning_objective_active`: ID of the current LO.
        *   `full_prompt_to_llm`: The complete prompt sent to the SLM.
*   **`timestamp`**: (String) ISO 8601 timestamp of when the event occurred.
*   **`authority`**: (Object) Information about who is attesting to the statement's validity (placeholder in current implementation).

**LRS Integration**:
In a production environment, these xAPI-like statements would be sent to a Learning Record Store (LRS). An LRS is a database system specifically designed to store, retrieve, and manage learning activity data formatted as xAPI statements.

**Benefits of LRS Integration**:
*   **Learning Analytics**: Enables detailed analysis of student interactions, learning pathways, common misconceptions, and AITA effectiveness.
*   **Teacher Oversight**: Provides data for dashboards that help teachers monitor student progress and identify areas where students might need additional support.
*   **Research**: Creates a rich dataset for educational research on AI tutoring, student learning, and pedagogical strategies.
*   **Interoperability**: xAPI is a standard, allowing data to potentially be shared or analyzed across different learning systems.

## 6. Teacher Oversight Dashboard Data Usage

The `teacher_dashboard_prototype.py` (Streamlit application) consumes the `xapi_statements.jsonl` file to provide insights:

*   **Loading Data**: The `load_xapi_statements` function reads the JSON Lines file.
*   **Session Summaries (`get_session_summaries`)**:
    *   Uses `context.extensions.http://example.com/xapi/extensions/session_id` to group statements into sessions.
    *   Extracts `actor.account.name` for "Student ID".
    *   Uses the earliest `timestamp` in a session for "Start Time (UTC)".
    *   Counts statements within a session for "Turn Count".
    *   Extracts `object.definition.extensions.http://example.com/xapi/extensions/user_utterance_raw` from the first user turn for "First User Utterance".
*   **Dialogue Transcripts (`get_dialogue_turns_for_session`)**:
    *   Filters statements by the selected `session_id`.
    *   Uses `timestamp` for ordering turns.
    *   Determines `speaker` based on whether `user_utterance_raw` or `result.response` (AITA's final message) is present.
    *   Displays `user_utterance_raw` or `result.response` as the turn's utterance.
    *   **Moderation Details**: Displays `result.extensions.http://example.com/xapi/extensions/input_moderation_details` and `result.extensions.http://example.com/xapi/extensions/output_moderation_details`.
    *   **Raw LLM Response**: Displays `object.definition.extensions.http://example.com/xapi/extensions/aita_response_raw` if it differs from `result.response` (indicating moderation override).
    *   **Full LLM Prompt**: Displays `context.extensions.http://example.com/xapi/extensions/full_prompt_to_llm`.

## 7. Interoperability Goals

The data strategies employed aim for a high degree of interoperability and extensibility:

*   **Model Context Protocol (MCP)**: Standardizes communication between the AITA client and context-providing services (like the mock LMS). This allows different AITAs to connect to various LMSs or content sources that support MCP.
*   **xAPI (Experience API)**: Using an xAPI-like structure for logging interactions prepares the ecosystem for integration with standard LRSs. This promotes data portability and allows for the use of off-the-shelf xAPI-compatible analytics tools.
*   **Educational Ontology (Conceptual)**: Linking dialogue turns and content to a formal ontology would provide a rich semantic layer, enabling more sophisticated queries, reasoning about pedagogical effectiveness, and personalized learning pathways. It would also facilitate sharing and aligning content and strategies across different AITAs and educational domains.

These strategies collectively aim to create a flexible, data-driven, and interconnected ecosystem for developing and deploying effective AI Tutors.
