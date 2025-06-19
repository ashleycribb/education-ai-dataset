import torch
from transformers import AutoTokenizer # AutoModelForCausalLM will be via model_loader_utils
from typing import List, Dict, Optional, Any
# from peft import PeftModel # No longer needed directly here
import os
import json
import datetime
import uuid
import time

# --- Import new utility ---
from model_loader_utils import load_model_tokenizer_with_adapter, DummySLM # Import DummySLM

# MCP Imports
from modelcontextprotocol.client.stdio_client import MCPStdIOClient
from modelcontextprotocol.protocol import ResourcePath

# Moderation Service Import
from moderation_service import ModerationService

# 1. Configuration
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
MAX_HISTORY_TURNS = 3
XAPI_LOG_FILE_PATH = "xapi_statements.jsonl"

DEFAULT_STUDENT_ID = "student001"
DEFAULT_SUBJECT = "ReadingComprehension"
DEFAULT_ITEM_ID = "passage_kitten_001"

# Simple Console Logger (defined locally as it's used throughout)
class ConsoleLogger:
    def info(self, message: str): print(f"CLIENT_INFO: {message}")
    def error(self, message: str, exc_info: bool = False): print(f"CLIENT_ERROR: {message}")
    def warning(self, message: str): print(f"CLIENT_WARNING: {message}")

logger = ConsoleLogger()

# --- Dummy SLM for Fallback (REMOVED - Will use from model_loader_utils) ---
# class DummySLM:
#    # ... (previous local definition was here) ...
#    pass

# 2. Load Model and Tokenizer (Commented out - replaced by utility)
# def load_model_and_tokenizer(model_id: str, adapter_path: Optional[str] = None):
#     # ... (previous local implementation) ...
#     pass


# 3. MCP Client Function (remains the same)
def fetch_lms_activity_context(mcp_client: MCPStdIOClient, student_id: str, subject: str, item_id: str) -> Optional[Dict[str, Any]]:
    logger.info(f"Fetching LMS context for student '{student_id}', subject '{subject}', item '{item_id}'...")
    try:
        path = f"/student/{student_id}/activity_context"
        query_params = {"subject": subject, "item_id": item_id}
        resource_path = ResourcePath(path=path, query_params=query_params)
        response = mcp_client.get_resource(resource_path)

        if response and response.status_code == 200 and response.payload:
            logger.info("LMS context fetched successfully.")
            return response.payload
        else:
            error_msg = response.payload.get("error", "Unknown error") if response and response.payload else "No response or empty/invalid payload"
            logger.error(f"Error fetching LMS context: Status {response.status_code if response else 'N/A'}, Message: {error_msg}")
            return None
    except Exception as e:
        logger.error(f"Exception during MCP get_resource: {e}", exc_info=True)
        return None

# 4. Chat Loop (Adjusted for potential DummySLM from utility)
def chat_with_aita(model: Any, tokenizer: AutoTokenizer, device: torch.device, mcp_client: MCPStdIOClient, moderation_service: ModerationService, student_id_override: Optional[str] = None):
    current_student_id = student_id_override if student_id_override else DEFAULT_STUDENT_ID
    current_subject = DEFAULT_SUBJECT
    current_item_id = DEFAULT_ITEM_ID
    lms_context = fetch_lms_activity_context(mcp_client, current_student_id, current_subject, current_item_id)

    student_id_anonymized = lms_context.get("student_id_anonymized", current_student_id) if lms_context else current_student_id
    passage_title_from_context = lms_context.get("current_passage_title", lms_context.get("current_item_title", "the current topic")) if lms_context else "the current topic"
    passage_text_from_context = lms_context.get("current_passage_text_snippet", lms_context.get("current_item_text_snippet", "Please tell me what you'd like to practice!")) if lms_context else "Please tell me what you'd like to practice!"
    primary_lo_list = lms_context.get("target_learning_objectives_for_activity", []) if lms_context else []
    primary_lo = primary_lo_list[0] if primary_lo_list and isinstance(primary_lo_list, list) and len(primary_lo_list) > 0 else {}
    lo_description_from_context = primary_lo.get("description", f"general {current_subject} understanding")
    lo_id_from_context = primary_lo.get("lo_id", f"{current_subject.upper()}.X.General")
    subject_from_context = lms_context.get("subject", current_subject) if lms_context else current_subject
    item_id_for_context = lms_context.get("current_passage_id", lms_context.get("current_item_id", "unknown_item")) if lms_context else "unknown_item"
    teacher_notes = lms_context.get("teacher_notes_for_student_on_lo", "") if lms_context else ""
    AITA_PERSONA_NAME = "Explorer AITA"
    if "ReadingComprehension" in subject_from_context: AITA_PERSONA_NAME = "Reading Explorer AITA"
    elif "Ecology" in subject_from_context or "Science" in subject_from_context: AITA_PERSONA_NAME = "Eco Explorer AITA"

    system_prompt = (
        f"You are {AITA_PERSONA_NAME}, a friendly and helpful AI tutor for {lms_context.get('grade_level','middle school')} {subject_from_context}. "
        f"You are currently helping a student with '{passage_title_from_context}'. The learning objective is: '{lo_description_from_context}'. "
        f"The relevant text snippet is: \"{passage_text_from_context}\" {f'Your teacher left a note: \"{teacher_notes}\" ' if teacher_notes else ''}"
        "Guide students with questions; don't give answers directly. Keep responses concise and age-appropriate."
    )
    initial_aita_message = f"Hi! I'm {AITA_PERSONA_NAME}. I see you're working on '{passage_title_from_context}'. The learning goal is: '{lo_description_from_context}'. {teacher_notes if teacher_notes else ''} What are your first thoughts or questions?"
    if not lms_context:
        initial_aita_message = f"Hi! I'm {AITA_PERSONA_NAME}. What would you like to work on today?"
        system_prompt = (f"You are {AITA_PERSONA_NAME}, a friendly and helpful AI tutor. Guide students with questions. Keep responses concise and age-appropriate.")

    conversation_history: List[Dict[str, str]] = []
    session_id = uuid.uuid4().hex
    turn_counter = 0
    print(f"\n--- {AITA_PERSONA_NAME} ---")
    logger.info(f"Session ID: {session_id}")
    print(f"AITA: {initial_aita_message}")

    while True:
        turn_counter += 1
        current_timestamp_utc = datetime.datetime.utcnow().isoformat() + "Z"
        xapi_statement = {
            "id": str(uuid.uuid4()), "actor": {"objectType": "Agent", "name": "cli_user", "account": {"homePage": "http://example.com/cli", "name": student_id_anonymized}},
            "verb": {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted_with_AITA_turn"}},
            "object": {"objectType": "Activity", "id": f"http://example.com/aita_pilot/session/{session_id}/turn/{turn_counter}",
                       "definition": {"name": {"en-US": "AITA Interaction Turn"}, "description": {"en-US": f"Interaction with {AITA_PERSONA_NAME} about '{passage_title_from_context}' on LO: {lo_id_from_context}"},
                                      "type": "http://adlnet.gov/expapi/activities/interaction", "extensions": {}}},
            "result": {"response": "", "duration": "", "extensions": {}},
            "context": {"contextActivities": {"parent": [{"id": f"http://example.com/aita_pilot/content_item/{item_id_for_context}"}]},
                        "extensions": {"http://example.com/xapi/extensions/session_id": session_id, "http://example.com/xapi/extensions/aita_persona": AITA_PERSONA_NAME,
                                       "http://example.com/xapi/extensions/learning_objective_active": lo_id_from_context, "http://example.com/xapi/extensions/full_prompt_to_llm": "" }},
            "timestamp": current_timestamp_utc, "authority": {"objectType": "Agent", "name": "AITA_System_Logger_v2.3_Mod", "account": {"homePage": "http://example.com/aita_system", "name": "System"}}
        }

        try:
            user_input_raw = input("User: ").strip()
            if "extensions" not in xapi_statement["object"]["definition"]:
                xapi_statement["object"]["definition"]["extensions"] = {}
            xapi_statement["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/user_utterance_raw"] = user_input_raw
        except EOFError: logger.info("Exiting chat due to EOF."); break
        except KeyboardInterrupt: logger.info("Exiting chat due to interrupt."); break

        if user_input_raw.lower() in ["quit", "exit", "q"]:
            logger.info("Exiting chat. Goodbye!")
            xapi_statement["verb"] = {"id": "http://adlnet.gov/expapi/verbs/exited", "display": {"en-US": "exited_AITA_session"}}
            with open(XAPI_LOG_FILE_PATH, 'a') as f: json.dump(xapi_statement, f); f.write('\n')
            break
        if not user_input_raw: continue

        mod_input_results = moderation_service.check_text(user_input_raw)
        if "extensions" not in xapi_statement["result"]: xapi_statement["result"]["extensions"] = {}
        xapi_statement["result"]["extensions"]["http://example.com/xapi/extensions/input_moderation_details"] = mod_input_results
        if not mod_input_results["is_safe"]:
            polite_refusal = "AITA: I'm sorry, I can't process that request. Let's stick to our learning task or try phrasing it differently."
            print(polite_refusal)
            xapi_statement["result"]["response"] = polite_refusal
            with open(XAPI_LOG_FILE_PATH, 'a') as f: json.dump(xapi_statement, f); f.write('\n')
            continue

        messages_for_template = [{"role": "system", "content": system_prompt}]
        messages_for_template.extend(conversation_history)
        messages_for_template.append({"role": "user", "content": user_input_raw})

        try:
            prompt_text = tokenizer.apply_chat_template(messages_for_template, tokenize=False, add_generation_prompt=True)
            if "extensions" not in xapi_statement["context"]: xapi_statement["context"]["extensions"] = {}
            xapi_statement["context"]["extensions"]["http://example.com/xapi/extensions/full_prompt_to_llm"] = prompt_text

            inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=True).to(device)
            input_ids_length = inputs.input_ids.shape[1]

            logger.info("AITA is thinking...")
            generation_start_time = time.time()

            with torch.no_grad():
                generated_outputs = model.generate(
                    inputs.input_ids, max_new_tokens=300,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    temperature=0.7, top_p=0.9, do_sample=True
                )

            generation_duration_s = time.time() - generation_start_time
            xapi_statement["result"]["duration"] = f"PT{generation_duration_s:.2f}S"

            response_ids = generated_outputs[0][input_ids_length:]
            raw_response_text = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

            if "extensions" not in xapi_statement["object"]["definition"]: xapi_statement["object"]["definition"]["extensions"] = {}
            xapi_statement["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/aita_response_raw"] = raw_response_text
            xapi_statement["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/pedagogical_notes"] = ["Placeholder: Note 1 for this AITA turn.", "Placeholder: Note 2 indicating strategy."]
            xapi_statement["object"]["definition"]["extensions"]["http://example.com/xapi/extensions/aita_turn_narrative_rationale"] = "Placeholder: This is a simulated narrative rationale for the AITA's current turn."

            mod_output_results = moderation_service.check_text(raw_response_text)
            if "extensions" not in xapi_statement["result"]: xapi_statement["result"]["extensions"] = {}
            xapi_statement["result"]["extensions"]["http://example.com/xapi/extensions/output_moderation_details"] = mod_output_results
            final_response_text = raw_response_text
            if not mod_output_results["is_safe"]:
                generic_safe_response = "AITA: I was about to say something that might not be quite right for our lesson. Let's try a different way! How about you tell me what you found most interesting in the text?"
                final_response_text = generic_safe_response

            xapi_statement["result"]["response"] = final_response_text
            print(f"AITA: {final_response_text}")

            conversation_history.append({"role": "user", "content": user_input_raw})
            conversation_history.append({"role": "assistant", "content": final_response_text})
            if len(conversation_history) > MAX_HISTORY_TURNS * 2:
                conversation_history = conversation_history[-(MAX_HISTORY_TURNS * 2):]

        except Exception as e:
            error_message = f"CLIENT: Error during model interaction: {e}"
            logger.error(error_message, exc_info=True)
            xapi_statement["result"]["response"] = f"AITA_ERROR_INTERNAL: {error_message}"
            if "extensions" not in xapi_statement["result"]: xapi_statement["result"]["extensions"] = {}
            xapi_statement["result"]["extensions"]["http://example.com/xapi/extensions/error_occurred"] = str(e)

        finally:
            with open(XAPI_LOG_FILE_PATH, 'a') as f:
                json.dump(xapi_statement, f)
                f.write('\n')

# 5. Main Block
if __name__ == "__main__":
    ADAPTER_CHECKPOINT_PATH: Optional[str] = None
    student_id_for_session = os.environ.get("AITA_STUDENT_ID", DEFAULT_STUDENT_ID)

    try:
        logger.info("Initializing Moderation Service...")
        moderation_service = ModerationService(logger=logger)
        logger.info("Moderation Service initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize ModerationService: {e}. Safeguards will be non-functional.", exc_info=True)
        class _DummyModerationService:
            def check_text(self, text: str) -> Dict[str, Any]:
                return {"is_safe": True, "flagged_categories": [], "scores": {}, "model_used": "dummy_moderation_service_due_to_error", "status": "service_init_failed"}
        moderation_service = _DummyModerationService()
        logger.warning("Using _DummyModerationService. Content will not be actively moderated.")

    mcp_client = MCPStdIOClient()
    try:
        logger.info("Starting MCP Client...")
        mcp_client.start()
        logger.info("MCP Client started.")

        # Call the utility function for loading model and tokenizer
        model, tokenizer, device = load_model_tokenizer_with_adapter(
            MODEL_ID,
            adapter_path=ADAPTER_CHECKPOINT_PATH,
            logger=logger
        )

        # Refined DummySLM fallback logic
        if model is None or tokenizer is None:
            logger.warning(f"Failed to load real SLM model/tokenizer for '{MODEL_ID}' via utility. Falling back to DummySLM.")

            if tokenizer is None: # Attempt to load tokenizer again only if it's None
                logger.info(f"Attempting to re-load tokenizer for DummySLM: {MODEL_ID}")
                try:
                    # Directly use AutoTokenizer from transformers, it's already imported
                    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
                    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
                    logger.info("Tokenizer re-loaded for DummySLM.")
                except Exception as e_tok_dummy:
                    logger.error(f"CRITICAL: Failed to load tokenizer even for DummySLM: {e_tok_dummy}. Cannot proceed.", exc_info=True)
                    tokenizer = None

            if device is None: # Determine device for DummySLM if not already set
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                logger.info(f"Device for DummySLM set to: {device}")

            if tokenizer and device:
                 model = DummySLM(device=device, tokenizer=tokenizer, logger=logger) # Pass logger
                 logger.info("DummySLM has been instantiated.")
            else:
                 logger.error("CRITICAL: Tokenizer and/or device unavailable, cannot instantiate DummySLM. Exiting.")
                 critical_error_log = {"id": str(uuid.uuid4()), "error_message": "Tokenizer/device unavailable for DummySLM."}
                 with open(XAPI_LOG_FILE_PATH, 'a') as f: json.dump(critical_error_log, f); f.write('\n')
                 model = None

        if model and tokenizer and device:
            chat_with_aita(model, tokenizer, device, mcp_client, moderation_service, student_id_override=student_id_for_session)
        else:
            logger.error("Failed to initialize model and tokenizer even with DummySLM fallback. Exiting CLI.")
            critical_error_log = {
                "id": str(uuid.uuid4()), "actor": {"name": "System"},
                "verb": {"id": "http://adlnet.gov/expapi/verbs/failed", "display": {"en-US": "failed_system_initialization"}},
                "object": {"id": "http://example.com/aita_cli", "definition": {"name": {"en-US": "AITA CLI System"}}},
                "result": {"extensions":{"http://example.com/xapi/extensions/error_message": "Model or tokenizer failed to load, including fallback."}},
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z", "stage": "initialization_cli"
            }
            with open(XAPI_LOG_FILE_PATH, 'a') as f: json.dump(critical_error_log, f); f.write('\n')

    except Exception as e:
        logger.error(f"Critical error in main execution: {e}", exc_info=True)
    finally:
        logger.info("Stopping MCP Client...")
        mcp_client.stop()
        logger.info("MCP Client stopped. CLI session ended.")

[end of aita_mcp_client.py]
