import logging
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# --- Pydantic Model for xAPI Statement ---
class XAPIStatement(BaseModel):
    actor: Dict[str, Any]
    verb: Dict[str, Any]
    object: Dict[str, Any]
    context: Dict[str, Any] | None = None
    timestamp: str | None = None

# --- FastAPI Application ---
app = FastAPI()

# --- Logging Configuration ---
# Log to stdout, which is the standard for containerized applications
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# --- API Endpoint ---
@app.post("/statement")
async def receive_statement(statement: XAPIStatement):
    """
    Receives an xAPI statement via HTTP POST, logs it, and returns a confirmation.
    """
    try:
        actor_name = statement.actor.get("name", "Unknown Actor")
        verb_display = statement.verb.get("display", {}).get("en-US", "Unknown Verb")

        logging.info(f"Received statement via HTTP: '{actor_name} {verb_display}'")

        return {"success": True, "message": "Statement received and logged."}
    except Exception as e:
        logging.error(f"An error occurred while processing the statement: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

# --- Root Endpoint for Health Check ---
@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the server is running.
    """
    return {"message": "MCP Service is running. Post xAPI statements to /statement."}
