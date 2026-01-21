# Instructions for Agents

This project is an AI-powered educational platform. Here are some guidelines for working with this codebase.

## Project Structure
-   **Services**: `aita_interaction_service.py`, `api_integration_hub.py`, `quiz_generator.py`, etc. are FastAPI applications.
-   **Dashboards**: `teacher_dashboard_main.py`, `student_frontend_streamlit.py`, `advanced_analytics.py` are Streamlit apps.
-   **SDKs**: `k12_mcp_client_sdk/` and `k12_mcp_server_sdk/` contain Model Context Protocol implementations.

## Testing
-   Always run `test_installation.py` first to ensure the environment is set up.
-   Run `test_services.py` to verify that services can initialize.
-   Run `test_new_features.py` to verify the functionality of new modules.
-   If you modify code, ensure these tests pass before submitting.

## Known Issues
-   `modelcontextprotocol` might need to be installed manually if `pip install -r requirements.txt` fails to install it (it is sometimes commented out).
-   The project relies heavily on mock data. Be careful when assuming data persistence.

## Common Tasks
-   **Starting Services**: Use `python feature_launcher.py start` or run individual scripts.
-   **Linting**: Use `python -m py_compile *.py` to check for syntax errors.
