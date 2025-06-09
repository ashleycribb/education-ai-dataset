# AITA Data Pipeline Integration: Authoring Tool & Fine-Tuning

## 1. Introduction

### Purpose
This document explains how dialogues created with the `aita_dialogue_authoring_tool.py` integrate into the data pipeline for fine-tuning AI Tutors (AITAs). It also clarifies how programmatically generated dialogues (from `data_processing_scripts.py`) can be imported into the authoring tool for review and refinement.

The goal is to ensure a consistent data format throughout the AITA content creation and training lifecycle, enabling flexibility and collaboration between educators and AI trainers.

## 2. Workflow 1: Authoring Tool -> Fine-Tuning

This workflow describes the process of creating dialogues with the authoring tool and using them to fine-tune an AITA model.

1.  **Author/Edit Dialogue**:
    *   An educator, curriculum specialist, or SME uses the `aita_dialogue_authoring_tool.py` (Streamlit application) to create a new AITA dialogue or load and edit an existing one.
    *   They populate all relevant fields, including global dialogue metadata, AITA profile, pedagogical intent, context (e.g., passage text), and the sequence of dialogue turns with utterances and pedagogical notes.

2.  **Save Dialogue as AITA JSON**:
    *   The author saves their work from the tool, which exports it as a single JSON file (e.g., `my_authored_dialogue.json`).
    *   This file strictly adheres to the **enhanced AITA JSON structure** defined in `DataStrategy.md` and implemented by the `get_new_dialogue_template()` function in the authoring tool.

3.  **Collect and Aggregate Authored Dialogues**:
    *   Multiple JSON files, each representing a single dialogue, are collected.
    *   These individual JSON objects are then combined into a single JSON file where the root is a list of these dialogue objects (e.g., `authored_dataset.json`). This step might involve a simple script to read multiple files and append their content to a list, then save that list.

4.  **Split Dataset**:
    *   The `split_dataset.py` script is used to divide `authored_dataset.json` (or any dataset in the correct list-of-dialogues format) into training, validation, and (optionally) test splits.
    *   This produces files like `train_split.json` and `validation_split.json`.

5.  **Fine-Tune AITA Model**:
    *   The `fine_tune_aita.py` script is configured to use the generated split files (e.g., `dataset_path` is set to `train_split.json`, and `eval_dataset_path` to `validation_split.json` if evaluation is used).
    *   The `load_and_prepare_dataset` function within `fine_tune_aita.py` reads these JSON files.
    *   The `format_dialogue_for_sft` function processes the `dialogue_turns` from each dialogue object, preparing them in the format expected by the `SFTTrainer` (typically a single string per dialogue, formatted using the SLM's chat template).

## 3. Workflow 2: Programmatic Generation -> Authoring Tool (for Refinement)

This workflow allows for programmatically generated dialogues to be reviewed and improved using the authoring tool.

1.  **Generate "Gold Standard" or Template Dialogues**:
    *   The `data_processing_scripts.py` script is used to generate initial dialogue datasets (e.g., `pilot_dataset_reading_compre_v1_iter1.json`, `eco_explorer_aita_sample_data_iter1.json`).
    *   These dialogues are also created in the **enhanced AITA JSON structure**.

2.  **Import into Authoring Tool**:
    *   An educator or SME can use the "Load AITA Dialogue JSON" feature in `aita_dialogue_authoring_tool.py`.
    *   They can select an individual dialogue JSON file that was either programmatically generated or previously authored. (Note: If `data_processing_scripts.py` outputs a list of dialogues in one file, a single dialogue object would need to be extracted first to be loaded into the V1 authoring tool, or the tool enhanced to pick one from a list). *For V1, assume loading individual dialogue JSONs.*

3.  **Review, Edit, and Refine**:
    *   The loaded dialogue is displayed in the authoring tool's interface.
    *   The user can then review all fields, edit utterances, refine pedagogical notes, add or remove turns, and adjust any metadata.

4.  **Save/Export Refined Dialogue**:
    *   The modified dialogue can be saved as a new JSON file from the authoring tool, again in the standard enhanced AITA JSON format. This refined dialogue can then be reintegrated into datasets for fine-tuning.

## 4. Data Format Consistency

**Crucially, both `data_processing_scripts.py` (for its "gold standard" and iteration 1 generated examples) and the `aita_dialogue_authoring_tool.py` (as its primary output format) are designed to produce data that adheres to the same enhanced AITA JSON structure.**

This consistency ensures interoperability within the data pipeline:

*   **`dialogue_turns`**: This field in the JSON is always a list of turn objects.
*   **`pedagogical_notes`**: Within each AITA turn object in `dialogue_turns`, the `pedagogical_notes` field is consistently a **`List[str]`** (a list of strings). Each string in the list represents a distinct pedagogical annotation for that turn. The authoring tool uses a text area with newline separation for input, which is then parsed into this list structure.
*   **Other list-based tag fields** (e.g., `metadata.tags`, `pedagogical_intent.keywords`, `dialogue_turns[X].safeguard_tags`, `dialogue_turns[X].ontology_concept_tags`) are also handled as lists of strings (typically from comma-separated input in the V1 authoring tool).

This uniform data structure ensures that `fine_tune_aita.py` can reliably process datasets originating from either programmatic generation or manual authoring/refinement through the tool, without requiring different parsing logic for the `dialogue_turns` and their contents.

## 5. Conceptual Review of Data Format Consistency (Authoring Tool & Fine-Tuning Script)

*   **Authoring Tool Output (`st.session_state.current_dialogue`)**:
    *   The `get_new_dialogue_template()` function in `aita_dialogue_authoring_tool.py` initializes `dialogue_turns` as `[]`.
    *   The `add_turn_callback` function appends new turn dictionaries, and for AITA turns, initializes `pedagogical_notes: []`, `safeguard_tags: []`, etc.
    *   When editing, `pedagogical_notes` are input into a `st.text_area` (one note per line) and then processed into a `List[str]` using `[note.strip() for note in ped_notes_str.split('\n') if note.strip()]`.
    *   Similarly, comma-separated tags are processed into `List[str]`.
    *   The structure saved via the "Save Dialogue as JSON" button will therefore correctly have `pedagogical_notes` and other tag fields as lists of strings.

*   **Fine-Tuning Script Input (`format_dialogue_for_sft` in `fine_tune_aita.py`)**:
    *   The `format_dialogue_for_sft` function in `fine_tune_aita.py` accesses `dialogue_turns` using `example.get('dialogue_turns', [])`. This correctly handles cases where `dialogue_turns` might be missing (though the authoring tool template ensures it's present).
    *   Inside the loop, it accesses `turn.get("speaker", "").lower()` and `turn.get("utterance", "")`. These fields are correctly structured by the authoring tool.
    *   The `pedagogical_notes` field itself is not directly used by `format_dialogue_for_sft` to create the input string for the SLM (which is built from speaker roles and utterances). Its format as `List[str]` is primarily for data storage, analysis, and potential future use by more advanced fine-tuning techniques or for human review. The current SFT process primarily relies on the structured dialogue (speaker roles and utterances) for training.

*   **Compatibility Confirmation**:
    *   The data structure produced by `aita_dialogue_authoring_tool.py` (with `pedagogical_notes` as `List[str]` and other tag fields as `List[str]`) is **compatible** with the expectations of `format_dialogue_for_sft` in `fine_tune_aita.py`.
    *   The SFT script correctly extracts the necessary `speaker` and `utterance` fields from the `dialogue_turns` list. The fact that `pedagogical_notes` or other metadata fields exist within the turn objects does not interfere with this process.
    *   Default empty lists (`[]`) for `pedagogical_notes` or tags in the authoring tool's template or if a user leaves them blank will also be handled gracefully by `format_dialogue_for_sft` (as it only uses speaker/utterance) and by any downstream analysis tools (which should expect these fields to potentially be empty lists).

*   **Minor Adjustments/Considerations**:
    *   No immediate adjustments seem necessary in `format_dialogue_for_sft` to handle the authoring tool's output. The use of `.get()` and providing default empty lists/strings in data generation and processing makes the pipeline robust to fields that might occasionally be empty (though the authoring tool template aims for completeness).
    *   The `dialogue_version` in `get_new_dialogue_template()` was set to `"1.5_AITA_AuthoringTool_V1"`. This is distinct from the version in `data_processing_scripts.py` (`"1.4_enhanced_iter1_..."`). This is acceptable as it indicates the source and version of the *schema/tool* that generated the data. Consumers of the data should primarily be concerned with the presence and structure of expected fields like `dialogue_turns`.

The data pipeline appears consistent and robust for integrating dialogues from both programmatic generation and the new authoring tool into the fine-tuning process.
