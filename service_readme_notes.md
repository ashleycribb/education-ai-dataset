# AITA Interaction Service: README Notes

## Overview

This document provides brief notes on building and running the `aita_interaction_service.py` using Docker, and how to test its endpoints.

This service uses FastAPI to provide an API for interacting with a Small Language Model (SLM) to simulate an AI Tutor (AITA). It includes basic user profile management.

## Building the Docker Image

1.  **Ensure Docker is installed** on your system.
2.  Make sure you have the following files in the same directory:
    *   `aita_interaction_service.py`
    *   `Dockerfile`
    *   *(Optional but recommended for production: `requirements.txt`)*
3.  Open your terminal, navigate to this directory.
4.  Run the Docker build command:

    ```bash
    # Conceptual command (replace 'aita-service' with your desired image name)
    docker build -t aita-service:latest .
    ```

    *   The `.` indicates that the build context is the current directory.
    *   This command will use the instructions in the `Dockerfile` to build the image.
    *   The current `Dockerfile` installs PyTorch for CPU. For GPU support, the Dockerfile and base image would need to be adjusted (e.g., using an `nvidia/cuda` base image and installing the GPU-enabled PyTorch version).

## Running the Docker Container

1.  Once the image is built, you can run it as a container:

    ```bash
    # Conceptual command
    docker run -d -p 8000:8000 --name aita_interaction_container aita-service:latest
    ```
    *   `-d`: Runs the container in detached mode (in the background).
    *   `-p 8000:8000`: Maps port 8000 of the host machine to port 8000 of the container (where the FastAPI service is running).
    *   `--name aita_interaction_container`: Assigns a name to the running container for easier management.
    *   `aita-service:latest`: Specifies the image to use.

2.  **To view logs from the running container:**
    ```bash
    docker logs aita_interaction_container -f
    ```
    *(Press Ctrl+C to stop following logs)*

3.  **To stop the container:**
    ```bash
    docker stop aita_interaction_container
    ```

4.  **To remove the container (after stopping):**
    ```bash
    docker rm aita_interaction_container
    ```

## Testing Endpoints

Once the container is running, you can test the endpoints using a tool like `curl` or Postman.

### User Profile Endpoints

#### `/users/register` (POST)
*   **Purpose**: Creates a new user profile.
*   **Example `curl` command**:
    ```bash
    curl -X POST "http://localhost:8000/users/register" \
         -H "Content-Type: application/json" \
         -d '{
               "username": "student_jane_doe",
               "grade_level": 4,
               "preferred_aita_persona_id": "ReadingExplorerAITA_4thGrade_v1_adapter"
             }'
    ```
*   **Example Response (Success - Status 201)**:
    ```json
    {
      "username": "student_jane_doe",
      "grade_level": 4,
      "preferred_aita_persona_id": "ReadingExplorerAITA_4thGrade_v1_adapter",
      "user_id": "generated_uuid_string_for_jane",
      "created_at": "2024-08-01T12:00:00.000000Z" 
    }
    ```
*   **Example Response (Failure - Status 400, Username Exists)**:
    ```json
    {
        "detail": "Username 'student_jane_doe' already exists."
    }
    ```

#### `/users/{user_id}` (GET)
*   **Purpose**: Retrieves an existing user profile by their `user_id`.
*   **Example `curl` command** (replace `your_user_id_here` with a `user_id` obtained from the register endpoint, e.g., "generated\_uuid\_string\_for\_jane"):
    ```bash
    curl -X GET "http://localhost:8000/users/your_user_id_here"
    ```
*   **Example Response (Success - Status 200)**:
    ```json
    {
      "username": "student_jane_doe",
      "grade_level": 4,
      "preferred_aita_persona_id": "ReadingExplorerAITA_4thGrade_v1_adapter",
      "user_id": "your_user_id_here",
      "created_at": "2024-08-01T12:00:00.000000Z" 
    }
    ```
*   **Example Response (Failure - Status 404, User Not Found)**:
    ```json
    {
        "detail": "User not found"
    }
    ```

### `/interact` Endpoint (POST)

*   **Purpose**: Main endpoint for interacting with an AITA.
*   **Example `curl` command** (use a `user_id` obtained from registration):
    ```bash
    curl -X POST "http://localhost:8000/interact" \
         -H "Content-Type: application/json" \
         -d '{
               "user_id": "your_user_id_here", 
               "aita_persona_id": "default_phi3_base", 
               "user_utterance": "Hello AITA, can you help me with main idea?",
               "conversation_history": []
             }'
    ```
*   **Expected Response (example)**:
    ```json
    {
      "session_id": "some-uuid-string-here",
      "aita_response": "Of course! The main idea is what a story is mostly about. What story are you reading today?",
      "debug_info": {
        "model_used": "microsoft/Phi-3-mini-4k-instruct",
        "aita_persona_requested": "default_phi3_base",
        "user_profile_found": true 
      }
    }
    ```
    *   The `session_id` will be a newly generated UUID if not provided in the request.
    *   The `aita_response` will vary based on the SLM's generation.
    *   `debug_info.user_profile_found` will indicate if the `user_id` matched a profile.

These notes provide a basic outline for deploying and testing the AITA Interaction Service. For production, more robust error handling, logging, security, and potentially a model management layer would be necessary. Also, the in-memory `USER_PROFILES_DB` would be replaced with a persistent database.
