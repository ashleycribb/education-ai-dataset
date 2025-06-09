# AITA Interaction Service: README Notes

## Overview

This document provides brief notes on building and running the `aita_interaction_service.py` using Docker, and how to test its endpoints.

This service uses FastAPI to provide an API for interacting with a Small Language Model (SLM) to simulate an AI Tutor (AITA). It includes basic user profile management, content moderation, simulated LMS context, xAPI logging, and conceptual support for loading different AITA personas (fine-tuned models/adapters).

## Building the Docker Image

1.  **Ensure Docker is installed** on your system.
2.  Make sure you have the following files and directories in your build context (e.g., the root of the project where you run `docker build`):
    *   `aita_interaction_service.py`
    *   `moderation_service.py`
    *   `k12_mcp_client_sdk/` (directory containing at least `xapi_utils.py` and `__init__.py`)
    *   `Dockerfile`
    *   *(Optional but recommended for production: `requirements.txt`)*
3.  Open your terminal, navigate to this directory.
4.  Run the Docker build command:

    ```bash
    docker build -t aita-service:latest .
    ```
    *   The `.` indicates that the build context is the current directory.
    *   This command will use the instructions in the `Dockerfile` to build the image.
    *   The `Dockerfile` installs PyTorch for CPU. For GPU support, the Dockerfile and base image would need adjustment.
    *   Placeholder adapter directories (`/app/adapters/*`) are created within the image so the service can start even if actual adapter files are not yet mounted or copied.

## Running the Docker Container

1.  Once the image is built, you can run it as a container:

    ```bash
    docker run -d -p 8000:8000 \
           -v $(pwd)/service_xapi_statements.jsonl:/app/service_xapi_statements.jsonl \
           --name aita_interaction_container aita-service:latest
    ```
    *   `-d`: Runs the container in detached mode.
    *   `-p 8000:8000`: Maps port 8000 of the host to port 8000 of the container.
    *   **`-v $(pwd)/service_xapi_statements.jsonl:/app/service_xapi_statements.jsonl`**: (Optional, but recommended for persistence) Mounts a local file into the container for xAPI log persistence. Ensure `service_xapi_statements.jsonl` exists locally first (e.g., `touch service_xapi_statements.jsonl`) or adjust the mount. Without this, logs will be lost when the container stops.
    *   `--name aita_interaction_container`: Assigns a name to the container.
    *   `aita-service:latest`: Specifies the image.
    *   **Note on Adapters**: To use actual fine-tuned LoRA adapters, you would need to mount your local adapter directories into the corresponding paths inside the container (e.g., `-v $(pwd)/my_local_adapters/reading_explorer_pilot1:/app/adapters/reading_explorer_pilot1`).

2.  **To view logs from the running container:**
    ```bash
    docker logs aita_interaction_container -f
    ```

3.  **To stop and remove the container:**
    ```bash
    docker stop aita_interaction_container
    docker rm aita_interaction_container
    ```

## Testing Endpoints

### User Profile Endpoints (`/users/register`, `/users/{user_id}`)
These endpoints function as previously described for creating and retrieving user profiles. The `user_id` obtained from registration is used in the `/interact` endpoint.

**Example: Register User**
```bash
curl -X POST "http://localhost:8000/users/register" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "student_ada_lovelace",
           "grade_level": 7,
           "preferred_aita_persona_id": "EcoExplorerAITA_7thGrade_Pilot1"
         }'
```
*(Save the returned `user_id` for the next step.)*

### `/interact` Endpoint (POST)

*   **Purpose**: Main endpoint for interacting with an AITA.
*   **Key Request Fields**:
    *   `user_id`: The registered ID of the user.
    *   `aita_persona_id`: Specifies which AITA persona (and potentially fine-tuned adapter) to use. Examples:
        *   `"default_phi3_base"` (uses the base SLM without specific adapters).
        *   `"ReadingExplorerAITA_4thGrade_Pilot1"` (attempts to load adapter from `/app/adapters/reading_explorer_pilot1`).
        *   `"EcoExplorerAITA_7thGrade_Pilot1"` (attempts to load adapter from `/app/adapters/eco_explorer_pilot1`).
        *   If an adapter for the given `aita_persona_id` is not found or fails to load, the service falls back to the base model for that persona.
    *   `user_utterance`: The text input from the user.
    *   `conversation_history`: (Optional) A list of previous turns in the format `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`.
    *   `subject`, `current_item_id`: (Optional) Used to fetch specific simulated LMS context from the service's internal `MOCK_DB`. If not provided, a default context for the user might be sought.

*   **Example `curl` command** (using a `user_id` from registration, e.g., "generated_uuid_for_ada"):
    ```bash
    # Assuming "generated_uuid_for_ada" is the user_id for student_ada_lovelace
    # This example uses the preferred_aita_persona_id set during registration for Ada.
    # The service will attempt to load "EcoExplorerAITA_7thGrade_Pilot1".
    # We also specify subject and item_id to get specific context.
    curl -X POST "http://localhost:8000/interact" \
         -H "Content-Type: application/json" \
         -d '{
               "user_id": "generated_uuid_for_ada",
               "aita_persona_id": "EcoExplorerAITA_7thGrade_Pilot1",
               "user_utterance": "What is a food web?",
               "conversation_history": [],
               "subject": "Ecology",
               "current_item_id": "eco_passage_foodweb_001"
             }'
    ```

*   **Key Features Demonstrated in Response & Logs**:
    *   **Contextual System Prompt**: The SLM's system prompt is now dynamically built using (simulated) LMS context fetched based on `user_id`, `subject`, and `item_id`.
    *   **Moderation**: Both user input and AITA raw output are checked by `ModerationService`. Results are logged. If input is unsafe, a polite refusal is returned. If output is unsafe, a generic safe message is returned.
    *   **xAPI Logging**: Interactions are logged to `service_xapi_statements.jsonl` inside the container (or the mounted file if `-v` is used). These logs include moderation details and the full prompt sent to the LLM.
    *   **Persona/Adapter Loading**: The `debug_info` in the response will indicate the `aita_persona_resolved` and if a user profile was found. Server logs will show attempts to load specific adapters.

**Example Response (Conceptual for Eco Explorer):**
```json
{
  "session_id": "some-new-uuid-string",
  "aita_response": "A food web shows how energy moves through an ecosystem! For example, the sun gives energy to plants. What do you think eats the plants in a forest?",
  "debug_info": {
    "model_used": "microsoft/Phi-3-mini-4k-instruct", // Or path to adapter if loaded
    "aita_persona_resolved": "EcoExplorerAITA_7thGrade_Pilot1",
    "user_profile_found": true,
    "lms_context_found": true
  }
}
```

These notes provide an updated outline for deploying and testing the enhanced AITA Interaction Service. Remember to check server logs for details on model/adapter loading and interaction processing.
