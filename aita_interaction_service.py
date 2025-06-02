import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn
from datetime import datetime # Added

# --- 1. Pydantic Models ---
class UserProfileCreate(BaseModel):
    username: str
    grade_level: Optional[int] = None
    preferred_aita_persona_id: Optional[str] = None # e.g., "ReadingExplorerAITA_4thGrade_v1_adapter"

class UserProfile(UserProfileCreate):
    user_id: str
    created_at: datetime

class InteractionRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: str # This should now ideally be a registered user_id
    aita_persona_id: str = "default_phi3_base"
    user_utterance: str
    conversation_history: List[Dict[str, str]] = []

class InteractionResponse(BaseModel):
    session_id: str
    aita_response: str
    debug_info: Optional[Dict[str, Any]] = None

# --- 2. FastAPI App Initialization & Model Loading ---
app = FastAPI(title="AITA Interaction Service", version="0.2.0") # Version bump

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
model: Optional[AutoModelForCausalLM] = None
tokenizer: Optional[AutoTokenizer] = None
device: Optional[torch.device] = None

# In-Memory User Store (Global)
USER_PROFILES_DB: Dict[str, UserProfile] = {}

@app.on_event("startup")
async def load_model_resources():
    global model, tokenizer, device
    print(f"INFO: Loading base model '{MODEL_ID}' at startup...")
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"INFO: Using device: {device}")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print(f"INFO: Tokenizer pad_token set to eos_token: {tokenizer.eos_token}")

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype="auto",
            trust_remote_code=True
        )
        model.to(device)
        model.eval()
        print(f"INFO: Model '{MODEL_ID}' loaded successfully on {device}.")
    except Exception as e:
        print(f"ERROR: Failed to load model or tokenizer at startup: {e}")
        model = None
        tokenizer = None

# --- 3. User Profile Endpoints ---
@app.post("/users/register", response_model=UserProfile, status_code=201)
async def register_user(user_create: UserProfileCreate):
    # Check if username already exists
    for profile in USER_PROFILES_DB.values():
        if profile.username == user_create.username:
            raise HTTPException(status_code=400, detail=f"Username '{user_create.username}' already exists.")

    user_id = uuid.uuid4().hex
    created_at = datetime.utcnow()

    user_profile = UserProfile(
        user_id=user_id,
        username=user_create.username,
        grade_level=user_create.grade_level,
        preferred_aita_persona_id=user_create.preferred_aita_persona_id,
        created_at=created_at
    )
    USER_PROFILES_DB[user_id] = user_profile
    print(f"INFO: User registered: {user_profile.username} (ID: {user_id})")
    return user_profile

@app.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    user_profile = USER_PROFILES_DB.get(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return user_profile

# --- 4. /interact Endpoint (Modified) ---
@app.post("/interact", response_model=InteractionResponse)
async def interact_with_aita(request: InteractionRequest):
    global model, tokenizer, device

    if model is None or tokenizer is None or device is None:
        print("ERROR: Model resources not available. Check startup logs.")
        raise HTTPException(status_code=503, detail="Model resources are not available.")

    current_session_id = request.session_id if request.session_id else uuid.uuid4().hex

    user_profile = USER_PROFILES_DB.get(request.user_id)
    effective_aita_persona_id = request.aita_persona_id
    system_prompt_addon = ""

    if user_profile:
        print(f"INFO: Interaction for known user: {user_profile.username} (Grade: {user_profile.grade_level}, Preferred AITA: {user_profile.preferred_aita_persona_id})")
        # Conceptual: Use preferred_aita_persona_id to select model/adapter
        if user_profile.preferred_aita_persona_id:
            effective_aita_persona_id = user_profile.preferred_aita_persona_id
            print(f"INFO: Using user's preferred AITA persona: {effective_aita_persona_id}")
        if user_profile.grade_level:
            system_prompt_addon = f" The student is in grade {user_profile.grade_level}."
        # For xAPI logging, actor.account.name should use request.user_id (which is the registered user_id)
    else:
        print(f"INFO: Interaction for guest user or user_id '{request.user_id}' not found in DB. Using default persona '{request.aita_persona_id}'.")
        # Proceed with default behavior if profile not found.

    # TODO: Implement MCP client call for richer context.
    system_prompt = f"You are a helpful AI assistant ({effective_aita_persona_id}). Please respond clearly and concisely.{system_prompt_addon}"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(request.conversation_history)
    messages.append({"role": "user", "content": request.user_utterance})

    try:
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=True).to(device)
        input_ids_length = inputs.input_ids.shape[1]

        with torch.no_grad():
            generated_outputs = model.generate(
                inputs.input_ids, max_new_tokens=300, eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id, do_sample=True, temperature=0.7, top_p=0.9
            )

        response_ids = generated_outputs[0][input_ids_length:]
        aita_raw_response = tokenizer.decode(response_ids, skip_special_tokens=True).strip()
        aita_final_response = aita_raw_response # Placeholder for moderation

        # Log interaction (simplified for V1, full xAPI would be more complex here)
        print(f"INFO: Session: {current_session_id}, User: {request.user_id}, Utterance: '{request.user_utterance}', AITA Final: '{aita_final_response}'")

        return InteractionResponse(
            session_id=current_session_id,
            aita_response=aita_final_response,
            debug_info={"model_used": MODEL_ID, "aita_persona_resolved": effective_aita_persona_id, "user_profile_found": bool(user_profile)}
        )
    except Exception as e:
        print(f"ERROR: Exception during model interaction: {e}")
        raise HTTPException(status_code=500, detail=f"Error during model interaction: {str(e)}")

# --- 5. Main block for Uvicorn ---
if __name__ == "__main__":
    print("INFO: Starting AITA Interaction Service with Uvicorn (version with User Profiles)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
