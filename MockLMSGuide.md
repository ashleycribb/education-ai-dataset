# Mock LMS MCP Server Guide (`lms_mcp_server_mock.py`)

## 1. Overview

### Purpose
The `lms_mcp_server_mock.py` script simulates a basic Learning Management System (LMS) or other educational platform. Its primary function is to provide contextual information to AI Tutors (AITAs) or other educational tools using the Model Context Protocol (MCP). This allows AITAs to tailor their interactions based on the student's current learning activity.

### Primary Use Case
This mock server is intended for **local testing and development** of MCP client applications, such as the `aita_mcp_client.py` developed in this project. It allows developers to simulate an LMS environment without needing a full-fledged LMS instance.

## 2. Environment Setup

### Recommended Python Version
*   Python 3.9 or higher is recommended.

### Main Python Library
The server relies on the `modelcontextprotocol` library.
Install it using pip:
```bash
pip install modelcontextprotocol
```
Ensure any other standard Python libraries used (like `json`, `datetime`) are also available in your environment.

## 3. Running the Mock LMS Server

### Command to Run
Execute the script from your terminal:
```bash
python lms_mcp_server_mock.py
```

### StdIO Mode Operation
*   The server operates in **stdio mode**. This means it listens for MCP requests on its standard input (stdin) and sends MCP responses to its standard output (stdout).
*   It does not open any network ports.

### Usage with Piping
This stdio operation is designed for use with command-line pipes, where the output of the server is directly fed as input to an MCP client, and vice-versa.
```bash
python lms_mcp_server_mock.py | python aita_mcp_client.py
```
In this example:
*   `lms_mcp_server_mock.py` sends its responses (MCP messages) to `aita_mcp_client.py`.
*   `aita_mcp_client.py` sends its requests (MCP messages) to `lms_mcp_server_mock.py`.

## 4. Understanding the Mock Data (`MOCK_DB`)

The script contains an in-memory Python dictionary named `MOCK_DB` that serves as its database.

### `student_activity_contexts`
This is the primary data store used by the server. It's a dictionary where:
*   **Keys** are strings constructed by concatenating `student_id`, `subject`, and `item_id`.
    *   Example key: `"student001_ReadingComprehension_passage_kitten_001"`
*   **Values** are dictionaries representing the specific context for that student and activity. Important fields include:
    *   `student_id_anonymized`: (e.g., "student001")
    *   `subject`: (e.g., "ReadingComprehension", "Ecology")
    *   `current_passage_id` or `current_item_id`: The ID of the content item (e.g., "passage_kitten_001").
    *   `current_passage_title` or `current_item_title`: The title of the content.
    *   `current_passage_text_snippet` or `current_item_text_snippet`: A short preview of the content.
    *   `target_learning_objectives_for_activity`: A list of learning objectives associated with the activity, each an object with `lo_id` and `description`.
        ```json
        [
            {"lo_id": "RC.4.LO1.MainIdea.Narrative", "description": "Identify the main idea..."},
            {"lo_id": "RC.4.LO3.Vocabulary", "description": "Determine the meaning of 'cozy'..."}
        ]
        ```
    *   `recent_attempts_on_this_lo_or_passage`: An integer count.
    *   `teacher_notes_for_student_on_lo`: Optional teacher-provided notes specific to the student and LO.

### Source Passages
*   The content for fields like `current_passage_title` and `current_passage_text_snippet` is derived from global lists within the script, such as:
    *   `DEFAULT_4TH_GRADE_PASSAGES`
    *   `DEFAULT_7TH_GRADE_SCIENCE_PASSAGES`
*   The `get_passage_snippet` helper function is used to extract a short preview from the full passage text.

## 5. Adding or Modifying Mock Data

You can customize the context provided by the mock server by directly editing `lms_mcp_server_mock.py`:

1.  **Add New Passage Details (Optional)**:
    *   If your new context refers to a new passage, add its details to the relevant list (e.g., `DEFAULT_4TH_GRADE_PASSAGES` or `DEFAULT_7TH_GRADE_SCIENCE_PASSAGES`). Each passage is a dictionary:
        ```python
        # Example for DEFAULT_4TH_GRADE_PASSAGES:
        {
            "id": "passage_new_story_001",
            "title": "The Brave Little Ant",
            "text": "Once upon a time, a little ant named Andy found a giant crumb..."
        }
        ```

2.  **Add New Student Activity Context**:
    *   Locate the `MOCK_DB` dictionary in the script.
    *   Navigate to the `student_activity_contexts` sub-dictionary.
    *   Add a new key-value pair. The key must follow the format: `"{student_id}_{subject}_{item_id}"`.
    *   The value should be a dictionary containing all the necessary fields described in Section 4.

    **Example of adding a new context for "student003" for a new reading passage "passage_new_story_001"**:
    ```python
    # Inside MOCK_DB["student_activity_contexts"]:
    "student003_ReadingComprehension_passage_new_story_001": {
        "student_id_anonymized": "student003",
        "subject": "ReadingComprehension",
        "current_passage_id": "passage_new_story_001",
        "current_passage_title": "The Brave Little Ant", # Assuming added to DEFAULT_4TH_GRADE_PASSAGES
        "current_passage_text_snippet": get_passage_snippet("Once upon a time, a little ant named Andy found a giant crumb..."),
        "target_learning_objectives_for_activity": [
            {"lo_id": "RC.4.LO.CharacterTraits", "description": "Identify character traits based on actions."}
        ],
        "recent_attempts_on_this_lo_or_passage": 0,
        "teacher_notes_for_student_on_lo": "Think about what Andy does in the story!"
    },
    ```
3.  **Restart the Server**: After saving your changes to `lms_mcp_server_mock.py`, you'll need to stop and restart it for the changes to take effect.

## 6. MCP Resource Served

The mock server currently exposes one primary resource endpoint:

*   **Resource Path**: `/student/{student_id}/activity_context`
*   **Path Parameters**:
    *   `{student_id}`: (String) The unique identifier for the student (e.g., "student001", "student002").
*   **Query Parameters**:
    *   `subject`: (String) The subject area of the activity (e.g., "ReadingComprehension", "Ecology", "Mathematics").
    *   `item_id`: (String) The unique identifier for the specific content item or activity (e.g., "passage_kitten_001", "eco_passage_foodweb_001", "topic_fractions_intro").
*   **Successful Response (Status 200)**:
    *   If a context matching the combined key (`{student_id}_{subject}_{item_id}`) is found in `MOCK_DB`, the server returns a JSON payload containing the context object. Example structure:
        ```json
        {
            "student_id_anonymized": "student001",
            "subject": "ReadingComprehension",
            "current_passage_id": "passage_kitten_001",
            "current_passage_title": "Lily the Lost Kitten",
            "current_passage_text_snippet": "Lily the little kitten was lost. She wandered through tall grass and over a bumpy road....",
            "target_learning_objectives_for_activity": [
                {"lo_id": "RC.4.LO1.MainIdea.Narrative", "description": "Identify the main idea..."},
                {"lo_id": "RC.4.LO3.Vocabulary", "description": "Determine the meaning of 'cozy'..."}
            ],
            "recent_attempts_on_this_lo_or_passage": 2,
            "teacher_notes_for_student_on_lo": "Remember to look for both the problem and how it's solved..."
        }
        ```
*   **Error Responses**:
    *   **Status 400 (Bad Request)**: If required path or query parameters (`student_id`, `subject`, `item_id`) are missing. The payload will contain an error message.
    *   **Status 404 (Not Found)**: If no context is found in `MOCK_DB` for the constructed key. The payload will contain an error message.

## 7. Interaction with `aita_mcp_client.py`

The `aita_mcp_client.py` script is designed to interact with this mock LMS server.
*   When `aita_mcp_client.py` starts, it uses its `DEFAULT_STUDENT_ID`, `DEFAULT_SUBJECT`, and `DEFAULT_ITEM_ID` variables (defined at the top of that script) to make a request to the `/student/{student_id}/activity_context` endpoint of the `lms_mcp_server_mock.py`.
*   The context received from the mock server is then used by `aita_mcp_client.py` to tailor its system prompt and initial greeting, simulating how a real AITA would adapt to information from an LMS.

By modifying the `MOCK_DB` in the server and the default request parameters in the client, you can simulate various student and activity contexts for testing.
