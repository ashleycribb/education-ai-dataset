# model_loader_utils.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Optional, Tuple, Any
import os

class DefaultLogger:
    def info(self, message: str): print(f"INFO: {message}")
    def error(self, message: str, exc_info: bool = False):
        print(f"ERROR: {message}")
        if exc_info: pass # In a real logger, you might use traceback.format_exc()
    def warning(self, message: str): print(f"WARNING: {message}")

class DummySLM:
    def __init__(self, device: torch.device, tokenizer: Optional[AutoTokenizer], logger: Optional[Any] = None):
        self.device = device
        self.tokenizer = tokenizer # Store tokenizer for encoding dummy response
        self.name_or_path = "DummySLM_Fallback" # Mimic real model attribute

        if logger is None:
            self.logger = DefaultLogger()
        else:
            self.logger = logger
        self.logger.info(f"Instantiated DummySLM. Device: {self.device}. Tokenizer: {'Available' if self.tokenizer else 'Not Available'}")

    def generate(self, input_ids: torch.Tensor, max_new_tokens: int, eos_token_id: int, pad_token_id: int, **kwargs) -> torch.Tensor:
        dummy_response_text = "This is a dummy response from DummySLM. The primary model may have failed to load or encountered an issue."

        if self.tokenizer:
            # Ensure input_ids is on the same device as the tokenizer outputs will be
            # This might not be strictly necessary if input_ids is already on self.device,
            # but it's safer.
            input_ids = input_ids.to(self.device)

            dummy_response_ids = self.tokenizer.encode(dummy_response_text, add_special_tokens=False, return_tensors="pt").to(self.device)

            # Ensure max_new_tokens is respected (approximately).
            if dummy_response_ids.shape[1] > max_new_tokens:
                dummy_response_ids = dummy_response_ids[:, :max_new_tokens]

            # Add EOS token at the end of the dummy response
            eos_tensor = torch.tensor([[eos_token_id]], dtype=torch.long, device=self.device)

            # Handle case where dummy_response_ids might be empty if max_new_tokens is too small or text is empty
            if dummy_response_ids.shape[1] == 0:
                 dummy_response_ids_with_eos = eos_tensor
            else:
                 dummy_response_ids_with_eos = torch.cat([dummy_response_ids, eos_tensor], dim=1)

            # Concatenate with the original input_ids
            # The model.generate() function normally returns the prompt + generated tokens.
            full_sequence = torch.cat([input_ids, dummy_response_ids_with_eos], dim=1)
            return full_sequence
        else:
            self.logger.error("DummySLM: Tokenizer not available for encoding dummy response.")
            # Fallback: return input_ids concatenated with an EOS token to avoid downstream errors
            # expecting a longer sequence, and ensure it's on the correct device.
            eos_fill_tensor = torch.full((input_ids.shape[0], 1), eos_token_id, dtype=torch.long, device=input_ids.device)
            return torch.cat([input_ids, eos_fill_tensor], dim=1)


    def to(self, device: torch.device):
        self.logger.info(f"DummySLM: Moving to device {device} (no-op for most internal tensors, device property updated).")
        self.device = device
        return self

    def eval(self):
        self.logger.info("DummySLM set to eval mode (no-op).")
        pass

def load_model_tokenizer_with_adapter(
    model_id: str,
    adapter_path: Optional[str] = None,
    logger: Optional[Any] = None,
    trust_remote_code_flag: bool = True,
    torch_dtype_str: str = "auto"
) -> Tuple[Optional[Any], Optional[AutoTokenizer], Optional[torch.device]]:
    if logger is None:
        logger = DefaultLogger()
    logger.info(f"Attempting to load model and tokenizer for '{model_id}'...")
    loaded_tokenizer: Optional[AutoTokenizer] = None
    loaded_model: Optional[Any] = None
    current_device: Optional[torch.device] = None
    try:
        current_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {current_device}")
        logger.info(f"Loading tokenizer for '{model_id}'...")
        loaded_tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=trust_remote_code_flag)
        if loaded_tokenizer.pad_token is None:
            loaded_tokenizer.pad_token = loaded_tokenizer.eos_token
            logger.info(f"Set tokenizer.pad_token to tokenizer.eos_token: {loaded_tokenizer.eos_token}")
        logger.info(f"Loading base model '{model_id}' with dtype '{torch_dtype_str}'...")
        dtype_map = {"auto": "auto", "bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
        resolved_torch_dtype = dtype_map.get(torch_dtype_str.lower(), "auto")
        loaded_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=resolved_torch_dtype,
            trust_remote_code=trust_remote_code_flag
        )
        loaded_model.to(current_device)
        logger.info(f"Base model '{model_id}' loaded successfully on {current_device}.")
        if adapter_path:
            expected_config_file = os.path.join(adapter_path, "adapter_config.json")
            has_model_file = any(os.path.exists(os.path.join(adapter_path, fName)) for fName in ["adapter_model.bin", "adapter_model.safetensors"])

            if os.path.isdir(adapter_path) and os.path.exists(expected_config_file) and has_model_file:
                logger.info(f"Loading PEFT adapter from directory: '{adapter_path}'...")
                try:
                    loaded_model = PeftModel.from_pretrained(loaded_model, adapter_path)
                    logger.info(f"PEFT adapter loaded successfully from {adapter_path}.")
                except Exception as e_adapter:
                    logger.error(f"Error loading PEFT adapter from {adapter_path}: {str(e_adapter)}. Using base model only.", exc_info=True)
            else:
                logger.warning(f"Adapter path '{adapter_path}' not found, not a directory, or doesn't appear to be a valid PEFT adapter directory (missing config or model files). Using base model only.")
        else:
            logger.info("No adapter path provided. Using base model only.")
        loaded_model.eval()
        logger.info(f"Model setup complete for '{model_id}' (with adapter: {adapter_path if adapter_path else 'None'}). Model is in eval mode.")
        return loaded_model, loaded_tokenizer, current_device
    except Exception as e:
        logger.error(f"Critical error during model/tokenizer loading for '{model_id}': {str(e)}", exc_info=True)
        # Return tokenizer if it loaded, even if model failed, so DummySLM can use it
        return None, loaded_tokenizer, current_device


if __name__ == '__main__':
    logger_test = DefaultLogger()
    logger_test.info("--- Testing model_loader_utils.py ---")

    model_to_test = "gpt2"
    logger_test.info(f"Test 1: Loading a base model ({model_to_test})...")
    model1, tokenizer1, device1 = load_model_tokenizer_with_adapter(model_id=model_to_test, logger=logger_test)
    if model1 and tokenizer1:
        logger_test.info(f"{model_to_test} loaded successfully on {device1}.")
        try:
            inputs = tokenizer1("Hello, world!", return_tensors="pt").to(device1)
            # For gpt2, eos_token_id and pad_token_id are usually the same.
            # Ensure they are available for the dummy generate call.
            eos_id = tokenizer1.eos_token_id if tokenizer1.eos_token_id is not None else 50256
            pad_id = tokenizer1.pad_token_id if tokenizer1.pad_token_id is not None else eos_id
            outputs = model1.generate(**inputs, max_new_tokens=5, eos_token_id=eos_id, pad_token_id=pad_id)
            logger_test.info(f"Sample generation output: {tokenizer1.decode(outputs[0])}")
        except Exception as e_gen:
            logger_test.error(f"Error during sample generation with {model_to_test}: {e_gen}", exc_info=True)
    else:
        logger_test.error(f"Failed to load {model_to_test}.")

    logger_test.info(f"Test 2: Loading {model_to_test} with a non-existent adapter path...")
    non_existent_adapter_path = "./non_existent_adapter_dir_for_testing"
    if os.path.exists(non_existent_adapter_path):
        logger_test.warning(f"Test adapter path {non_existent_adapter_path} unexpectedly exists. Test might not be accurate.")

    model2, tokenizer2, device2 = load_model_tokenizer_with_adapter(
        model_id=model_to_test,
        adapter_path=non_existent_adapter_path,
        logger=logger_test
    )
    if model2 and tokenizer2:
        logger_test.info(f"{model_to_test} loaded (non-existent adapter test). Model type: {type(model2)}")
        if not isinstance(model2, PeftModel):
            logger_test.info("Correctly using base model as adapter was not found.")
        else:
            logger_test.error("Incorrectly loaded a PeftModel when adapter path was non-existent.")
    else:
        logger_test.error(f"Failed to load {model_to_test} for non-existent adapter test.")

    logger_test.info("Test 3: Conceptual test for loading with a VALID adapter path.")
    dummy_adapter_path = "./dummy_gpt2_adapter_for_testing"
    if os.path.exists(dummy_adapter_path) and os.path.isdir(dummy_adapter_path) and os.path.exists(os.path.join(dummy_adapter_path, "adapter_config.json")):
        logger_test.info(f"Attempting to load {model_to_test} with dummy adapter from {dummy_adapter_path}...")
        model3, tokenizer3, device3 = load_model_tokenizer_with_adapter(
            model_id=model_to_test,
            adapter_path=dummy_adapter_path,
            logger=logger_test
        )
        if model3 and tokenizer3:
             logger_test.info(f"{model_to_test} with adapter loaded. Model type: {type(model3)}")
             if isinstance(model3, PeftModel):
                 logger_test.info("Successfully loaded model as PeftModel.")
             else:
                 logger_test.warning("Loaded model but it is NOT a PeftModel, check adapter loading logic if adapter was expected.")
        else:
            logger_test.error(f"Failed to load {model_to_test} with adapter from {dummy_adapter_path}")
    else:
        logger_test.warning(f"Skipping Test 3: Dummy adapter directory '{dummy_adapter_path}' not found or is not a valid adapter dir.")

    logger_test.info("Test 4: Testing DummySLM instantiation and generation (simulating model load failure)")
    # Simulate tokenizer loaded but model failed
    temp_tokenizer, _, temp_device = load_model_tokenizer_with_adapter(model_id="gpt2", logger=logger_test)
    if temp_tokenizer and temp_device:
        logger_test.info("Simulating model load failure after successful tokenizer load...")
        dummy_model = DummySLM(device=temp_device, tokenizer=temp_tokenizer, logger=logger_test)
        logger_test.info("DummySLM instantiated.")
        try:
            test_input_text = "Test input for dummy."
            # Ensure pad_token_id is set for generate
            if temp_tokenizer.pad_token_id is None: temp_tokenizer.pad_token_id = temp_tokenizer.eos_token_id

            inputs_for_dummy = temp_tokenizer(test_input_text, return_tensors="pt").to(temp_device)
            dummy_outputs = dummy_model.generate(
                inputs_for_dummy.input_ids,
                max_new_tokens=10,
                eos_token_id=temp_tokenizer.eos_token_id if temp_tokenizer.eos_token_id is not None else 50256,
                pad_token_id=temp_tokenizer.pad_token_id if temp_tokenizer.pad_token_id is not None else 50256
            )
            decoded_dummy_output = temp_tokenizer.decode(dummy_outputs[0]) # Decode the whole sequence
            logger_test.info(f"DummySLM generated output tensor shape: {dummy_outputs.shape}")
            logger_test.info(f"DummySLM decoded output: {decoded_dummy_output}")
            if "dummy response from DummySLM" in decoded_dummy_output:
                logger_test.info("DummySLM generation test PASSED.")
            else:
                logger_test.error("DummySLM generation test FAILED: Output does not contain expected dummy text.")
        except Exception as e_dummy_gen:
            logger_test.error(f"Error during DummySLM generation test: {e_dummy_gen}", exc_info=True)
    else:
        logger_test.warning("Skipping DummySLM test as base tokenizer failed to load.")


    logger_test.info("--- Finished testing model_loader_utils.py ---")
