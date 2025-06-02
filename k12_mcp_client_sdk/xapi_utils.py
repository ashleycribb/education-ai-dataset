import json
import datetime
import uuid
from typing import Dict, Any, Optional, List

def create_interaction_xapi_statement(
    actor_name: str,
    actor_account_name: str, # Typically a persistent, unique ID for the user
    verb_id: str,
    verb_display: str,
    object_activity_id: str,
    object_activity_name: str,
    object_activity_description: str,
    session_id: Optional[str] = None,
    aita_persona: Optional[str] = "GenericAITA",
    result_response: Optional[str] = None,
    result_duration_seconds: Optional[float] = None,
    result_extensions: Optional[Dict[str, Any]] = None,
    context_parent_activity_id: Optional[str] = None,
    context_extensions: Optional[Dict[str, Any]] = None,
    timestamp_utc: Optional[str] = None
) -> Dict[str, Any]:
    """
    Constructs and returns a dictionary closely resembling an xAPI statement structure.
    """
    if timestamp_utc is None:
        timestamp_utc = datetime.datetime.utcnow().isoformat() + "Z"

    statement = {
        "id": str(uuid.uuid4()),
        "actor": {
            "objectType": "Agent",
            "name": actor_name, # User-friendly name
            "account": { # Account object for unique identification
                "homePage": "http://example.com/k12_lms", # Placeholder homepage for the account provider
                "name": actor_account_name 
            }
        },
        "verb": {
            "id": verb_id, # e.g., "http://adlnet.gov/expapi/verbs/interacted"
            "display": {"en-US": verb_display} # e.g., "interacted with"
        },
        "object": {
            "objectType": "Activity",
            "id": object_activity_id, # Unique ID for the activity or interaction point
            "definition": {
                "name": {"en-US": object_activity_name},
                "description": {"en-US": object_activity_description},
                "type": "http://adlnet.gov/expapi/activities/interaction" # Example type
            }
        },
        "result": {},
        "context": {
            "contextActivities": {},
            "extensions": {
                "http://example.com/xapi/extensions/aita_persona": aita_persona
            }
        },
        "timestamp": timestamp_utc,
        "authority": { # Placeholder authority
            "objectType": "Agent",
            "name": "K12 MCP Client SDK Logger",
            "account": {
                "homePage": "http://example.com/k12_mcp_client_sdk",
                "name": "k12_mcp_client_sdk_v0.1.0"
            }
        }
    }

    if session_id:
        if statement["context"]["extensions"] is None: statement["context"]["extensions"] = {}
        statement["context"]["extensions"]["http://example.com/xapi/extensions/session_id"] = session_id
        
    if result_response is not None:
        statement["result"]["response"] = result_response
        
    if result_duration_seconds is not None:
        # Format duration as ISO 8601 duration string
        statement["result"]["duration"] = f"PT{result_duration_seconds:.2f}S"
        
    if result_extensions:
        if statement["result"].get("extensions") is None: statement["result"]["extensions"] = {}
        statement["result"]["extensions"].update(result_extensions)
        
    if context_parent_activity_id:
        if statement["context"]["contextActivities"].get("parent") is None: statement["context"]["contextActivities"]["parent"] = []
        statement["context"]["contextActivities"]["parent"].append({"id": context_parent_activity_id})
        
    if context_extensions:
        if statement["context"].get("extensions") is None: statement["context"]["extensions"] = {}
        statement["context"]["extensions"].update(context_extensions)

    return statement

def log_xapi_statement(statement: Dict[str, Any], filepath: str, logger: Optional[Any] = None):
    """
    Appends the given statement dictionary as a JSON string to the specified file (JSON Lines format).
    Includes basic error handling for file I/O.
    """
    try:
        with open(filepath, 'a') as f:
            json.dump(statement, f)
            f.write('\n')
        if logger:
            logger.info(f"Successfully logged xAPI statement ID {statement.get('id')} to {filepath}")
    except IOError as e:
        if logger:
            logger.error(f"Error logging xAPI statement ID {statement.get('id')} to {filepath}: {e}")
    except Exception as e: # Catch other potential errors like JSON serialization issues
        if logger:
            logger.error(f"An unexpected error occurred while logging statement ID {statement.get('id')}: {e}")
