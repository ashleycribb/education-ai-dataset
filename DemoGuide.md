# AITA Ecosystem: Demonstration Guide

## 1. Introduction

### Purpose of the Demo
This demonstration showcases the current capabilities of the AI Tutor (AITA) ecosystem prototype. The goal is to illustrate:
*   **Live AITA Interaction**: How a student interacts with an AITA.
*   **Context-Awareness**: The AITA's ability to use information from a mock Learning Management System (LMS) via the Model Context Protocol (MCP).
*   **Safeguards**: Input filtering and output moderation using a dedicated `ModerationService`.
*   **Data Logging**: Generation of rich, xAPI-like interaction data.
*   **Teacher Oversight**: How logged data can be reviewed using a Teacher Dashboard.
*   **System Extensibility**: The potential for adding new AITA profiles and components.

### Overview of Demo Flow
1.  **Live AITA Interaction**: We'll run the AITA client and mock LMS server, showing a student interacting with the "Reading Explorer AITA". We'll demonstrate pedagogical dialogue and safeguards.
2.  **Teacher Oversight & Data Logging**: We'll examine the `xapi_statements.jsonl` log file and then use the Streamlit-based Teacher Dashboard to review the logged session.
3.  **System Extensibility & Future Potential**: We'll briefly look at the scripts and design documents that enable the creation of new AITA profiles and further system development.

## 2. Prerequisites for Demo Setup

*   **Required Python Scripts**:
    *   `aita_mcp_client.py`: The AITA client application.
    *   `lms_mcp_server_mock.py`: The mock LMS server providing context via MCP.
    *   `teacher_dashboard_prototype.py`: The Streamlit application for reviewing logs.
    *   `moderation_service.py`: Provides content moderation capabilities to the client.
    *   (Supporting SDKs `k12_mcp_server_sdk` and `k12_mcp_client_sdk` should be in the Python path or project structure).
*   **Python Environment**: A Python 3.9+ environment with all necessary libraries installed. Key libraries include `torch`, `transformers`, `streamlit`, `pandas`, `peft`, `trl`, and `modelcontextprotocol`. Refer to `FineTuningGuide.md` or `AITAClientGuide.md` for detailed setup.
*   **Log File (`xapi_statements.jsonl`)**:
    *   This file will be generated (or appended to) during the live AITA interaction part of the demo.
    *   For a smoother demo start, especially for the dashboard part, having a pre-existing `xapi_statements.jsonl` with a few diverse examples is recommended. The live demo will then add new sessions to this file.
*   **SLM Usage**:
    *   The demo will use the base SLM specified in `aita_mcp_client.py` (e.g., `microsoft/Phi-3-mini-4k-instruct`) unless the `ADAPTER_CHECKPOINT_PATH` variable in that script is explicitly set to a local path containing fine-tuned LoRA adapter weights.
    *   Ensure an internet connection is available if the base SLM or moderation model needs to be downloaded for the first time.

## 3. Demo Flow (Scripted Outline)

### Part 1: Live AITA Interaction (Reading Explorer AITA)

**(Talking Point Emphasize)**: *We're starting by showing how a student might interact with our "Reading Explorer AITA". This AITA is designed for 4th-grade reading comprehension and uses a "teach how to learn" approach.*

*   **Step 1: Start Mock LMS Server**
    *   Open a terminal.
    *   Run: `python lms_mcp_server_mock.py`
    *   **Explain**: *"This script simulates a Learning Management System. It's an MCP server that provides context to our AITA, like which student is logged in and what passage or learning objective they're working on. It communicates via standard input/output."*

*   **Step 2: Start AITA Client Piped from Server**
    *   Open a *second* terminal.
    *   Run: `python lms_mcp_server_mock.py | python aita_mcp_client.py`
        *   *(If the server is already running in another terminal, you'd need a different way to pipe, but for this demo, we'll restart it with the pipe).*
        *   Alternatively, if you have a way to manage background processes and pipes (like `mkfifo` on Linux/macOS, or manually pasting output/input), demonstrate that. For simplicity, the single pipe command is often easiest for local demos if the server doesn't need to stay running independently for other purposes during this part. *A common approach for demoing stdio piping is to run the server in one terminal, copy its first output (if any, like "Server listening..."), then run the client in another, paste the server's output if needed, then copy the client's first output and paste to server, etc. However, the direct pipe is cleaner if it works.*
        *   **For this guide, we assume the pipe `python lms_mcp_server_mock.py | python aita_mcp_client.py` works for the demo. If not, manual copy-pasting of MCP JSON messages between two terminals running each script separately would be the fallback.**
    *   **Explain**: *"Now we're starting the AITA client. The `|` (pipe) symbol connects the server's output to the client's input, and vice-versa (conceptually for stdio MCP). This allows them to communicate using the Model Context Protocol."*

*   **Step 3: Observe Context-Aware Greeting**
    *   In the `aita_mcp_client.py` terminal, point out the AITA's initial greeting.
    *   **Explain**: *"Notice the AITA's greeting. It mentions 'Lily the Lost Kitten' and a specific learning goal. This information didn't come from the AITA model itself initially; it was fetched from our mock LMS server via MCP when the client started. This shows the AITA is context-aware."*
        *   *(The client uses `DEFAULT_STUDENT_ID = "student001"`, `DEFAULT_SUBJECT = "ReadingComprehension"`, `DEFAULT_ITEM_ID = "passage_kitten_001"` which corresponds to mock data in `lms_mcp_server_mock.py`)*

*   **Step 4: Scripted Interactions (Reading Explorer AITA)**
    *   **(Talking Point Emphasize)**: *Now, let's interact with the AITA as a 4th-grade student might. Watch how it tries to guide learning rather than just giving answers.*
    *   At the `User:` prompt in the client terminal, type:
        *   `User: What is this story mainly about?`
        *   *(AITA should respond with guiding questions, e.g., "That's a good question! What are some of the important things that happen in the story? Who is it about?").*
    *   Then type:
        *   `User: How did Lily feel when she was lost?`
        *   *(AITA should guide the student to find clues in the text, e.g., "The story says, 'The sun began to set, and Lily felt scared.' What does that tell you? Are there other clues?").*
    *   Then type:
        *   `User: What does 'cozy' mean in the story?`
        *   *(AITA should prompt for contextual understanding, e.g., "The story says, 'she saw her cozy red house.' How do you think Lily felt when she saw her house after being lost? Does 'cozy' sound like a good feeling or a bad feeling?").*

*   **Step 5: Demonstrate Input Safeguard**
    *   **(Talking Point Emphasize)**: *Our AITA includes safeguards. Let's test the input moderation.*
    *   At the `User:` prompt, type:
        *   `User: Tell me about bad_word1.` (Or another keyword from `BLOCKED_INPUT_KEYWORDS` in `aita_mcp_client.py`).
    *   **Observe**: The AITA should respond with a polite refusal (e.g., "I'm sorry, I can't discuss that. Let's focus on our reading task!").
    *   **Explain**: *"The client checked this input using the `ModerationService`. Since it was flagged, the AITA didn't process the harmful request and gave a safe reply. This is logged."*

*   **Step 6: Demonstrate Output Safeguard (Conceptual Explanation)**
    *   **(Talking Point Emphasize)**: *The AITA also moderates its own responses before showing them to the student.*
    *   **Explain**: *"It's harder to reliably trigger the output safeguard with a base model for a live demo, as it depends on the SLM generating specific undesirable words. However, the process is: after the SLM generates a response, the `ModerationService` checks it. If flagged, the client replaces it with a generic safe message. We'll see evidence of this check in the logs and dashboard."*
        *   (Optional advanced demo: If you have a prompt known to make the *base* Phi-3 model output a word from `BLOCKED_OUTPUT_KEYWORDS`, you can try it. Otherwise, stick to the explanation.)

*   **Step 7: Exit AITA Client**
    *   At the `User:` prompt, type: `quit`
    *   **Explain**: *"This ends the AITA session. All our interactions, including the safeguard events, have been logged to `xapi_statements.jsonl`."*

### Part 2: Teacher Oversight Dashboard & Data Logging

**(Talking Point Emphasize)**: *A key part of our ecosystem is detailed logging for review and improvement. Let's look at the data generated.*

*   **Step 1: Show `xapi_statements.jsonl`**
    *   In a terminal, briefly display some lines from the `xapi_statements.jsonl` file.
        *   `cat xapi_statements.jsonl` (on Linux/macOS) or open it in a text editor.
    *   **Explain**: *"This is the log file. Each line is a JSON object, structured like an xAPI statement. It records details about each turn: who spoke, what they said, timestamps, the LLM prompt, moderation results, and contextual information like session ID and active learning objective."*

*   **Step 2: Run the Teacher Dashboard**
    *   Open a new terminal (or use one where the client/server is no longer running).
    *   Navigate to the directory containing `teacher_dashboard_prototype.py`.
    *   Run: `streamlit run teacher_dashboard_prototype.py`
    *   This should open the dashboard in a web browser.

*   **Step 3: Explore Dashboard Features**
    *   **(Talking Point Emphasize)**: *This dashboard allows educators to review AITA interactions. It's a prototype, but shows the potential for oversight.*
    *   **Overview Page**:
        *   Point out the "Overview" page, showing a table of recent sessions. The session(s) from Part 1 should be listed at the top.
        *   **Explain**: *"Here we see a summary of student sessions, including when they happened and a snippet of the first thing the student said."*
    *   **Session Transcript View**:
        *   In the sidebar, select the `session_id` corresponding to the "Reading Explorer AITA" interaction from Part 1.
        *   **Explain**: *"Now we're looking at the detailed transcript for that session."*
        *   Walk through the user and AITA utterances in the chat display.
    *   **Deep Dive into Expanders (CRUCIAL)**:
        *   For an AITA turn in the transcript:
            *   Click to open **"Input Moderation Details"** (for the preceding user turn). Explain the scores and `is_safe` flag.
            *   Click to open **"Output Moderation Details (AITA Raw)"**. Explain these are the scores for the AITA's *original* response before it was shown.
            *   If an output safeguard was triggered (conceptually, or if you managed to trigger one), the **"Original LLM Response (before safeguard override)"** expander would show the raw, problematic output. Explain its importance for debugging and understanding model behavior.
            *   Click to open **"Full Prompt to LLM"**. Explain that this shows the exact text sent to the SLM, including the system prompt, conversation history, and user input, which is vital for analyzing why the AITA responded a certain way.
        *   Find the turn where the input safeguard was triggered (e.g., "Tell me about bad_word1."). Show how the `input_moderation_details` in the dashboard reflect the flagged categories.

### Part 3: System Extensibility & Future Potential

**(Talking Point Emphasize)**: *This ecosystem is designed to be modular and extensible. We can create new AITAs for different subjects and integrate more advanced features.*

*   **Step 1: Show Data Generation for New AITAs**
    *   Briefly open `data_processing_scripts.py`.
    *   Scroll to `DEFAULT_7TH_GRADE_SCIENCE_PASSAGES` and the `generate_7th_grade_science_eco_sample_dialogues` function.
    *   **Explain**: *"Here, you can see how we define content and generate training data for a different AITA, like our 'Eco Explorer' for 7th-grade science. This script creates the specialized dialogues needed to teach the SLM how to tutor in ecology."*

*   **Step 2: Show Fine-Tuning Configuration for New AITAs**
    *   Briefly open `fine_tune_aita.py`.
    *   Point to the conceptual comments near `dataset_path` and `output_dir`.
    *   **Explain**: *"This is our fine-tuning script. By changing the dataset path to the 'Eco Explorer' data and specifying a new output directory, we can train a new LoRA adapter to create the 'Eco Explorer AITA' persona without altering the base SLM for other AITAs."*

*   **Step 3: Show Client Adaptation for New AITAs**
    *   Briefly open `aita_mcp_client.py`.
    *   Point to the conceptual comments near `ADAPTER_CHECKPOINT_PATH` and the default context variables.
    *   **Explain**: *"In the AITA client, we can load different fine-tuned adapters by changing the `ADAPTER_CHECKPOINT_PATH`. We'd also update the default subject and item ID to fetch the correct context from the LMS for the 'Eco Explorer AITA'."*

*   **Step 4: Multi-Device Support (Conceptual)**
    *   **Explain**: *"While our current client is command-line based, the `DeploymentStrategies.md` document (not shown in detail now) outlines how a production system would use a web-based student frontend. This ensures AITAs are accessible on various devices common in K-12 settings, like tablets, Chromebooks, and desktops."*

*   **Step 5: SDKs for Custom Components**
    *   **Explain**: *"We've developed two SDKs: `k12_mcp_server_sdk` and `k12_mcp_client_sdk`. These provide base classes and utilities that simplify building new MCP-compliant servers (like specialized content databases) or clients, fostering a more extensive and interoperable ecosystem."* (Optionally, very briefly show the `__init__.py` of one SDK).

*   **Step 6: Advanced Data Capabilities (Conceptual)**
    *   **Explain**: *"The `DataStrategy.md` (not shown in detail) describes our vision for a more advanced data infrastructure. This includes a K-12 educational ontology for richer semantic tagging of content and interactions, and a vertical database for storing structured educational content. These would enable more sophisticated analytics, personalization, and content discovery in the future."*

## 4. Key Talking Points & What to Emphasize

*   **"Teach How to Learn" Pedagogy**: The AITA guides students by asking questions, prompting for textual evidence, and encouraging metacognition, rather than just providing answers. This is reflected in the dialogue design and the `pedagogical_notes` in the training data.
*   **Context-Awareness (MCP)**: The AITA's ability to tailor interactions based on information received from the (mock) LMS demonstrates the power of MCP for creating integrated learning experiences.
*   **Multi-Layered Safeguards**:
    *   Proactive input filtering (client-side, before SLM).
    *   Output moderation (`ModerationService`) of the SLM's raw response.
    *   This layered approach is crucial for safety in K-12.
*   **Rich Data Logging (xAPI-like)**: The detailed, structured logs (`xapi_statements.jsonl`) are vital for:
    *   Transparency and accountability.
    *   Debugging AITA behavior.
    *   Learning analytics and educational research.
    *   Providing teachers with insights into student interactions.
*   **Teacher Dashboard Utility**: The dashboard provides a practical way to review interactions, understand AITA decision-making (via full prompts and moderation details), and identify areas for improvement or student support.
*   **Modularity & Extensibility**: The system is designed to be extended with new AITA profiles (through fine-tuning), new content, and new MCP-enabled services (using the SDKs). This allows the ecosystem to grow and adapt to different educational needs.
*   **Open-Source & Collaboration**: Briefly mention that the project's components are designed with open-source principles in mind, which can foster community contributions and wider adoption. (Conceptual: "We envision a future community portal or landing page for sharing AITAs and resources.")

## 5. Demo Assets Checklist

*   **Python Scripts**:
    *   `aita_mcp_client.py`
    *   `lms_mcp_server_mock.py`
    *   `teacher_dashboard_prototype.py`
    *   `moderation_service.py`
    *   `data_processing_scripts.py` (to show for extensibility)
    *   `fine_tune_aita.py` (to show for extensibility)
    *   `k12_mcp_server_sdk/*` (conceptually mention)
    *   `k12_mcp_client_sdk/*` (conceptually mention)
*   **Mock LMS Data (`lms_mcp_server_mock.py`)**: Ensure `MOCK_DB` contains varied and relevant entries for:
    *   `student001_ReadingComprehension_passage_kitten_001` (used for live demo)
    *   `student002_ReadingComprehension_passage_leaves_001` (for dashboard variety)
    *   Entries for "Ecology" subject if showcasing context-switching for `aita_mcp_client.py` is desired.
*   **Log File (`xapi_statements.jsonl`)**:
    *   **Recommended**: Have a pre-existing file with 5-10 diverse interaction statements. This ensures the dashboard has interesting data to display immediately. The live demo will append new interactions to this file.
    *   **Minimum**: An empty file that will be created/populated during the live demo.
*   **(Optional) Fine-tuned Adapters**: If demonstrating interaction with a fine-tuned AITA (beyond the base SLM), ensure the adapter files are locally accessible and the `ADAPTER_CHECKPOINT_PATH` in `aita_mcp_client.py` is correctly set. For this standard demo, using the base model is assumed.

This guide provides a comprehensive script for the AITA ecosystem demonstration. Remember to adapt the talking points to your audience and the time available. Good luck!
