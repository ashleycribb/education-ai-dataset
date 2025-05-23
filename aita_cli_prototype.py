import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Optional

# 1. Configuration
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
MAX_HISTORY_TURNS = 3 # Number of past user/assistant turn pairs to keep

# 2. Load Model and Tokenizer
def load_model_and_tokenizer(model_id: str):
    """Loads the specified model and tokenizer."""
    print(f"Loading model and tokenizer for '{model_id}'...")
    try:
        # Determine device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {device}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            print(f"Set tokenizer.pad_token to tokenizer.eos_token: {tokenizer.eos_token}")

        # Load model
        # For Phi-3, torch_dtype="auto" is often recommended.
        # If issues with "auto", can try torch.bfloat16 if supported, or torch.float16
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto", # Automatically selects appropriate dtype (e.g. bfloat16 on Ampere)
            trust_remote_code=True
        )
        model.to(device) # Move model to the determined device
        model.eval() # Set model to evaluation mode

        print(f"Model '{model_id}' loaded successfully on {device}.")
        return model, tokenizer, device
    except Exception as e:
        print(f"Error loading model or tokenizer: {e}")
        return None, None, None

# 3. Chat Loop
def chat_with_aita(model, tokenizer, device):
    """Handles the command-line chat loop with the AITA model."""
    
    system_prompt = (
        "You are Reading Explorer AITA, a friendly and helpful AI tutor for 4th-grade reading comprehension. "
        "Help students understand how to find the main idea and make inferences, but don't give away answers directly. "
        "Guide them with questions. Keep your responses concise and suitable for a 4th grader."
    )
    
    # Stores tuples of (user_input, assistant_response)
    # More accurately, stores message dicts: {"role": "user", "content": ...}, {"role": "assistant", "content": ...}
    conversation_history: List[Dict[str, str]] = []

    print("\n--- Reading Explorer AITA ---")
    print("Type 'quit', 'exit', or 'q' to end the session.")
    print(f"System: {system_prompt}\n")

    while True:
        try:
            user_input = input("User: ").strip()
        except EOFError:
            print("\nExiting chat due to EOF.")
            break
        except KeyboardInterrupt:
            print("\nExiting chat due to interrupt.")
            break


        if user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting chat. Goodbye!")
            break

        if not user_input:
            continue

        # Construct messages for the template
        messages_for_template = [{"role": "system", "content": system_prompt}]
        messages_for_template.extend(conversation_history)
        messages_for_template.append({"role": "user", "content": user_input})
        
        try:
            # Format the prompt using the tokenizer's chat template
            # add_generation_prompt=True is important to ensure the prompt ends with the assistant's turn marker
            prompt_text = tokenizer.apply_chat_template(
                messages_for_template,
                tokenize=False,
                add_generation_prompt=True 
            )

            # Tokenize the input
            # For Phi-3, the prompt already includes special tokens like <|end|> via apply_chat_template.
            # So, add_special_tokens=False might be appropriate for encode if the template handles everything.
            # However, Hugging Face examples often use default (add_special_tokens=True) or don't specify,
            # relying on the tokenizer's default behavior which is usually fine.
            inputs = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=True).to(device)
            input_ids_length = inputs.input_ids.shape[1]


            # Generate response
            # The Phi-3 model card specifies <|end|> as the stop token, which is tokenizer.eos_token
            # The model card also mentions <|file_separator|> but that seems less relevant for typical chat.
            # Using tokenizer.eos_token_id should be correct for Phi-3 as it represents <|end|>.
            print("AITA is thinking...")
            with torch.no_grad(): # Important for inference
                generated_outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=300,  # Adjusted for typical chat response length
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id, # Important if pad_token is set
                    eos_token_id=tokenizer.eos_token_id # Ensures generation stops at <|end|>
                )
            
            # Decode only the newly generated tokens
            response_ids = generated_outputs[0][input_ids_length:]
            response_text = tokenizer.decode(response_ids, skip_special_tokens=True).strip()

            print(f"AITA: {response_text}")

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response_text})

            # Keep history to a manageable size (last MAX_HISTORY_TURNS pairs)
            if len(conversation_history) > MAX_HISTORY_TURNS * 2:
                # Keep the last MAX_HISTORY_TURNS*2 items (which is MAX_HISTORY_TURNS pairs)
                conversation_history = conversation_history[-(MAX_HISTORY_TURNS * 2):]
        
        except Exception as e:
            print(f"Error during model interaction: {e}")
            # Optionally, break or allow user to try again
            # break 

# 4. Main Block
if __name__ == "__main__":
    model, tokenizer, device = load_model_and_tokenizer(MODEL_ID)
    if model and tokenizer and device:
        try:
            chat_with_aita(model, tokenizer, device)
        except Exception as e:
            print(f"An unexpected error occurred during chat: {e}")
    else:
        print("Failed to load model and tokenizer. Exiting CLI.")
