# Extensible Teacher Oversight Dashboard: Architectural Design (V2 Prototype)

## 1. Introduction

### Purpose
This document outlines a design for an extensible and modular architecture for the Teacher Oversight Dashboard. The goal is to evolve the current prototype into a more robust system that can easily accommodate new analytical features, views, and data sources while improving maintainability.

### Recap of Current Dashboard
The current `teacher_dashboard_prototype.py` is a single-file Streamlit application. While effective for initial demonstration, its monolithic structure makes it challenging to:
*   Add new, complex analytical views without significantly refactoring the main file.
*   Manage data loading and processing logic independently from UI rendering.
*   Collaborate on different features simultaneously.
*   Scale effectively if data volume or feature complexity grows substantially.

This V2 design aims to address these limitations by introducing a multi-page Streamlit application structure with a dedicated data abstraction layer.

## 2. Goals for Extensible Architecture

*   **Modularity**: Clearly separate data handling, different dashboard pages/views, and shared utilities into distinct modules or files.
*   **Ease of Adding New Features**: Enable developers to add new analytical features or dashboard pages with minimal impact on existing core structures. A new view should ideally be a new Python file in a designated `pages/` directory.
*   **Maintainability**: Improve code organization and readability through separation of concerns, making it easier to debug and update individual components.
*   **Scalability (Conceptual)**: While the V2 prototype will still be Streamlit-based, the architecture should provide a clear conceptual path towards a more scalable solution involving a dedicated backend API and frontend framework if future needs demand it.
*   **Efficiency**: Implement data caching to improve performance, especially when dealing with potentially growing log files.

## 3. Proposed Architecture: Enhanced Streamlit Multi-Page Application (V2 Prototype)

### 3.1. Core Idea
The V2 prototype will leverage Streamlit's native multi-page application functionality. This is achieved by organizing individual pages (views/features) as separate Python scripts within a `pages/` subdirectory. A dedicated data management module (`dashboard_data_manager.py`) will handle all data loading, processing, and caching, serving as a single source of truth for all pages.

### 3.2. Key Modules & Their Responsibilities

*   **`teacher_dashboard_main.py` (Main App Runner):**
    *   **Responsibilities**:
        *   Sets the overall Streamlit page configuration (`st.set_page_config(page_title="AITA Teacher Dashboard V2", layout="wide")`).
        *   Displays a top-level title or welcome message for the entire application (e.g., `st.title("AITA Teacher Dashboard V2")`).
        *   Instantiates the `DashboardDataManager`.
        *   Calls the primary data loading function from `DashboardDataManager` to load and cache the xAPI statements (e.g., `data_manager.load_and_cache_data()`).
        *   Streamlit automatically generates sidebar navigation based on the Python files found in the `pages/` directory. This script itself can serve as the "home" page or simply be the entry point that sets up shared resources.
    *   **Key Code Snippets (Conceptual)**:
        ```python
        # teacher_dashboard_main.py
        import streamlit as st
        from dashboard_data_manager import DashboardDataManager # Assuming this class is defined

        st.set_page_config(page_title="AITA Teacher Dashboard V2", layout="wide")
        st.title("AITA Teacher Dashboard V2")
        
        # Initialize and load data (cached)
        # The data manager instance could be stored in st.session_state if complex state is needed across pages,
        # or simply instantiated and its methods called by each page if data loading is cached globally by Streamlit.
        # For simplicity here, assume data_manager methods are called directly by pages after initial load.
        
        # @st.cache_data # Caching would be within the data_manager
        # def load_data():
        #     data_manager = DashboardDataManager()
        #     return data_manager.load_xapi_statements() # Or a more comprehensive load function
        
        # all_statements = load_data()
        # st.sidebar.success("Data loaded successfully!")
        
        st.markdown("Welcome to the AITA Teacher Dashboard. Please select a view from the sidebar.")
        # Streamlit handles page navigation from here based on files in pages/
        ```

*   **`dashboard_data_manager.py` (Data Abstraction Layer):**
    *   **Responsibilities**:
        *   Centralize all data loading, parsing, filtering, and analysis logic.
        *   Utilize `st.cache_data` to cache loaded and processed data, preventing redundant computations and improving app responsiveness.
        *   Provide well-defined functions for pages to retrieve data.
    *   **Key Functions (Signatures & Purpose)**:
        ```python
        # dashboard_data_manager.py
        import streamlit as st
        import json
        import pandas as pd
        from typing import List, Dict, Any, Optional

        # @st.cache_data # Cache the raw data loading
        def load_xapi_statements(log_filepath: str = "xapi_statements.jsonl") -> List[Dict[str, Any]]:
            # ... (logic from current teacher_dashboard_prototype.py, including placeholder data)
            # ... Returns list of statement dictionaries
            pass

        # @st.cache_data # Cache derived data if computationally intensive
        def get_filtered_session_summaries(_all_statements: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
            # _all_statements is passed to allow caching based on its content
            # filters = {"student_id": Optional[str], "date": Optional[datetime.date]}
            # ... (logic from current teacher_dashboard_prototype.py, enhanced for robustness)
            # ... Returns list of session summary dictionaries
            pass

        # @st.cache_data
        def get_turns_for_session(_all_statements: List[Dict[str, Any]], session_id: str) -> List[Dict[str, Any]]:
            # ... (logic from current teacher_dashboard_prototype.py, enhanced for robustness)
            # ... Returns list of formatted dialogue turns for the given session_id
            pass

        # --- New Analytics Functions (Placeholders for Future Features) ---
        # @st.cache_data
        def analyze_misconceptions(_all_statements: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
            # Conceptual: Analyzes dialogue turns for patterns indicating common misconceptions.
            # Would require sophisticated NLP or rule-based logic on 'user_utterance_raw' and 'aita_response_final_to_user'.
            # For V2 prototype, this could return mock/placeholder data.
            # Example return: [{"misconception": "Confuses producers and consumers", "count": 5, "related_los": ["ECO.7.LO1"]}]
            print(f"Placeholder: Analyzing misconceptions with filters: {filters}")
            return [{"misconception": "Placeholder: Difficulty with main idea vs. details", "count": 10, "example_session_id": "session1"}]

        # @st.cache_data
        def analyze_strategy_effectiveness(_all_statements: List[Dict[str, Any]], filters: Dict[str, Any]) -> Dict[str, Any]:
            # Conceptual: More advanced, might try to correlate AITA pedagogical notes/strategies with student outcomes.
            # For V2 prototype, this would return mock/placeholder data.
            print(f"Placeholder: Analyzing strategy effectiveness with filters: {filters}")
            return {"strategy_X_usage": 50, "strategy_Y_correlation_positive": True, "notes": "Mock data"}
            
        # @st.cache_data
        def get_student_progress_summary(_all_statements: List[Dict[str, Any]], student_id: str, lo_filters: Optional[List[str]] = None) -> List[Dict[str, Any]]:
            # Conceptual: Tracks a student's interactions across sessions for specific LOs.
            # For V2 prototype, returns mock/placeholder data.
            # Example return: [{"lo_id": "RC.4.LO1", "status": "developing", "sessions_count": 3, "last_interaction_date": "..."}]
            print(f"Placeholder: Getting progress for student {student_id} with LO filters: {lo_filters}")
            return [{"lo_id": "RC.4.LO1.MainIdea", "status": "Proficient (mock)", "interactions": 5, "last_seen": "2024-07-31"}]
        ```

*   **`pages/` (Directory for individual views/features):**
    *   This directory will contain separate `.py` files, each representing a page in the Streamlit application. Streamlit automatically creates sidebar navigation based on these filenames (e.g., `1_Overview_Dashboard.py` becomes "Overview Dashboard" in the sidebar).
    *   **`1_Overview_Dashboard.py`**:
        *   Imports functions from `dashboard_data_manager`.
        *   Implements the UI for the main session overview page (similar to the "Overview" part of the current prototype).
        *   Includes filter widgets (Student ID, Date).
        *   Calls `data_manager.get_filtered_session_summaries()` with filter values.
        *   Displays aggregate statistics and the filtered session table.
    *   **`2_Session_Transcript_View.py`**:
        *   Imports functions from `dashboard_data_manager`.
        *   Allows selection of a session (perhaps passed via query params from Overview, or a selectbox if navigating directly).
        *   Calls `data_manager.get_turns_for_session()` for the selected session.
        *   Renders the detailed transcript view, including expanders for moderation details, LLM prompts, etc. (similar to the session detail part of the current prototype).
    *   **(Example New Feature) `3_Misconception_Analysis_Prototype.py`**:
        *   A new Streamlit page script.
        *   Imports `DashboardDataManager`.
        *   Calls `data_manager.analyze_misconceptions()` (which would initially return mock/placeholder data).
        *   Uses Streamlit elements (e.g., `st.bar_chart`, `st.data_frame`) to display the (mock) analysis of potential student misconceptions.
        *   Might include filters relevant to this analysis (e.g., by LO, date range).
    *   **(Example New Feature) `4_Student_Progress_View_Prototype.py`**:
        *   A new page script.
        *   Allows selection of a student (e.g., `st.selectbox` with student IDs from `get_filtered_session_summaries`).
        *   Calls `data_manager.get_student_progress_summary()` for the selected student.
        *   Displays a conceptual summary of student progress (mock data initially).

*   **`dashboard_utils.py` (Shared Utilities - Optional but Recommended):**
    *   **Responsibilities**: Contain helper functions used across multiple pages to maintain consistency and reduce code duplication.
    *   **Example Functions**:
        *   `render_moderation_details(moderation_data, type_label)`: A function to consistently display the JSON for input/output moderation in an expander with appropriate warnings/errors.
        *   `format_timestamp(timestamp_str)`: Standardized timestamp formatting.
        *   `create_info_banner(message, icon)`: Consistent UI for info messages.

### 3.3. Data Flow

1.  **Raw Data**: `xapi_statements.jsonl` (or placeholder content).
2.  **Data Loading & Caching**: `teacher_dashboard_main.py` (or individual pages if data manager is session-scoped) triggers data loading via `DashboardDataManager.load_xapi_statements()`. This function reads the file and uses `@st.cache_data` to store the raw list of statements.
3.  **Data Processing & Analysis**:
    *   Page scripts (e.g., `1_Overview_Dashboard.py`, `3_Misconception_Analysis_Prototype.py`) call specific functions in `DashboardDataManager` (e.g., `get_filtered_session_summaries`, `analyze_misconceptions`).
    *   These data manager functions take the cached raw statements and any filters as input.
    *   They perform the necessary processing/analysis. The results of these functions can also be cached using `@st.cache_data` if they are computationally intensive.
4.  **UI Rendering**: Page scripts use Streamlit elements (`st.dataframe`, `st.chat_message`, `st.bar_chart`, etc.) to display the data returned by the `DashboardDataManager`.

### 3.4. Adding New "Add-on" Features/Views

This architecture simplifies adding new features:

1.  **Define Data Logic**: If the new feature requires new data processing or analysis, add a corresponding function to `dashboard_data_manager.py` (e.g., `analyze_student_engagement_patterns()`). Implement this function, initially perhaps with mock data. Ensure it's cached if appropriate.
2.  **Create New Page Script**: Create a new `.py` file in the `pages/` directory (e.g., `5_Engagement_Patterns.py`).
3.  **Implement UI**: In the new page script:
    *   Import necessary functions from `dashboard_data_manager`.
    *   Call the data logic function to get the required data.
    *   Use Streamlit elements to build the UI for displaying the new feature/analysis.
4.  **Automatic Navigation**: Streamlit will automatically add the new page to the sidebar navigation.

## 4. Path to Greater Scalability (Brief Discussion)

While the V2 Streamlit multi-page app offers better organization and some performance gains via caching, very large datasets or a high number of concurrent users might eventually require a more traditionally scalable web architecture:

*   **Dedicated Backend API**:
    *   The data processing and analytics logic currently in `DashboardDataManager` could be migrated to a dedicated backend API service (e.g., built with FastAPI or Flask).
    *   This backend would handle connections to a production database (e.g., a proper LRS or data warehouse) instead of reading from a JSONL file.
    *   The API would expose endpoints for fetching session summaries, transcripts, analytics, etc.

*   **Dedicated Frontend Application**:
    *   The Streamlit UI pages would be reimplemented as a separate frontend application (e.g., using React, Vue, Angular, or a Python web framework like Django/Flask with server-side templates).
    *   This frontend would consume data from the dedicated backend API.

*   **Benefits of this Evolution**:
    *   Improved performance and scalability for large data/user loads.
    *   More control over UI/UX design and complex frontend interactions.
    *   Better separation of concerns between frontend, backend, and data storage.
    *   Allows for independent scaling of frontend and backend components.

The V2 enhanced Streamlit architecture serves as an excellent intermediate step, allowing for rapid development and iteration of new dashboard features while keeping the path open for future scalability. The modular `DashboardDataManager` can be more easily adapted or replaced by an API client module if/when a dedicated backend is developed.
