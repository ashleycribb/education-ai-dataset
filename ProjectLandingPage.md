# The Open AITA Initiative: Building Pedagogically Sound AI Tutors for K-12

## Vision / Mission Statement

Our mission is to foster the development of open-source, safe, and effective AI Teacher's Assistants (AITAs) that empower K-12 students by focusing on a "teach how to learn" pedagogical philosophy.

## What is This Project?

This project explores the creation of **AI Teacher's Assistants (AITAs)** – specialized AI tutors designed to support K-12 students in various subjects. Our core pedagogical philosophy is to **"teach how to learn,"** meaning our AITAs aim to guide students through questioning, metacognitive prompts, and problem-solving strategies rather than simply providing direct answers.

Key features of our AITA ecosystem include:
*   **Context-Awareness**: AITAs can leverage contextual information (e.g., from an LMS about the student's current activity) using the **Model Context Protocol (MCP)** to tailor interactions.
*   **Built-in Safeguards**: We prioritize student safety with integrated content moderation for both student inputs and AITA outputs using a dedicated `ModerationService`.
*   **Data-Driven Teacher Oversight**: Detailed interaction logs, structured like xAPI statements, are generated to allow educators to review student progress and AITA performance via a prototype Teacher Dashboard.
*   **Open-Source Nature**: We are committed to developing this ecosystem using open-source models, tools, and by sharing our methodologies and code.

## Current Status & Key Components

This project is currently in a prototype stage, demonstrating the feasibility and core functionalities of the AITA ecosystem. Key components developed include:

*   **AITA SLM Fine-Tuning Pipeline**: A process for fine-tuning Small Language Models (SLMs), using Microsoft's Phi-3 series as an example, with Parameter-Efficient Fine-Tuning (PEFT/LoRA).
*   **Data Generation & Processing Scripts**: Tools (`data_processing_scripts.py`, `extract_*.py`, `preprocess_extracted_data.py`) for creating specialized AITA datasets (e.g., for reading comprehension and ecology) in a structured JSON format designed for pedagogical fine-tuning.
*   **Prototype AITAs**:
    *   **"Reading Explorer AITA"**: For 4th-grade reading comprehension (main idea, inference, vocabulary).
    *   **"Eco Explorer AITA"**: For 7th-grade science/ecology (food webs, biotic/abiotic factors, human impact).
*   **MCP-Based Interaction**:
    *   `lms_mcp_server_mock.py`: A mock LMS server providing student/activity context via MCP.
    *   `aita_mcp_client.py`: An AITA client that fetches context from the MCP server and interacts with the SLM.
*   **Safeguard Mechanisms**: `moderation_service.py` uses a Hugging Face model (e.g., `unitary/toxic-bert`) to check text for appropriateness.
*   **xAPI-like Interaction Logging**: The `aita_mcp_client.py` generates detailed interaction logs in `xapi_statements.jsonl`.
*   **Prototype Teacher Oversight Dashboard**: A Streamlit application (`teacher_dashboard_prototype.py`) for visualizing the logged interaction data.
*   **SDKs for MCP Development**:
    *   `k12_mcp_server_sdk`: Simplifies building new MCP-compliant servers.
    *   `k12_mcp_client_sdk`: Simplifies building new MCP clients, including xAPI logging utilities.

A comprehensive demonstration script (`DemoGuide.md`) is available to showcase these components working together with synthetic and sample data.

## Core Principles

*   **Open Source**: Utilizing and contributing to open-source models, tools, and frameworks to foster collaboration and accessibility.
*   **Pedagogical Focus**: Prioritizing a "teach how to learn" approach, emphasizing critical thinking, metacognition, and guided discovery over rote memorization or direct answer provision.
*   **Safety & Responsibility**: Implementing multi-layered safeguards, including content moderation and ethical considerations, to ensure AITAs are safe and appropriate for K-12 students.
*   **Data-Driven Iteration**: Leveraging detailed interaction logs (xAPI-like) for continuous analysis, evaluation, and improvement of AITA effectiveness and pedagogical strategies.
*   **Community Collaboration**: Building a foundation that can be extended and enriched by educators, developers, and researchers.

## Technology Stack (High-Level)

*   **Python**: Primary programming language.
*   **Hugging Face Ecosystem**:
    *   `Transformers`: For accessing and using pre-trained SLMs.
    *   `PEFT` (Parameter-Efficient Fine-Tuning): For LoRA-based fine-tuning.
    *   `TRL` (Transformer Reinforcement Learning): Provides `SFTTrainer` for supervised fine-tuning.
    *   `Datasets`: For handling and processing training data.
*   **Small Language Models (SLMs)**: Example implementation uses Microsoft's Phi-3 series.
*   **Model Context Protocol (MCP)**: For standardized communication between the AITA client and context providers (e.g., mock LMS).
*   **FastAPI**: Used for the (conceptual) AITA Interaction Service backend.
*   **Streamlit**: Powers the prototype Teacher Oversight Dashboard.
*   **PyTorch**: As the underlying deep learning framework for the SLMs.

## How to Get Involved (Call to Action)

We welcome collaboration from individuals and institutions interested in advancing open and effective AI for K-12 education!

*   **Link to Our GitHub Repository**: `[Link to Our GitHub Repository](https://github.com/your-org/your-aita-project)` (Placeholder - replace with actual link)

*   **Areas for Contribution**:
    *   **Educators & Subject Matter Experts**:
        *   Developing and curating high-quality, diverse datasets for new subjects and grade levels.
        *   Reviewing and refining pedagogical strategies embedded in AITA dialogues.
        *   Aligning AITA content with curriculum standards.
        *   Contributing to the conceptual K-12 educational ontology.
    *   **Developers**:
        *   Enhancing the `k12_mcp_server_sdk` and `k12_mcp_client_sdk`.
        *   Experimenting with fine-tuning different SLMs for various AITA roles.
        *   Developing robust student and teacher frontend applications.
        *   Building new MCP servers to connect AITAs with real educational data sources.
        *   Improving the `ModerationService` and other safeguard mechanisms.
    *   **Researchers**:
        *   Utilizing the AITA platform and its detailed xAPI-like logs for studies in educational AI, learning analytics, and pedagogical effectiveness.

*   **Contact/Discussion**:
    *   Join the discussion on our GitHub repository's "Discussions" tab (if enabled).
    *   For direct inquiries, contact us at: `[your-project-contact-email@example.com]` (Placeholder).

## High-Level Roadmap (Future Directions)

Our vision extends beyond the current prototype. Key future goals include:

1.  **User Trials & Feedback**: Conducting pilot studies with K-12 students and teachers to gather feedback and iteratively improve AITA effectiveness and usability.
2.  **Responsive Web-Based Student Frontend**: Developing a user-friendly, multi-device compatible web interface for students to interact with AITAs.
3.  **Expanded AITA Profiles & Subject Coverage**: Creating fine-tuned AITAs for a broader range of subjects (e.g., Math, History, Arts) and grade levels, based on newly sourced and curated datasets.
4.  **LMS & Real Data Integration**: Moving beyond mock servers to integrate with actual Learning Management Systems and other educational databases using MCP.
5.  **Enhanced Teacher Dashboard & Analytics**: Developing more sophisticated analytics and visualizations in the Teacher Dashboard based on LRS data.

## Project Licensing

The codebase for this project, including the SDKs and example components, is primarily intended to be licensed under a permissive open-source license such as the **MIT License** or **Apache 2.0 License**. Specific licenses for individual components or datasets sourced from external providers will be clearly indicated in their respective locations.

We believe an open approach is crucial for building trust, fostering innovation, and ensuring broad accessibility of these educational tools.
