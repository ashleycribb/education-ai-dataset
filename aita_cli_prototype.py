import torch
# Removed: from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Optional, Any # Added Any
# Removed: from peft import PeftModel
import os
import json
import datetime
import uuid
import time

# --- Import new utility ---
from model_loader_utils import load_model_tokenizer_with_adapter, DefaultLogger

# MCP Imports (Not used in this CLI prototype directly, but kept if other logic depends on it)
# from modelcontextprotocol.client.stdio_client import MCPStdIOClient
# from modelcontextprotocol.protocol import ResourcePath

# Moderation Service Import (Not used in this CLI prototype directly)
# from moderation_service import ModerationService

# 1. Configuration
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
MAX_HISTORY_TURNS = 3
LOG_FILE_PATH = "aita_interactions.jsonl" # Renamed from XAPI_LOG_FILE_PATH for consistency with original script

# Safeguard keywords
BLOCKED_INPUT_KEYWORDS = ["bad_word1", "inappropriate_topic_a", "tell me a secret"]
BLOCKED_OUTPUT_KEYWORDS = ["undesirable_wordx", "problem_phrase_y", "i cannot help you"]

# Default student and activity (Not used in this CLI prototype directly without MCP integration)
# DEFAULT_STUDENT_ID = "student001"
# DEFAULT_SUBJECT = "ReadingComprehension"
# DEFAULT_ITEM_ID = "passage_kitten_001"

# --- Initialize a global logger instance (or pass it around) ---
# The original script had a class ConsoleLogger defined and instantiated as logger.
# We will use DefaultLogger from the utility.
logger = DefaultLogger()


# 2. Load Model and Tokenizer (Commented out - replaced by utility)
# def load_model_and_tokenizer(model_id: str, adapter_path: Optional[str] = None):
#     """Loads the specified model and tokenizer, optionally applying a PEFT adapter."""
#     print(f"Loading base model and tokenizer for '{model_id}'...")
#     try:
#         # Determine device
#         device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         print(f"Using device: {device}")

#         # Load tokenizer
#         tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
#         if tokenizer.pad_token is None:
#             tokenizer.pad_token = tokenizer.eos_token
#             print(f"Set tokenizer.pad_token to tokenizer.eos_token: {tokenizer.eos_token}")

#         # Load model
#         model = AutoModelForCausalLM.from_pretrained(
#             model_id,
#             torch_dtype="auto",
#             trust_remote_code=True
#         )
#         model.to(device)

#         if adapter_path and os.path.exists(adapter_path):
#             print(f"Loading PEFT adapter from '{adapter_path}'...")
#             try:
#                 model = PeftModel.from_pretrained(model, adapter_path)
#                 print(f"PEFT adapter loaded successfully from {adapter_path}.")
#             except Exception as e:
#                 print(f"Error loading PEFT adapter: {e}. Using base model only.")
#         else:
#             if adapter_path:
#                 print(f"Adapter path '{adapter_path}' not found. Using base model only.")
#             else:
#                 print("No adapter path provided. Using base model only.")

#         model.eval()

#         print(f"Model (base: '{model_id}') ready on {device}.")
#         return model, tokenizer, device
#     except Exception as e:
#         print(f"Error loading model or tokenizer: {e}")
#         return None, None, None

# 3. Chat Loop
# The 'device' parameter is now determined by load_model_tokenizer_with_adapter
# The 'tokenizer' and 'model' are also returned by it.
def chat_with_aita(model: Any, tokenizer: Any, device: torch.device): # Updated type hints for model/tokenizer from Any
    """Handles the command-line chat loop with the AITA model."""

    # Simplified system prompt as MCP context fetching is not part of this script's core logic anymore
    system_prompt = (
        "You are Reading Explorer AITA, a friendly and helpful AI tutor for 4th-grade reading comprehension. "
        "Help students understand how to find the main idea and make inferences, but don't give away answers directly. "
        "Guide them with questions. Keep your responses concise and suitable for a 4th grader."
    )

    conversation_history: List[Dict[str, str]] = []
    session_id = uuid.uuid4().hex # session_id is still useful for logging
    turn_counter = 0
    aita_persona_name = "Reading Explorer AITA" # Kept for logging consistency

    logger.info(f"--- {aita_persona_name} ---") # Changed print to logger.info
    logger.info(f"Session ID: {session_id}")
    logger.info("Type 'quit', 'exit', or 'q' to end the session.") # Changed print to logger.info
    logger.info(f"System Prompt (for this session): {system_prompt}\n") # Changed print to logger.info


    while True:
        turn_counter += 1
        interaction_id = f"{session_id}_turn_{turn_counter}"
        timestamp_utc = datetime.datetime.utcnow().isoformat() + "Z"
        user_id_placeholder = "cli_user_001" # This CLI doesn't have formal user registration
        active_lo_placeholder = "RC.4.GeneralCLI" # Placeholder LO for CLI interactions

        # Simplified log_entry as MCP context is not directly fetched here
        log_entry: Dict[str, Any] = {
            "interaction_id": interaction_id, "session_id": session_id, "timestamp_utc": timestamp_utc,
            "user_id": user_id_placeholder, "aita_persona": aita_persona_name,
            "learning_objective_id_active": active_lo_placeholder,
            "user_utterance_raw": "", "input_safeguard_triggered": False, "input_blocked_keywords_found": [],
            "aita_prompt_sent_to_llm": "", "aita_response_raw": "", "output_safeguard_triggered": False,
            "output_blocked_keywords_found": [], "aita_response_final_to_user": "",
            "xapi_verb_id": "http://example.com/xapi/cli/interacted_with_aita",
            "xapi_object_id": f"http://example.com/aita_cli_interaction/{interaction_id}",
            "xapi_object_definition_name": "AITA CLI Turn",
            "generation_duration_ms": 0.0
        }

        try:
            user_input_raw = input("User: ").strip()
            log_entry["user_utterance_raw"] = user_input_raw
        except EOFError:
            logger.info("\nExiting chat due to EOF.")
            break
        except KeyboardInterrupt:
            logger.info("\nExiting chat due to interrupt.")
            break

        if user_input_raw.lower() in ["quit", "exit", "q"]:
            logger.info("Exiting chat. Goodbye!")
            # Log exit event if needed
            break

        if not user_input_raw:
            continue

        # Input Safeguard Check
        found_input_blocked_keywords = [kw for kw in BLOCKED_INPUT_KEYWORDS if kw.lower() in user_input_raw.lower()]
        if found_input_blocked_keywords:
            polite_refusal = "AITA: I'm sorry, I can't discuss that. Let's focus on our reading task!"
            print(polite_refusal) # Keep print for user feedback
            log_entry["input_safeguard_triggered"] = True
            log_entry["input_blocked_keywords_found"] = found_input_blocked_keywords
            log_entry["aita_response_final_to_user"] = polite_refusal
            # Simplified logging - full xAPI structure might be overkill if not using k12_mcp_client_sdk.xapi_utils
            with open(LOG_FILE_PATH, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
            continue

        messages_for_template = [{"role": "system", "content": system_prompt}]
        messages_for_template.extend(conversation_history)
        messages_for_template.append({"role": "user", "content": user_input_raw})

        try:
            prompt_text = tokenizer.apply_chat_template(
                messages_for_template, tokenize=False, add_generation_prompt=True
            )
            log_entry["aita_prompt_sent_to_llm"] = prompt_text

            inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=True).to(device)
            input_ids_length = inputs.input_ids.shape[1]

            logger.info("AITA is thinking...")
            generation_start_time = time.time()
            with torch.no_grad():
                generated_outputs = model.generate( # model is now from the utility
                    inputs.input_ids,
                    max_new_tokens=300,
                    temperature=0.7, top_p=0.9, do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            generation_duration_ms = (time.time() - generation_start_time) * 1000
            log_entry["generation_duration_ms"] = round(generation_duration_ms, 2)

            response_ids = generated_outputs[0][input_ids_length:]
            raw_response_text = tokenizer.decode(response_ids, skip_special_tokens=True).strip()
            log_entry["aita_response_raw"] = raw_response_text

            final_response_text = raw_response_text
            found_output_blocked_keywords = [kw for kw in BLOCKED_OUTPUT_KEYWORDS if kw.lower() in raw_response_text.lower()]
            if found_output_blocked_keywords:
                generic_safe_response = "AITA: I seem to be having trouble formulating a helpful response for that. Could you try asking in a different way?"
                final_response_text = generic_safe_response
                log_entry["output_safeguard_triggered"] = True
                log_entry["output_blocked_keywords_found"] = found_output_blocked_keywords

            log_entry["aita_response_final_to_user"] = final_response_text
            print(f"AITA: {final_response_text}")

            conversation_history.append({"role": "user", "content": user_input_raw})
            conversation_history.append({"role": "assistant", "content": final_response_text})

            if len(conversation_history) > MAX_HISTORY_TURNS * 2:
                conversation_history = conversation_history[-(MAX_HISTORY_TURNS * 2):]

        except Exception as e:
            error_message = f"Error during model interaction: {e}"
            logger.error(error_message, exc_info=True) # Use logger
            log_entry["aita_response_final_to_user"] = f"AITA_ERROR: {error_message}"

        finally:
            with open(LOG_FILE_PATH, 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')

# 4. Main Block
if __name__ == "__main__":
    ADAPTER_CHECKPOINT_PATH: Optional[str] = None
    # ADAPTER_CHECKPOINT_PATH = "./non_existent_path_for_testing_fallback"

    # Instantiate DefaultLogger from the utility
    cli_logger = DefaultLogger()

    # Call the utility function for loading model and tokenizer
    model, tokenizer, device = load_model_tokenizer_with_adapter(
        MODEL_ID,
        adapter_path=ADAPTER_CHECKPOINT_PATH,
        logger=cli_logger
    )

    if model and tokenizer and device:
        # ModerationService and MCPClient are not part of this simplified CLI's core logic anymore
        # If they were needed, they would be initialized here.
        # For this version, chat_with_aita only needs model, tokenizer, device.
        try:
            chat_with_aita(model, tokenizer, device)
        except Exception as e:
            cli_logger.error(f"An unexpected error occurred during chat: {e}", exc_info=True)
            # Simplified critical error logging for CLI
            critical_error_log = {
                "interaction_id": f"{uuid.uuid4().hex}_critical_error",
                "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
                "error_message": str(e), "stage": "chat_initialization_cli"
            }
            with open(LOG_FILE_PATH, 'a') as f:
                json.dump(critical_error_log, f)
                f.write('\n')
    else:
        cli_logger.error("Failed to load model and/or tokenizer. Exiting CLI.")
        critical_error_log = {
            "interaction_id": f"{uuid.uuid4().hex}_critical_error",
            "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
            "error_message": "Model or tokenizer failed to load via utility.", "stage": "model_loading_cli"
        }
        with open(LOG_FILE_PATH, 'a') as f:
            json.dump(critical_error_log, f)
            f.write('\n')

    logger.info("CLI session ended.") # Use logger
