import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel # Added
import uvicorn
from datetime import datetime
import os # Added
import json # Added for xAPI logging

# --- SDK Imports ---
# Assuming k12_mcp_client_sdk is in the Python path or installed
# If running locally in this project structure, path adjustments might be needed
# For this prototype, we'll assume it can be imported if in the same parent dir and path is set.
try:
    from k12_mcp_client_sdk.xapi_utils import create_interaction_xapi_statement, log_xapi_statement
except ImportError:
    print("WARNING: k12_mcp_client_sdk.xapi_utils not found. xAPI Logging will be basic.")
    # Define dummy functions if import fails, so service can still run
    def create_interaction_xapi_statement(**kwargs): return kwargs # Returns a dict, not a real statement
    def log_xapi_statement(statement, filepath, logger=None): print(f"DUMMY_LOG_TO_{filepath}: {statement}")

# --- Moderation Service Import ---
try:
    from moderation_service import ModerationService
except ImportError:
    print("WARNING: moderation_service.py not found. Moderation will be disabled.")
    class ModerationService: # Dummy service
        def __init__(self, logger=None): self.logger = logger; print("INFO: Using DUMMY ModerationService.")
        def check_text(self, text:str) -> Dict[str, Any]: 
            return {"is_safe": True, "flagged_categories": [], "scores": {}, "model_used": "dummy_moderation_disabled"}

# --- 1. Pydantic Models (from previous version, largely unchanged) ---
class UserProfileCreate(BaseModel):
    username: str
    grade_level: Optional[int] = None
    preferred_aita_persona_id: Optional[str] = None

class UserProfile(UserProfileCreate):
    user_id: str
    created_at: datetime

class InteractionRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: str 
    aita_persona_id: str = "default_phi3_base" 
    user_utterance: str
    conversation_history: List[Dict[str, str]] = []
    # Optional fields for richer context if client sends them directly
    # (Alternative to fetching from a separate MCP context server for simple cases)
    subject: Optional[str] = None 
    current_item_id: Optional[str] = None
    current_item_title: Optional[str] = None
    current_item_text_snippet: Optional[str] = None
    target_learning_objectives: Optional[List[Dict[str,str]]] = None


class InteractionResponse(BaseModel):
    session_id: str
    aita_response: str
    debug_info: Optional[Dict[str, Any]] = None

# --- 2. FastAPI App Initialization & Global Configurations ---
app = FastAPI(title="AITA Interaction Service", version="0.3.0") # Version bump for new features

BASE_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct" # Base model for all personas for now
XAPI_LOG_FILE_PATH = "service_xapi_statements.jsonl"

ADAPTER_CONFIG: Dict[str, str] = {
    "ReadingExplorerAITA_4thGrade_Pilot1": "./adapters/reading_explorer_pilot1", # Conceptual path
    "EcoExplorerAITA_7thGrade_Pilot1": "./adapters/eco_explorer_pilot1",       # Conceptual path
    # "default_phi3_base" is implicitly the base model without an adapter
}
LOADED_MODELS_CACHE: Dict[str, Dict[str, Any]] = {} # Cache for {persona_id: {"model": ..., "tokenizer": ..., "device": ...}}

# --- Mock LMS Data (Simulated Context Provider) ---
# Copied from lms_mcp_server_mock.py for self-contained simulated context
DEFAULT_4TH_GRADE_PASSAGES: List[Dict[str, str]] = [
    {"id": "passage_kitten_001", "title": "Lily the Lost Kitten", "text": "Lily the little kitten was lost..."},
    {"id": "passage_leaves_001", "title": "Why Leaves Change Color", "text": "In autumn, many leaves change..."}
]
DEFAULT_7TH_GRADE_SCIENCE_PASSAGES: List[Dict[str, str]] = [
    {"id": "eco_passage_foodweb_001", "title": "Forest Food Web", "text": "In a forest ecosystem, energy flows..."},
    {"id": "eco_passage_biotic_abiotic_001", "title": "Pond Life", "text": "A pond is teeming with life..."}
]
def get_passage_snippet(passage_text: str, word_count: int = 25) -> str:
    words = passage_text.split(); return " ".join(words[:word_count]) + "..." if len(words) > word_count else passage_text

MOCK_DB: Dict[str, Any] = {
    "student_activity_contexts": {
        "student001_ReadingComprehension_passage_kitten_001": {"student_id_anonymized": "student001", "subject": "ReadingComprehension", "current_passage_id": "passage_kitten_001", "current_passage_title": DEFAULT_4TH_GRADE_PASSAGES[0]["title"], "current_passage_text_snippet": get_passage_snippet(DEFAULT_4TH_GRADE_PASSAGES[0]["text"]), "target_learning_objectives_for_activity": [{"lo_id": "RC.4.LO1", "description": "Identify main idea."}], "teacher_notes_for_student_on_lo": "Focus on Lily's feelings."},
        "student001_Ecology_eco_passage_foodweb_001": {"student_id_anonymized": "student001", "subject": "Ecology", "current_item_id": "eco_passage_foodweb_001", "current_item_title": DEFAULT_7TH_GRADE_SCIENCE_PASSAGES[0]["title"], "current_item_text_snippet": get_passage_snippet(DEFAULT_7TH_GRADE_SCIENCE_PASSAGES[0]["text"]), "target_learning_objectives_for_activity": [{"lo_id": "SCI.7.ECO.LO1", "description": "Understand food webs."}]}
    }
}
USER_PROFILES_DB: Dict[str, UserProfile] = {} # In-memory user store

# --- Services ---
moderation_service: ModerationService

# --- 3. Model Loading Logic ---
def get_model_and_tokenizer_for_persona(persona_id: str, base_model_id: str) -> tuple[Optional[Any], Optional[Any], Optional[torch.device]]:
    if persona_id in LOADED_MODELS_CACHE:
        print(f"INFO: Returning cached model for persona: {persona_id}")
        cached = LOADED_MODELS_CACHE[persona_id]
        return cached["model"], cached["tokenizer"], cached["device"]

    print(f"INFO: Attempting to load model for persona: {persona_id} (base: {base_model_id})")
    try:
        current_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        local_tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
        if local_tokenizer.pad_token is None:
            local_tokenizer.pad_token = local_tokenizer.eos_token

        local_model = AutoModelForCausalLM.from_pretrained(
            base_model_id, torch_dtype="auto", trust_remote_code=True
        )
        
        adapter_path = ADAPTER_CONFIG.get(persona_id)
        if adapter_path and os.path.exists(adapter_path): # Check if path exists
            print(f"INFO: Found adapter for '{persona_id}' at '{adapter_path}'. Loading...")
            try:
                local_model = PeftModel.from_pretrained(local_model, adapter_path)
                print(f"INFO: PEFT adapter '{adapter_path}' loaded successfully for '{persona_id}'.")
            except Exception as e_adapter:
                print(f"ERROR: Failed to load PEFT adapter for '{persona_id}' from '{adapter_path}': {e_adapter}. Using base model.")
        elif adapter_path: # Path configured but does not exist
             print(f"WARNING: Adapter path '{adapter_path}' for persona '{persona_id}' not found. Using base model.")
        else: # No adapter configured for this persona_id, use base model
            print(f"INFO: No specific adapter for persona '{persona_id}'. Using base model '{base_model_id}'.")

        local_model.to(current_device)
        local_model.eval()
        
        LOADED_MODELS_CACHE[persona_id] = {"model": local_model, "tokenizer": local_tokenizer, "device": current_device}
        print(f"INFO: Model & tokenizer for persona '{persona_id}' loaded and cached.")
        return local_model, local_tokenizer, current_device
    except Exception as e:
        print(f"ERROR: Failed to load model/tokenizer for persona '{persona_id}': {e}")
        return None, None, None

@app.on_event("startup")
async def startup_event():
    global moderation_service
    print("INFO: Service Startup: Initializing Moderation Service...")
    try:
        moderation_service = ModerationService() # Add logger if available globally
        print("INFO: Moderation Service initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize real ModerationService: {e}. Using DUMMY service.")
        class DummyModService:
            def check_text(self, text:str): return {"is_safe": True, "flagged_categories": [], "scores": {}, "model_used": "dummy_moderation_startup_failed"}
        moderation_service = DummyModService()
    
    # Pre-load default base model
    print("INFO: Service Startup: Pre-loading default base model...")
    get_model_and_tokenizer_for_persona("default_phi3_base", BASE_MODEL_ID)
    # Conceptual: Pre-load other common personas if desired
    # get_model_and_tokenizer_for_persona("ReadingExplorerAITA_4thGrade_Pilot1", BASE_MODEL_ID)


# --- 4. Simulated LMS Context Function ---
def get_simulated_lms_context(user_id: str, subject: Optional[str], item_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not subject or not item_id: # If subject/item_id not provided in request, try to find a default for user
        # This logic can be more sophisticated, e.g. based on user's last activity
        for key, context in MOCK_DB["student_activity_contexts"].items():
            if key.startswith(user_id):
                print(f"INFO: Found a default context for user {user_id}: {key}")
                return context
        print(f"INFO: No specific context found for user {user_id} with subject/item, and no default context available.")
        return None

    resource_key = f"{user_id}_{subject}_{item_id}"
    context = MOCK_DB["student_activity_contexts"].get(resource_key)
    if context:
        print(f"INFO: Simulated LMS context found for key: {resource_key}")
    else:
        print(f"WARNING: No simulated LMS context found for key: {resource_key}")
    return context

# --- 5. User Profile Endpoints (from previous version, largely unchanged) ---
@app.post("/users/register", response_model=UserProfile, status_code=201)
async def register_user(user_create: UserProfileCreate):
    for profile in USER_PROFILES_DB.values():
        if profile.username == user_create.username:
            raise HTTPException(status_code=400, detail=f"Username '{user_create.username}' already exists.")
    user_id = uuid.uuid4().hex; created_at = datetime.utcnow()
    user_profile = UserProfile(user_id=user_id, username=user_create.username, grade_level=user_create.grade_level, preferred_aita_persona_id=user_create.preferred_aita_persona_id, created_at=created_at)
    USER_PROFILES_DB[user_id] = user_profile
    print(f"INFO: User registered: {user_profile.username} (ID: {user_id})")
    return user_profile

@app.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    user_profile = USER_PROFILES_DB.get(user_id)
    if not user_profile: raise HTTPException(status_code=404, detail="User not found")
    return user_profile

# --- 6. /interact Endpoint (Significantly Updated) ---
@app.post("/interact", response_model=InteractionResponse)
async def interact_with_aita(request: InteractionRequest):
    current_session_id = request.session_id if request.session_id else uuid.uuid4().hex
    timestamp_utc = datetime.utcnow().isoformat() + "Z"

    # Determine AITA persona and load model
    effective_aita_persona_id = request.aita_persona_id
    user_profile = USER_PROFILES_DB.get(request.user_id)
    if user_profile and user_profile.preferred_aita_persona_id:
        effective_aita_persona_id = user_profile.preferred_aita_persona_id
        print(f"INFO: Using user's preferred AITA: {effective_aita_persona_id}")
    
    current_model, current_tokenizer, current_device = get_model_and_tokenizer_for_persona(effective_aita_persona_id, BASE_MODEL_ID)
    if not current_model or not current_tokenizer or not current_device:
        raise HTTPException(status_code=503, detail=f"Model resources for persona '{effective_aita_persona_id}' are not available.")

    # Fetch simulated LMS context
    lms_context = get_simulated_lms_context(request.user_id, request.subject, request.current_item_id)
    
    # Prepare context for system prompt and logging (more robust extraction)
    grade_level_info = f" The student is in grade {user_profile.grade_level}." if user_profile and user_profile.grade_level else ""
    passage_title = lms_context.get("current_passage_title", lms_context.get("current_item_title", "the current topic")) if lms_context else "the current topic"
    passage_snippet = lms_context.get("current_passage_text_snippet", lms_context.get("current_item_text_snippet", "a relevant educational activity")) if lms_context else "a relevant educational activity"
    lo_list = lms_context.get("target_learning_objectives_for_activity", []) if lms_context else []
    lo_desc = lo_list[0].get("description", "the learning goal") if lo_list and isinstance(lo_list, list) and len(lo_list) > 0 else "the learning goal"
    lo_id_log = lo_list[0].get("lo_id", "UNKNOWN_LO") if lo_list and isinstance(lo_list, list) and len(lo_list) > 0 else "UNKNOWN_LO"
    teacher_notes_log = lms_context.get("teacher_notes_for_student_on_lo", "") if lms_context else ""
    passage_id_log = lms_context.get("current_passage_id", lms_context.get("current_item_id", "unknown_item")) if lms_context else "unknown_item"

    system_prompt = f"You are {effective_aita_persona_id}, a helpful AI Tutor.{grade_level_info} You are discussing '{passage_title}' related to the learning objective: '{lo_desc}'. Passage snippet: \"{passage_snippet}\". {f'Teacher note: \"{teacher_notes_log}\" ' if teacher_notes_log else ''}Respond clearly, concisely, and age-appropriately. Guide the student; don't just give answers."

    # Input Moderation
    mod_input_results = moderation_service.check_text(request.user_utterance)
    if not mod_input_results["is_safe"]:
        aita_final_response = "I'm sorry, I can't process that request due to content policy. Let's focus on our learning task."
        # Log xAPI for flagged input
        xapi_log_data_input_flagged = {
            "actor_name": "ServiceUser", "actor_account_name": request.user_id,
            "verb_id": "http://adlnet.gov/expapi/verbs/attempted", "verb_display": "attempted to submit input",
            "object_activity_id": f"http://example.com/aita_interaction/{current_session_id}/turn_input_flagged",
            "object_activity_name": "User Input Moderation Event", "object_activity_description": "User input was flagged by moderation.",
            "session_id": current_session_id, "aita_persona": effective_aita_persona_id,
            "result_response": aita_final_response,
            "result_extensions": {"input_moderation_details": mod_input_results, "user_utterance_raw": request.user_utterance},
            "context_parent_activity_id": f"http://example.com/content/{passage_id_log}",
            "context_extensions": {"learning_objective_active": lo_id_log}
        }
        log_xapi_statement(create_interaction_xapi_statement(**xapi_log_data_input_flagged), XAPI_LOG_FILE_PATH)
        return InteractionResponse(session_id=current_session_id, aita_response=aita_final_response, debug_info={"input_moderation_triggered": True})

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.user_utterance})

    try:
        prompt_text = current_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = current_tokenizer(prompt_text, return_tensors="pt", add_special_tokens=True).to(current_device)
        input_ids_length = inputs.input_ids.shape[1]
        
        start_time = time.time()
        with torch.no_grad():
            generated_outputs = current_model.generate(
                inputs.input_ids, max_new_tokens=300, eos_token_id=current_tokenizer.eos_token_id,
                pad_token_id=current_tokenizer.pad_token_id, do_sample=True, temperature=0.7, top_p=0.9
            )
        duration_s = time.time() - start_time
        
        response_ids = generated_outputs[0][input_ids_length:]
        aita_raw_response = current_tokenizer.decode(response_ids, skip_special_tokens=True).strip()
        
        # Output Moderation
        mod_output_results = moderation_service.check_text(aita_raw_response)
        aita_final_response = aita_raw_response
        if not mod_output_results["is_safe"]:
            aita_final_response = "I may have generated a response that isn't quite right. Let's try a different approach. What were you thinking about that part of the text?"

        # Full xAPI Logging
        xapi_log_data = {
            "actor_name": "ServiceUser", "actor_account_name": request.user_id,
            "verb_id": "http://adlnet.gov/expapi/verbs/interacted", "verb_display": "interacted with AITA",
            "object_activity_id": f"http://example.com/aita_interaction/{current_session_id}/turn_{uuid.uuid4().hex[:8]}",
            "object_activity_name": "AITA Interaction Turn",
            "object_activity_description": f"User '{request.user_id}' interacted with '{effective_aita_persona_id}' on content '{passage_title}'. LO: {lo_id_log}.",
            "session_id": current_session_id, "aita_persona": effective_aita_persona_id,
            "result_response": aita_final_response, "result_duration_seconds": duration_s,
            "result_extensions": {"input_moderation_details": mod_input_results, "output_moderation_details": mod_output_results},
            "context_parent_activity_id": f"http://example.com/content/{passage_id_log}",
            "context_extensions": {
                "learning_objective_active": lo_id_log,
                "full_prompt_to_llm": prompt_text, # Can be very long, consider truncating if needed for some LRSs
                "user_utterance_raw": request.user_utterance,
                "aita_response_raw": aita_raw_response
            }
        }
        log_xapi_statement(create_interaction_xapi_statement(**xapi_log_data), XAPI_LOG_FILE_PATH)
        
        return InteractionResponse(
            session_id=current_session_id, aita_response=aita_final_response,
            debug_info={"model_used": current_model.name_or_path if hasattr(current_model, "name_or_path") else base_model_id, 
                        "aita_persona_resolved": effective_aita_persona_id, 
                        "user_profile_found": bool(user_profile),
                        "lms_context_found": bool(lms_context)}
        )
    except Exception as e:
        print(f"ERROR: Exception during model interaction: {e}")
        # Log error xAPI?
        raise HTTPException(status_code=500, detail=f"Error during model interaction: {str(e)}")

# --- 7. Main block for Uvicorn ---
if __name__ == "__main__":
    print("INFO: Starting AITA Interaction Service with Uvicorn (V1 Full Implementation)...")
    # Create dummy adapter dirs if they don't exist, so path checks don't fail loudly if testing personas
    for path_val in ADAPTER_CONFIG.values():
        if not os.path.exists(path_val):
            try:
                os.makedirs(path_val)
                print(f"INFO: Created placeholder adapter directory: {path_val}")
            except OSError as e:
                print(f"WARNING: Could not create placeholder adapter directory {path_val}: {e}")

    uvicorn.run(app, host="0.0.0.0", port=8000)
