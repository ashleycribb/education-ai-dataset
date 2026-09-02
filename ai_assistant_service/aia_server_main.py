import uuid
from fastapi import FastAPI, HTTPException, Body, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple

# Assuming assistant_logic_module is in the same directory (ai_assistant_service)
from .assistant_logic_module import AIAssistant, get_current_activity
from .db import connect_db, disconnect_db, create_raw_xapi_table_if_not_exists # Import DB functions
from fastapi.middleware.cors import CORSMiddleware # Import CORS

# --- Pydantic Models ---
class StartRequest(BaseModel):
    user_id: str
    activity_key: str

class InteractRequest(BaseModel):
    session_id: str
    student_response: str

class ApiResponse(BaseModel):
    session_id: str
    ai_messages: List[str]
    xapi_statements: List[Dict[str, Any]]
    is_activity_complete: bool

# --- FastAPI App Setup ---
app = FastAPI(
    title="AI Assistant Service",
    version="0.1.0",
    description="Provides API endpoints to interact with an AI learning assistant."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development/demo.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all standard HTTP methods.
    allow_headers=["*"],  # Allows all headers.
)

# In-memory session storage
active_sessions: Dict[str, AIAssistant] = {}

# --- Database Lifecycle Events ---
@app.on_event("startup")
async def startup_db_client():
    await connect_db()
    # This is a good place to create tables if they don't exist,
    # especially for development or simpler setups.
    # For production, migrations (e.g. Alembic) are usually preferred.
    await create_raw_xapi_table_if_not_exists()

@app.on_event("shutdown")
async def shutdown_db_client():
    await disconnect_db()

# --- API Endpoints ---

@app.post("/activity/start", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def start_activity_endpoint(request: StartRequest):
    """
    Starts a new learning activity session for a user with a given activity key.
    """
    session_id = uuid.uuid4().hex
    assistant = AIAssistant()

    activity_data_check = get_current_activity(request.user_id, request.activity_key)
    if not activity_data_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with key '{request.activity_key}' not found for user '{request.user_id}'."
        )

    await assistant.start_activity(user_id=request.user_id, activity_key=request.activity_key)
    active_sessions[session_id] = assistant

    ai_messages, xapi_statements, is_complete = assistant.get_pending_outputs()

    return ApiResponse(
        session_id=session_id,
        ai_messages=ai_messages,
        xapi_statements=xapi_statements,
        is_activity_complete=is_complete
    )

@app.post("/activity/interact", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def interact_with_activity_endpoint(request: InteractRequest):
    """
    Processes a student's response within an active learning session.
    """
    assistant = active_sessions.get(request.session_id)
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{request.session_id}' not found."
        )

    if assistant.is_activity_complete:
        ai_messages, xapi_statements, is_complete = assistant.get_pending_outputs()
        final_message = "This activity is already complete. Please start a new activity."
        if not ai_messages or (ai_messages and ai_messages[-1] != final_message):
             ai_messages.append(final_message)

        return ApiResponse(
            session_id=request.session_id,
            ai_messages=ai_messages,
            xapi_statements=xapi_statements,
            is_activity_complete=is_complete
        )

    await assistant.process_student_input(student_response=request.student_response)
    ai_messages, xapi_statements, is_complete = assistant.get_pending_outputs()

    return ApiResponse(
        session_id=request.session_id,
        ai_messages=ai_messages,
        xapi_statements=xapi_statements,
        is_activity_complete=is_complete
    )

@app.get("/")
async def read_root():
    return {"message": "AI Assistant Service is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("aia_server_main:app", host="0.0.0.0", port=8002, reload=True)
