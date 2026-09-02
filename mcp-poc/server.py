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
import socket
import json
import logging
import os

def main():
    """
    Main function to run the MCP server.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'server.log')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file_path,
        filemode='w' # Overwrite log on each start
    )

    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    logging.info(f"--- MCP Server listening on {host}:{port} ---")
    print(f"--- MCP Server listening on {host}:{port} ---") # Keep this for interactive mode

    while True:
        conn, addr = server_socket.accept()
        logging.info(f"Connection from {addr}")
        try:
            # Receive the data from the client
            data = conn.recv(4096)
            if data:
                # Decode the JSON data
                statement = json.loads(data.decode('utf-8'))
                actor_name = statement.get("actor", {}).get("name", "Unknown Actor")
                verb_display = statement.get("verb", {}).get("display", {}).get("en-US", "Unknown Verb")

                logging.info(f"Received statement: '{actor_name} {verb_display}'")

                # Send a success response back to the client
                response = {"success": True, "message": "Statement received and processed."}
                conn.sendall(json.dumps(response).encode('utf-8'))
        except json.JSONDecodeError:
            logging.error("Received invalid JSON.")
            response = {"success": False, "message": "Invalid JSON received."}
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            response = {"success": False, "message": f"An error occurred: {e}"}
            conn.sendall(json.dumps(response).encode('utf-8'))
        finally:
            logging.info("Closing connection.")
            conn.close()

if __name__ == "__main__":
    main()
