# AITA MCP Client: User Guide (`aita_mcp_client.py`)

## 1. Overview

### Purpose
This guide explains how to use the `aita_mcp_client.py` script to interact with an AI Tutor (AITA). This client can connect to:
*   A base Small Language Model (SLM) like Microsoft's Phi-3-mini series.
*   A fine-tuned version of an SLM, where specific LoRA adapter weights have been trained for a particular AITA persona (e.g., "Reading Explorer AITA" or "Eco Explorer AITA").

### Role as an MCP Client
The `aita_mcp_client.py` acts as a client for the Model Context Protocol (MCP). In this prototype, it demonstrates:
*   **Fetching Context**: It can retrieve simulated student and activity context from an MCP-compliant server (like the provided `lms_mcp_server_mock.py`). This context is then used to tailor the AITA's interaction.
*   **Logging Interactions**: It logs detailed information about each interaction turn to a JSON Lines file (`xapi_statements.jsonl`), structured similarly to xAPI statements, for later review and analysis.

## 2. Environment Setup

### Recommended Python Version
*   Python 3.9 or higher.

### Essential Python Libraries
You'll need several Python libraries. Install them using pip:
```bash
pip install torch torchvision torchaudio
pip install transformers datasets peft trl accelerate bitsandbytes sentencepiece
pip install modelcontextprotocol # For MCP client/server functionalities
```
*   **`torch`**: The core PyTorch library.
*   **`transformers`**: Hugging Face's library for state-of-the-art NLP models.
*   **`peft`**: Hugging Face's Parameter-Efficient Fine-Tuning library, used for loading LoRA adapters.
*   **`modelcontextprotocol`**: The library enabling MCP communication.
*   Other libraries like `datasets`, `trl`, `accelerate`, `bitsandbytes`, `sentencepiece` are often dependencies for `transformers` or related tasks like fine-tuning, but `torch`, `transformers`, `peft`, and `modelcontextprotocol` are key for this client.

### Additional Files
*   **`moderation_service.py`**: This file, containing the `ModerationService` class, must be in the same directory as `aita_mcp_client.py` or available in your Python path, as the client imports it directly.

## 3. Prerequisites

1.  **Running MCP Server (for context fetching)**:
    *   If you want the client to fetch context from the mock Learning Management System (LMS), the `lms_mcp_server_mock.py` script (or a similar MCP server) must be running and its output piped to `aita_mcp_client.py`.
    *   If the MCP server is not running or not connected, the client will fall back to a generic AITA persona and default prompts.

2.  **Access to Base SLM**:
    *   The client needs to download the base SLM specified in the script (e.g., `microsoft/Phi-3-mini-4k-instruct`) from Hugging Face Hub on its first run. This requires an internet connection. Subsequent runs will use the cached model.

3.  **(Optional) Fine-tuned LoRA Adapter Weights**:
    *   If you intend to use a specialized, fine-tuned AITA, you must have the LoRA adapter weights (e.g., from a training run using `fine_tune_aita.py`) available locally. You'll need to provide the path to these weights in the client script.

## 4. Configuration (`aita_mcp_client.py`)

Key variables at the top of `aita_mcp_client.py` allow you to configure its behavior:

*   **`MODEL_ID`**:
    *   Specifies the Hugging Face identifier for the base SLM (e.g., `"microsoft/Phi-3-mini-4k-instruct"`).
    *   This model will be downloaded if not already cached locally.

*   **`ADAPTER_CHECKPOINT_PATH`**:
    *   This variable (defined in the `if __name__ == "__main__":` block) should be set to the file path of your fine-tuned LoRA adapter weights if you want to load a specialized AITA.
    *   Example: `ADAPTER_CHECKPOINT_PATH = "./results_phi3_aita_reading_pilot/final_checkpoint"`
    *   If `ADAPTER_CHECKPOINT_PATH` is `None` or points to an invalid path, the client will use the base model specified by `MODEL_ID`.

*   **`XAPI_LOG_FILE_PATH`**:
    *   Defines the name of the file where interaction logs (xAPI-like statements) are saved. Defaults to `"xapi_statements.jsonl"`. Each interaction turn is appended as a new JSON line.

*   **`DEFAULT_STUDENT_ID`, `DEFAULT_SUBJECT`, `DEFAULT_ITEM_ID`**:
    *   These variables are used when the client starts up to fetch initial context from the `lms_mcp_server_mock.py`.
    *   They should correspond to valid keys and data within the mock LMS server's `MOCK_DB` to successfully retrieve context. For example, `DEFAULT_STUDENT_ID = "student001"`, `DEFAULT_SUBJECT = "ReadingComprehension"`, `DEFAULT_ITEM_ID = "passage_kitten_001"`.

*   **Safeguard Keywords (Legacy)**:
    *   `BLOCKED_INPUT_KEYWORDS` and `BLOCKED_OUTPUT_KEYWORDS` are still present but their functionality has been superseded by the `ModerationService`. The active content checking is now performed by the Hugging Face model loaded in `ModerationService`.

## 5. Running the Client

### StdIO Mode (Primary Example)
The client is designed to communicate with an MCP server (like `lms_mcp_server_mock.py`) over standard input/output (stdio). This is typically done using a pipe:

```bash
python lms_mcp_server_mock.py | python aita_mcp_client.py
```

*   **Left side (`lms_mcp_server_mock.py`)**: Runs the mock LMS server. Its standard output (where it sends MCP responses) becomes the standard input for the client.
*   **Right side (`aita_mcp_client.py`)**: Runs the AITA client. Its standard output (where it sends MCP requests) is piped from the server's input. The client also prints AITA and user interactions to the console.

**Interaction:**
*   Once running, the client will typically fetch initial context (if the server is connected) and display an initial message from the AITA.
*   You can then type your messages at the "User: " prompt and press Enter.
*   To exit, type "quit", "exit", or "q".

### (Conceptual) HTTP Mode
The `SimplifiedMCPClient` class (used internally by `aita_mcp_client.py` if you were to adapt the main script) also supports an `"http"` mode. This would involve:
1.  Running an MCP server in HTTP mode (e.g., `python k12_mcp_server_sdk/examples/simple_server_example.py` if adapted for HTTP, or a production MCP HTTP server).
2.  Modifying `aita_mcp_client.py` to instantiate `SimplifiedMCPClient` with `client_type="http"` and providing the `host` and `port` of the HTTP server.
The current example script is primarily set up for stdio.

## 6. Key Features Demonstrated

*   **Context Fetching**: The client calls the `/student/{student_id}/activity_context` endpoint on the MCP server to retrieve data about the student, the passage they are working on, target learning objectives, and teacher notes.
*   **Contextualized Interaction**:
    *   The fetched context dynamically shapes the AITA's system prompt.
    *   The AITA's initial greeting refers to the specific passage and learning objective from the context.
*   **SLM Interaction**: Manages the turn-by-turn dialogue with the (potentially fine-tuned) SLM, formatting prompts according to the Phi-3 chat template.
*   **Content Moderation**:
    *   Integrates `ModerationService` (from `moderation_service.py`).
    *   User inputs and AITA's raw outputs are checked for appropriateness using the `unitary/toxic-bert` model.
    *   If input is flagged, a polite refusal is shown. If output is flagged, it's replaced with a generic safe response.
    *   Detailed moderation scores and outcomes are logged.
*   **Structured Logging**:
    *   Interactions are logged to `xapi_statements.jsonl`.
    *   Each log entry is a JSON object structured like an xAPI statement, including `actor`, `verb`, `object` (with details of the interaction turn), `result` (with duration and moderation details), and `context` (with session info, full LLM prompt, etc.).

## 7. Interacting with Different Fine-Tuned AITA Profiles

The `aita_mcp_client.py` can be used to interact with different AITAs (e.g., Reading Explorer, Eco Explorer) by changing its configuration:

1.  **`ADAPTER_CHECKPOINT_PATH`**:
    *   Update this variable in the `if __name__ == "__main__":` block to point to the directory containing the LoRA adapter files for the desired AITA (e.g., `./results_phi3_aita_eco_pilot/final_checkpoint/`).
    *   If set to `None`, the client uses the base SLM without adapters.

2.  **Default Context Variables**:
    *   Adjust `DEFAULT_STUDENT_ID`, `DEFAULT_SUBJECT`, and `DEFAULT_ITEM_ID` at the top of the script. These should correspond to a relevant context for the target AITA that exists in your `lms_mcp_server_mock.py`'s `MOCK_DB`.
    *   For example, for an "Eco Explorer AITA", you might set:
        ```python
        DEFAULT_SUBJECT = "Ecology" 
        DEFAULT_ITEM_ID = "eco_passage_foodweb_001" 
        ```

3.  **System Prompt Adaptation**:
    *   The `system_prompt` in `chat_with_aita` is constructed dynamically using the fetched context. The persona name (e.g., "Reading Explorer AITA", "Eco Explorer AITA") is also adjusted based on the fetched subject.
    *   For AITAs with very distinct personas or instructional styles not fully captured by the fetched context, you might consider:
        *   Creating different versions of `aita_mcp_client.py`.
        *   Making the system prompt selection more sophisticated (e.g., based on the loaded adapter path or a configuration setting).

## 8. Basic Troubleshooting

*   **Piping Issues**: "Ensure `lms_mcp_server_mock.py` is running and its output is correctly piped to `aita_mcp_client.py`." If the client hangs or shows no output, the pipe might not be set up correctly, or the server script might have exited or errored.
*   **Model/Adapter Paths**: "Verify model identifiers in `MODEL_ID` and paths to adapters in `ADAPTER_CHECKPOINT_PATH` are correct and accessible." Incorrect paths will prevent the model or adapter from loading.
*   **First Run Downloads**: "On first run, `ModerationService` (and the main SLM) might download models, requiring internet access." This can take some time. Subsequent runs will use cached models. If `ModerationService` fails to load its model, it will fall back to a dummy service that doesn't perform actual moderation but allows the client to run.
*   **Check Logs**: "Check `xapi_statements.jsonl` for logged interactions and potential errors." This file provides a detailed trace of the client's operations, including any errors encountered during interaction with the SLM or MCP server.
*   **Python Environment**: Ensure all required libraries are installed in the Python environment you are using to run the scripts.
