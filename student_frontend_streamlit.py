# To run: streamlit run student_frontend_streamlit.py
import streamlit as st
from typing import List, Dict, Any, Optional
import requests # Added for API calls
import uuid # Added for potential client-side session init if needed

# --- Configuration ---
AITA_SERVICE_URL = "http://localhost:8000" # URL of the FastAPI backend service

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []
if "user_id" not in st.session_state:
    st.session_state.user_id: str = f"default_user_{uuid.uuid4().hex[:8]}" # Default user_id
if "session_id" not in st.session_state: # This will be updated by the backend
    st.session_state.session_id: Optional[str] = None
if "available_aita_personas" not in st.session_state:
    st.session_state.available_aita_personas: List[str] = [
        "default_phi3_base", 
        "ReadingExplorerAITA_4thGrade_Pilot1", 
        "EcoExplorerAITA_7thGrade_Pilot1"
    ]
if "current_aita_persona_id" not in st.session_state:
    st.session_state.current_aita_persona_id: str = st.session_state.available_aita_personas[0]
if "current_aita_display_name" not in st.session_state: # For displaying a more friendly name
    st.session_state.current_aita_display_name: str = st.session_state.available_aita_personas[0]


# --- Streamlit UI Layout and Logic ---
def run_student_frontend_v2():
    st.set_page_config(page_title="AITA Learning Zone V2", layout="wide")

    # --- Sidebar for User and AITA Persona Setup ---
    st.sidebar.header("User & AITA Setup")
    input_user_id = st.sidebar.text_input(
        "Enter your User ID:", 
        value=st.session_state.user_id
    )
    
    # Create a mapping from persona_id to a more friendly display name if desired
    persona_display_names = {
        "default_phi3_base": "Default Assistant (Phi-3 Base)",
        "ReadingExplorerAITA_4thGrade_Pilot1": "Reading Explorer (4th Grade)",
        "EcoExplorerAITA_7thGrade_Pilot1": "Eco Explorer (7th Grade)"
    }
    
    # Get the display name for the current persona, or default to the ID itself
    current_persona_display = persona_display_names.get(st.session_state.current_aita_persona_id, st.session_state.current_aita_persona_id)

    selected_persona_display_name = st.sidebar.selectbox(
        "Choose AITA Persona:", 
        options=[persona_display_names.get(pid, pid) for pid in st.session_state.available_aita_personas],
        index=[persona_display_names.get(pid, pid) for pid in st.session_state.available_aita_personas].index(current_persona_display) # Set current selection
    )

    if st.sidebar.button("Set User & Persona", key="set_user_persona_button"):
        st.session_state.user_id = input_user_id
        # Find the persona ID from the selected display name
        for pid, display_name in persona_display_names.items():
            if display_name == selected_persona_display_name:
                st.session_state.current_aita_persona_id = pid
                break
        st.session_state.current_aita_display_name = selected_persona_display_name
        
        # Reset chat for the new user/persona
        st.session_state.messages = []
        st.session_state.session_id = None # Reset session_id, backend will create new one
        st.sidebar.success(f"User set to: {st.session_state.user_id}\nAITA Persona: {st.session_state.current_aita_display_name}")
        st.rerun() # Rerun to reflect changes, especially the title

    # --- Main Chat Interface ---
    st.title(f"Chat with {st.session_state.current_aita_display_name}")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if not st.session_state.user_id: # Ensure user_id is set
        st.warning("Please enter a User ID in the sidebar to start chatting.")
    elif prompt := st.chat_input("What would you like to discuss or ask?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user's message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare Backend Request
        # Exclude system messages and only take recent history for the payload
        # The backend will prepend its own system prompt based on persona and context
        history_for_payload = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in st.session_state.messages[:-1] # Exclude the current user message already added
            if msg["role"] != "system" # Exclude any client-side system messages if they were used
        ][- (MAX_HISTORY_TURNS * 2):] # Keep last N turns (user + assistant pairs)

        payload = {
            "user_id": st.session_state.user_id,
            "aita_persona_id": st.session_state.current_aita_persona_id,
            "user_utterance": prompt,
            "conversation_history": history_for_payload,
            "session_id": st.session_state.session_id # Will be None for the first message of a session
            # Conceptual: Add subject, current_item_id if client is aware of these
            # "subject": "ReadingComprehension", # Example
            # "current_item_id": "passage_kitten_001" # Example
        }
        
        # Display AITA "thinking" animation and call backend
        with st.chat_message("assistant"):
            with st.spinner("AITA is thinking..."):
                try:
                    response = requests.post(f"{AITA_SERVICE_URL}/interact", json=payload, timeout=60) # Increased timeout
                    response.raise_for_status() 
                    response_data = response.json()
                    
                    assistant_response = response_data.get("aita_response", "Sorry, I encountered an issue processing your request.")
                    st.session_state.session_id = response_data.get("session_id") # Update/set session_id from backend
                
                except requests.exceptions.Timeout:
                    assistant_response = "Error: The AITA service timed out. Please try again."
                    st.error(assistant_response)
                except requests.exceptions.ConnectionError:
                    assistant_response = "Error: Could not connect to AITA service. Please ensure it's running."
                    st.error(assistant_response)
                except requests.exceptions.HTTPError as e:
                    error_detail = "Unknown error"
                    try:
                        error_detail = e.response.json().get("detail", e.response.text)
                    except: # Fallback if response is not JSON
                        error_detail = e.response.text
                    assistant_response = f"Error from AITA service: {e.response.status_code} - {error_detail}"
                    st.error(assistant_response)
                except json.JSONDecodeError: # Handle cases where response is not valid JSON
                    assistant_response = "Error: Received an invalid response from the AITA service."
                    st.error(assistant_response)
                except Exception as e:
                    assistant_response = f"An unexpected error occurred: {e}"
                    st.error(assistant_response)
            
            st.markdown(assistant_response) # Display AITA's response

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        # No explicit st.rerun() needed here as st.chat_input and widget interactions trigger it.
        # However, if state changes that don't trigger rerun, it might be needed.
        # The previous version had it; let's see if it's necessary after these changes.
        # For chat_input, it should rerun automatically.

# --- Running the App ---
if __name__ == "__main__":
    run_student_frontend_v2()
