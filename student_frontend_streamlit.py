# To run: streamlit run student_frontend_streamlit.py
import streamlit as st
from typing import List, Dict, Any

# --- Session State Initialization ---
# This needs to be at the top level of the script for Streamlit's execution model.
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []
if "current_aita_persona" not in st.session_state:
    st.session_state.current_aita_persona: str = "Reading Explorer AITA" # V1 Hardcoded

# --- Mock AITA Response Function ---
def get_mock_aita_response(user_message: str, aita_persona: str) -> str:
    """
    Simulates an AITA's response based on user input and AITA persona.
    """
    user_message_lower = user_message.lower()

    if "hello" in user_message_lower or "hi" in user_message_lower:
        return f"Hello there! I'm {aita_persona}. How can I help you with your reading today?"
    elif "main idea" in user_message_lower:
        return f"{aita_persona} says: The main idea is what the story is mostly about! What do you think this passage is about?"
    elif "inference" in user_message_lower:
        return f"{aita_persona} thinks: Making an inference is like being a detective and using clues from the text! What clues do you see?"
    elif "vocabulary" in user_message_lower or "meaning of" in user_message_lower:
        # Added a simple vocab response for more interaction
        return f"{aita_persona} suggests: When you see a new word, try looking at the words around it for clues to its meaning! What word are you wondering about?"
    else:
        return f"{aita_persona} is thinking... That's an interesting question! Can you tell me more about what you're wondering?"

# --- Streamlit UI Layout and Logic ---
def run_student_frontend():
    st.set_page_config(page_title="AITA Learning Zone", layout="wide")
    st.title(f"Chat with {st.session_state.current_aita_persona}")

    # Display Chat History
    # This will iterate through st.session_state.messages on each Streamlit re-run
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    # The `key` argument can be used to manage widget state if needed, but for simple chat_input,
    # Streamlit handles its state well.
    if prompt := st.chat_input("What would you like to discuss or ask?"):
        # Add user's message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user's message (Streamlit will re-run and the loop above will display it)
        # No need for an explicit `st.markdown` here for the user message due to re-run.

        # Get and add AITA's response
        assistant_response = get_mock_aita_response(prompt, st.session_state.current_aita_persona)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Force a re-run to display the new assistant message immediately.
        # st.chat_input causes a re-run automatically when input is submitted.
        # If we needed to force it for other reasons: st.experimental_rerun() or st.rerun() in newer versions
        st.rerun() # Ensures the assistant message is displayed immediately after processing

# --- Running the App ---
if __name__ == "__main__":
    # The Streamlit elements are defined in run_student_frontend,
    # but Streamlit executes the script from top to bottom.
    # Session state initialization should be outside any function if it needs to persist
    # across reruns and be globally accessible via st.session_state.
    # The call to run_student_frontend() will build the UI.
    run_student_frontend()
