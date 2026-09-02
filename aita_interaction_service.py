import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer # No longer directly needed here
# from peft import PeftModel # No longer directly needed here
import uvicorn
from datetime import datetime
import os
import json

# --- Import new utility ---
from model_loader_utils import load_model_tokenizer_with_adapter, DefaultLogger
# We'll use DefaultLogger from the utility if a more complex FastAPI/Uvicorn logger isn't set up globally

# --- SDK Imports ---
try:
    from k12_mcp_client_sdk.xapi_utils import create_interaction_xapi_statement, log_xapi_statement
except ImportError:
    print("WARNING: k12_mcp_client_sdk.xapi_utils not found. xAPI Logging will be basic.")
    def create_interaction_xapi_statement(**kwargs): return kwargs
    def log_xapi_statement(statement, filepath, logger=None): print(f"DUMMY_LOG_TO_{filepath}: {statement}")

# --- Moderation Service Import ---
try:
    from moderation_service import ModerationService
except ImportError:
    print("WARNING: moderation_service.py not found. Moderation will be disabled.")
    class ModerationService:
        def __init__(self, logger=None): self.logger = logger; print("INFO: Using DUMMY ModerationService.")
        def check_text(self, text:str) -> Dict[str, Any]:
            return {"is_safe": True, "flagged_categories": [], "scores": {}, "model_used": "dummy_moderation_disabled"}

# --- 1. Pydantic Models ---
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
app = FastAPI(title="AITA Interaction Service", version="0.4.0") # Version bump for utility integration

BASE_MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
XAPI_LOG_FILE_PATH = "service_xapi_statements.jsonl"

ADAPTER_CONFIG: Dict[str, str] = {
    "ReadingExplorerAITA_4thGrade_Pilot1": "./adapters/reading_explorer_pilot1",
    "EcoExplorerAITA_7thGrade_Pilot1": "./adapters/eco_explorer_pilot1",
}
LOADED_MODELS_CACHE: Dict[str, Dict[str, Any]] = {}

# --- Mock LMS Data ---
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
USER_PROFILES_DB: Dict[str, UserProfile] = {}

# --- Services & Loggers ---
moderation_service: ModerationService
service_logger = DefaultLogger() # Use DefaultLogger from utility, or integrate with Uvicorn's logger

# --- 3. Model Loading Logic (Refactored) ---
def get_model_and_tokenizer_for_persona(persona_id: str, base_model_id: str) -> tuple[Optional[Any], Optional[Any], Optional[torch.device]]:
    if persona_id in LOADED_MODELS_CACHE:
        service_logger.info(f"Returning cached model for persona: {persona_id}")
        cached = LOADED_MODELS_CACHE[persona_id]
        return cached["model"], cached["tokenizer"], cached["device"]

    service_logger.info(f"Attempting to load model for persona: {persona_id} (base: {base_model_id})")

    adapter_path_for_persona = ADAPTER_CONFIG.get(persona_id)

    # Call the shared utility
    # trust_remote_code_flag and torch_dtype_str can be global configs or defaults in the utility
    model, tokenizer, device = load_model_tokenizer_with_adapter(
        model_id=base_model_id,
        adapter_path=adapter_path_for_persona,
        logger=service_logger,
        trust_remote_code_flag=True, # Default from utility
        torch_dtype_str="auto" # Default from utility
    )

    if model and tokenizer and device:
        LOADED_MODELS_CACHE[persona_id] = {"model": model, "tokenizer": tokenizer, "device": device}
        service_logger.info(f"Model & tokenizer for persona '{persona_id}' loaded and cached.")
        return model, tokenizer, device
    else:
        service_logger.error(f"Failed to load model/tokenizer for persona '{persona_id}' using utility.")
        return None, None, None

@app.on_event("startup")
async def startup_event():
    global moderation_service # Ensure we're assigning to the global instance
    service_logger.info("Service Startup: Initializing Moderation Service...")
    try:
        moderation_service = ModerationService(logger=service_logger)
        service_logger.info("Moderation Service initialized successfully.")
    except Exception as e:
        service_logger.error(f"Failed to initialize real ModerationService: {e}. Using DUMMY service.", exc_info=True)
        class _DummyModService: # Renamed to avoid potential conflicts if moderation_service.py also defines DummyModerationService
            def __init__(self, logger=None): self.logger = logger; service_logger.info("Using _DummyModService.")
            def check_text(self, text:str) -> Dict[str, Any]:
                return {"is_safe": True, "flagged_categories": [], "scores": {}, "model_used": "dummy_moderation_startup_failed"}
        moderation_service = _DummyModService(logger=service_logger)

    service_logger.info("Service Startup: Pre-loading default base model ('default_phi3_base')...")
    get_model_and_tokenizer_for_persona("default_phi3_base", BASE_MODEL_ID)


# --- 4. Simulated LMS Context Function (remains the same) ---
def get_simulated_lms_context(user_id: str, subject: Optional[str], item_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not subject or not item_id:
        for key, context in MOCK_DB["student_activity_contexts"].items():
            if key.startswith(user_id):
                service_logger.info(f"Found a default context for user {user_id}: {key}")
                return context
        service_logger.info(f"No specific context found for user {user_id} with subject/item, and no default context available.")
        return None
    resource_key = f"{user_id}_{subject}_{item_id}"
    context = MOCK_DB["student_activity_contexts"].get(resource_key)
    if context: service_logger.info(f"Simulated LMS context found for key: {resource_key}")
    else: service_logger.warning(f"No simulated LMS context found for key: {resource_key}")
    return context

# --- 5. User Profile Endpoints (remains the same) ---
@app.post("/users/register", response_model=UserProfile, status_code=201)
async def register_user(user_create: UserProfileCreate):
    for profile in USER_PROFILES_DB.values():
        if profile.username == user_create.username:
            raise HTTPException(status_code=400, detail=f"Username '{user_create.username}' already exists.")
    user_id = uuid.uuid4().hex; created_at = datetime.utcnow()
    user_profile = UserProfile(user_id=user_id, **user_create.model_dump(), created_at=created_at) # Use model_dump for Pydantic v2
    USER_PROFILES_DB[user_id] = user_profile
    service_logger.info(f"User registered: {user_profile.username} (ID: {user_id})")
    return user_profile

@app.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    user_profile = USER_PROFILES_DB.get(user_id)
    if not user_profile: raise HTTPException(status_code=404, detail="User not found")
    return user_profile

# --- 6. /interact Endpoint (Uses refactored model loader) ---
@app.post("/interact", response_model=InteractionResponse)
async def interact_with_aita(request: InteractionRequest):
    current_session_id = request.session_id if request.session_id else uuid.uuid4().hex
    timestamp_utc = datetime.utcnow().isoformat() + "Z"

    effective_aita_persona_id = request.aita_persona_id
    user_profile = USER_PROFILES_DB.get(request.user_id)
    if user_profile and user_profile.preferred_aita_persona_id:
        effective_aita_persona_id = user_profile.preferred_aita_persona_id
        service_logger.info(f"Using user's preferred AITA: {effective_aita_persona_id}")

    # Use the refactored function to get model, tokenizer, device
    current_model, current_tokenizer, current_device = get_model_and_tokenizer_for_persona(effective_aita_persona_id, BASE_MODEL_ID)

    if not current_model or not current_tokenizer or not current_device: # Check all three
        service_logger.error(f"Model resources for persona '{effective_aita_persona_id}' are not available (utility returned None). Check startup & persona loading logs.")
        raise HTTPException(status_code=503, detail=f"Model resources for persona '{effective_aita_persona_id}' are not available.")

    lms_context = get_simulated_lms_context(request.user_id, request.subject, request.current_item_id)
    grade_level_info = f" The student is in grade {user_profile.grade_level}." if user_profile and user_profile.grade_level else ""
    passage_title = lms_context.get("current_passage_title", lms_context.get("current_item_title", "the current topic")) if lms_context else "the current topic"
    passage_snippet = lms_context.get("current_passage_text_snippet", lms_context.get("current_item_text_snippet", "a relevant educational activity")) if lms_context else "a relevant educational activity"
    lo_list = lms_context.get("target_learning_objectives_for_activity", []) if lms_context else []
    primary_lo = lo_list[0] if lo_list and isinstance(lo_list, list) and len(lo_list) > 0 else {}
    lo_desc = primary_lo.get("description", "the learning goal")
    lo_id_log = primary_lo.get("lo_id", "UNKNOWN_LO")
    teacher_notes_log = lms_context.get("teacher_notes_for_student_on_lo", "") if lms_context else ""
    passage_id_log = lms_context.get("current_passage_id", lms_context.get("current_item_id", "unknown_item")) if lms_context else "unknown_item"

    system_prompt = f"You are {effective_aita_persona_id}, a helpful AI Tutor.{grade_level_info} You are discussing '{passage_title}' related to the learning objective: '{lo_desc}'. Passage snippet: \"{passage_snippet}\". {f'Teacher note: \"{teacher_notes_log}\" ' if teacher_notes_log else ''}Respond clearly, concisely, and age-appropriately. Guide the student; don't just give answers."

    mod_input_results = moderation_service.check_text(request.user_utterance) # Ensure moderation_service is initialized
    if not mod_input_results["is_safe"]:
        aita_final_response = "I'm sorry, I can't process that request due to content policy. Let's focus on our learning task."
        # Log xAPI (simplified for brevity here, full structure in client)
        log_xapi_statement({"error": "unsafe input", "user_id": request.user_id, "input": request.user_utterance}, XAPI_LOG_FILE_PATH, service_logger)
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

        mod_output_results = moderation_service.check_text(aita_raw_response)
        aita_final_response = aita_raw_response
        if not mod_output_results["is_safe"]:
            aita_final_response = "I may have generated a response that isn't quite right. Let's try a different approach."

        xapi_log_data = {
            "actor_name": "ServiceUser", "actor_account_name": request.user_id,
            "verb_id": "http://adlnet.gov/expapi/verbs/interacted", "verb_display": "interacted with AITA Service",
            "object_activity_id": f"http://example.com/aita_service/{current_session_id}/turn_{uuid.uuid4().hex[:8]}",
            "object_activity_name": "AITA Service Interaction Turn",
            "object_activity_description": f"User '{request.user_id}' interacted with '{effective_aita_persona_id}' on content '{passage_title}'. LO: {lo_id_log}.",
            "session_id": current_session_id, "aita_persona": effective_aita_persona_id,
            "result_response": aita_final_response, "result_duration_seconds": duration_s,
            "result_extensions": {"input_moderation_details": mod_input_results, "output_moderation_details": mod_output_results},
            "context_parent_activity_id": f"http://example.com/content/{passage_id_log}",
            "context_extensions": {
                "learning_objective_active": lo_id_log, "full_prompt_to_llm": prompt_text,
                "user_utterance_raw": request.user_utterance, "aita_response_raw": aita_raw_response,
                "pedagogical_notes": ["Service Placeholder: Note 1", "Service Placeholder: Note 2"], # Placeholder reasoner fields
                "aita_turn_narrative_rationale": "Service Placeholder: Simulated rationale for this turn."
            }
        }
        log_xapi_statement(create_interaction_xapi_statement(**xapi_log_data), XAPI_LOG_FILE_PATH, service_logger)

        return InteractionResponse(
            session_id=current_session_id, aita_response=aita_final_response,
            debug_info={"model_used": current_model.name_or_path if hasattr(current_model, "name_or_path") else base_model_id,
                        "aita_persona_resolved": effective_aita_persona_id,
                        "user_profile_found": bool(user_profile),
                        "lms_context_found": bool(lms_context)}
        )
    except Exception as e:
        service_logger.error(f"Exception during model interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during model interaction: {str(e)}")

# --- 7. Main block for Uvicorn ---
if __name__ == "__main__":
    service_logger.info("Starting AITA Interaction Service with Uvicorn (V1 Full Implementation with Model Loader Utility)...")
    for path_val in ADAPTER_CONFIG.values():
        if not os.path.exists(path_val):
            try:
                os.makedirs(path_val)
                service_logger.info(f"Created placeholder adapter directory: {path_val}")
            except OSError as e:
                service_logger.warning(f"Could not create placeholder adapter directory {path_val}: {e}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
