import os
import json
from typing import Dict, List, Any

import torch
from datasets import load_dataset, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig # For QLoRA
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training # For QLoRA
)
from trl import SFTTrainer

# --- 1. Configuration Variables ---
# Model and dataset paths
model_name_or_path = "microsoft/Phi-3-mini-4k-instruct"
# Assuming the dataset created in previous steps is used.
# The previous subtask saved to "initial_structured_aita_data.json"
dataset_path = "initial_structured_aita_data.json" 
output_dir = "./test_run_results" # Changed for smoke test

# Hyperparameters for training (reasonable defaults)
learning_rate = 2e-4
num_train_epochs = 1 # Usually 1-3 epochs for fine-tuning
per_device_train_batch_size = 1 # Adjust based on GPU memory
per_device_eval_batch_size = 1
gradient_accumulation_steps = 4 # Effective batch size = batch_size * num_gpus * grad_accum_steps
warmup_steps = 100 # Reduced for smoke test, though max_steps will override
logging_steps = 1 # Changed for smoke test
save_steps = 500 # Save checkpoints every 500 steps (will not be reached with max_steps=3)
save_total_limit = 2 # Only keep the last 2 checkpoints
max_seq_length = 2048 # Max sequence length for Phi-3-mini-4k-instruct is 4096, but 2048 is often a good start
# Use bf16 if available (Ampere GPUs and newer), otherwise fp16. Set to False if no mixed precision.
use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
use_fp16 = not use_bf16 and torch.cuda.is_available()

# PEFT/LoRA Configuration
lora_r = 16  # Rank of LoRA attention
lora_alpha = 32 # Alpha for LoRA scaling
lora_dropout = 0.05
# Target modules for Phi-3. Common layers are qkv_proj, o_proj, gate_up_proj, down_proj (or fc1/fc2 like names).
# It's often best to inspect the model architecture or use a utility to find all linear layers.
# For Phi-3, common targets are: 'qkv_proj', 'o_proj', 'gate_up_proj', 'down_proj'
# Using a more general approach to target all linear layers for LoRA.
# target_modules = "all-linear" # TRL's SFTTrainer might handle this automatically or via specific PEFT utils.
# More specific target modules often found in Phi-3 examples:
target_modules = ["qkv_proj", "o_proj", "gate_up_proj", "down_proj", "fc1", "fc2"]


# --- 2. Model and Tokenizer Loading ---

def load_model_and_tokenizer(model_name: str):
    """Loads the model and tokenizer."""
    # Tokenizer for Phi-3
    # Phi-3 model card notes: "The tokenizer files already provide placeholder tokens that can be used for 
    # downstream fine-tuning, but they can also be extended up to the model's vocabulary size."
    # It also uses a specific chat template.
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    # Set padding token if not already set. EOS token is often a good choice for padding in Causal LMs.
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Phi-3 model card often mentions `tokenizer.padding_side = 'left'` for batched generation.
    # For training with SFTTrainer, if using right padding (default), ensure attention masks are correctly handled.
    # SFTTrainer typically handles this well. Let's stick to default (right) unless issues arise.
    # tokenizer.padding_side = 'left' # Optional: if needed for specific packing/batching schemes

    print(f"Tokenizer loaded. Pad token: {tokenizer.pad_token}, EOS token: {tokenizer.eos_token}")
    print(f"Default chat template: {tokenizer.chat_template or 'Not set in tokenizer, will use manual formatting.'}")

    # Model loading
    # For QLoRA, BitsAndBytesConfig would be defined here:
    # bnb_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_use_double_quant=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16 if use_bf16 else torch.float16
    # )
    # model = AutoModelForCausalLM.from_pretrained(
    #     model_name,
    #     quantization_config=bnb_config, # Pass bnb_config here for QLoRA
    #     device_map="auto", # Automatically distribute model layers across available GPUs
    #     trust_remote_code=True,
    #     torch_dtype=torch.bfloat16 if use_bf16 else (torch.float16 if use_fp16 else torch.float32) # Set compute dtype
    # )
    
    # Standard LoRA (without quantization for this script's primary path)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto", # "auto" is good for multi-GPU, can be "cuda" for single GPU or "cpu"
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if use_bf16 else (torch.float16 if use_fp16 else torch.float32)
    )
    
    # For QLoRA, after loading with bnb_config, you might also need:
    # model = prepare_model_for_kbit_training(model)

    print(f"Model '{model_name}' loaded successfully on device: {model.device}")
    return model, tokenizer

# --- 3. Dataset Loading and Preprocessing ---

def format_dialogue_for_sft(example: Dict[str, Any], tokenizer: AutoTokenizer) -> Dict[str, str]:
    """
    Formats a single dialogue example from our AITA JSON structure into a string
    that adheres to the Phi-3 chat template for Supervised Fine-Tuning (SFT).

    The Phi-3 chat template is:
    <|user|>
    Question<|end|>
    <|assistant|>
    Answer<|end|>

    For multi-turn dialogues, this pattern repeats.
    The SFTTrainer expects a single 'text' field containing the fully formatted dialogue.
    We should also ensure proper BOS/EOS tokens are handled if required by the model/trainer.
    Phi-3's tokenizer.apply_chat_template handles BOS automatically.
    EOS should be at the very end of the assistant's final turn.
    """
    dialogue_turns: List[Dict[str, str]] = example.get('dialogue', [])
    if not dialogue_turns:
        return {"text": ""}

    # Use a list of message dicts for apply_chat_template
    messages = []
    for turn in dialogue_turns:
        speaker = turn.get("speaker", "").lower()
        utterance = turn.get("utterance", "")
        
        if speaker == "student" or speaker == "user": # Assuming 'student' maps to 'user' role
            messages.append({"role": "user", "content": utterance})
        elif speaker == "aita" or speaker == "assistant": # Assuming 'aita' maps to 'assistant' role
            messages.append({"role": "assistant", "content": utterance})
        # else: ignore other speaker types or handle as needed

    # `add_generation_prompt=False` ensures the template is for training (ends with assistant's turn)
    # Tokenizer handles BOS. EOS is added by SFTTrainer if the last turn is assistant and `append_eos_token=True` (default).
    # Or, we can manually ensure the last turn from assistant ends with EOS if that's desired.
    # For Phi-3, the template itself includes <|end|> after each turn.
    # SFTTrainer will concatenate these examples, so each should be a self-contained dialogue unit.
    
    formatted_text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=False # Important for SFT: ensures template ends with assistant response
    )
    
    # SFTTrainer usually handles adding EOS token at the end of sequences if desired.
    # However, Phi-3's template uses <|end|> after each segment.
    # The last <|end|> from apply_chat_template for the assistant's turn should suffice.
    # If an additional global EOS is needed beyond the template's own <|end|>, it can be appended here.
    # For now, rely on apply_chat_template and SFTTrainer defaults.
    # formatted_text += tokenizer.eos_token # Only if not handled by template/trainer

    return {"text": formatted_text}


def load_and_prepare_dataset(dataset_path: str, tokenizer: AutoTokenizer):
    """Loads and prepares the dataset for SFT."""
    try:
        # Load dataset from JSON file. Assumes each line is a JSON object or it's a list of JSON objects.
        # If the JSON is a single list of records, 'json' type is appropriate.
        # If it's a JSONL file (one JSON object per line), use `lines=True`.
        # Our `initial_structured_aita_data.json` is a list of JSON objects in a single file.
        dataset = load_dataset('json', data_files=dataset_path, split='train') 
        print(f"Dataset loaded from {dataset_path}. Number of examples: {len(dataset)}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        # Fallback for safety: create a dummy dataset if loading fails, to allow script to run
        dummy_data = [
            {"dialogue": [{"speaker": "user", "utterance": "Hello"}, {"speaker": "assistant", "utterance": "Hi there!"}]},
            {"dialogue": [{"speaker": "user", "utterance": "How are you?"}, {"speaker": "assistant", "utterance": "I'm doing well, thank you!"}]}
        ]
        dataset = Dataset.from_list(dummy_data)
        print("Loaded dummy dataset due to error.")


    # Apply formatting
    # Ensure tokenizer is passed to the mapping function correctly
    formatted_dataset = dataset.map(
        lambda example: format_dialogue_for_sft(example, tokenizer),
        remove_columns=[col for col in dataset.column_names if col != "text"] # Keep only 'text' or columns needed by SFTTrainer
    )
    
    # Filter out empty strings that might result from faulty examples
    formatted_dataset = formatted_dataset.filter(lambda example: len(example['text']) > 0)
    
    print(f"Dataset formatted. Number of examples after formatting/filtering: {len(formatted_dataset)}")
    return formatted_dataset

# --- 4. PEFT Configuration (LoRA) ---

def get_lora_config():
    """Returns the LoRA configuration."""
    # LoraConfig for PEFT
    # Note: For QLoRA, the model should already be loaded in 4/8 bit using BitsAndBytesConfig
    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        # target_modules can be a list of module names, e.g., ["q_proj", "v_proj"]
        # or set to "all-linear" to target all linear layers.
        # For Phi-3, specific modules like "qkv_proj", "o_proj", "gate_up_proj", "down_proj" are common.
        # If using "all-linear", ensure it's compatible with the PEFT version and model.
        # Using explicit names is safer.
        target_modules=target_modules, 
        lora_dropout=lora_dropout,
        bias="none",  # Typically "none" for LoRA
        task_type="CAUSAL_LM",
    )
    print("LoRA config created.")
    return peft_config

# --- 5. Training Arguments ---

def get_training_args():
    """Returns the training arguments."""
    training_args = TrainingArguments(
        output_dir=output_dir, # Already updated to ./test_run_results
        num_train_epochs=num_train_epochs, # Already 1
        max_steps=3, # Crucial for smoke test
        per_device_train_batch_size=per_device_train_batch_size, # Already 1
        per_device_eval_batch_size=per_device_eval_batch_size, # If using evaluation
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate,
        logging_steps=logging_steps, # Already 1
        logging_dir="./test_run_logs", # Added for smoke test logs
        save_steps=save_steps, # Will not be reached
        save_total_limit=save_total_limit,
        # evaluation_strategy="steps", # Set to "steps" if eval_dataset is provided
        # eval_steps=save_steps,        # Evaluate at the same frequency as saving
        fp16=use_fp16,
        bf16=use_bf16,
        optim="paged_adamw_8bit", # Paged optimizer for memory efficiency, good with QLoRA
        # Other useful arguments:
        # report_to="tensorboard", # For logging to TensorBoard
        # lr_scheduler_type="cosine",
        # weight_decay=0.01,
        # max_grad_norm=0.3, # Gradient clipping
        # group_by_length=True, # Speeds up training by batching similar length sequences
    )
    print("TrainingArguments created.")
    return training_args

# --- 6. Trainer Initialization ---

def initialize_trainer(model, tokenizer, train_dataset, peft_config, training_args):
    """Initializes the SFTTrainer."""
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        # eval_dataset=eval_dataset, # Provide this if you have a validation set
        peft_config=peft_config,
        dataset_text_field="text",  # Name of the field in the dataset that contains the formatted text
        max_seq_length=max_seq_length,
        args=training_args,
        # packing=True, # Setting packing=True can significantly speed up training but requires careful attention to data formatting and EOS tokens.
                       # It concatenates multiple short examples into a single sequence.
                       # If not packing, ensure individual examples are not too short on average.
    )
    print("SFTTrainer initialized.")
    return trainer

# --- 7. Main Script Execution ---

if __name__ == "__main__":
    print("--- Starting Fine-tuning Setup for AITA on Phi-3 ---")

    # Step 1: Load model and tokenizer
    print("\n--- Step 1: Loading Model and Tokenizer ---")
    model, tokenizer = load_model_and_tokenizer(model_name_or_path)

    # Step 2: Load and prepare dataset
    print("\n--- Step 2: Loading and Preparing Dataset ---")
    # Check if dataset file exists
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset file not found at {dataset_path}")
        print("Please ensure the dataset exists or update the `dataset_path` variable.")
        # Create a dummy dataset to allow script to proceed without actual data for testing setup
        dummy_dialogues = [
            {"dialogue": [{"speaker": "user", "utterance": "Example question 1?"}, {"speaker": "assistant", "utterance": "Example answer 1."}]},
            {"dialogue": [{"speaker": "user", "utterance": "Example question 2?"}, {"speaker": "assistant", "utterance": "Example answer 2."}]}
        ]
        # Save dummy data to the expected path if it's missing, to allow dataset loader to work
        with open(dataset_path, 'w') as f:
            json.dump(dummy_dialogues, f)
        print(f"Created a dummy dataset at {dataset_path} for setup demonstration.")
    
    train_dataset = load_and_prepare_dataset(dataset_path, tokenizer)
    
    if len(train_dataset) > 0:
        print("\nSample of formatted training data (first example):")
        print(train_dataset[0]['text'])
    else:
        print("No data to display after formatting. Check dataset and formatting function.")

    # Step 3: PEFT Configuration
    print("\n--- Step 3: PEFT Configuration ---")
    peft_config = get_lora_config()
    
    # If not using QLoRA (model not quantized), and if PEFT is used, apply it now.
    # If model was loaded with BitsAndBytesConfig for QLoRA and prepare_model_for_kbit_training was called,
    # then get_peft_model is still used.
    # model = get_peft_model(model, peft_config) # This is often done by SFTTrainer if peft_config is passed.
    # print("PEFT model prepared.")
    # model.print_trainable_parameters() # Useful for verifying LoRA setup


    # Step 4: Training Arguments
    print("\n--- Step 4: Training Arguments ---")
    training_args = get_training_args()

    # Step 5: Initialize Trainer
    print("\n--- Step 5: Initializing Trainer ---")
    trainer = initialize_trainer(model, tokenizer, train_dataset, peft_config, training_args)
    print("Trainer setup is complete and ready for training.")

    # Step 6: Placeholder for Training Start
    print("\n--- Step 6: Training ---") # Modified heading
    # print("# To start training, uncomment the following lines:")
    print("Starting training...") # Uncommented
    trainer.train() # Uncommented
    print("Training finished.") # Uncommented
    
    print("\n# To save the fine-tuned model adapters, uncomment:")
    print("# trainer.save_model(os.path.join(output_dir, 'final_checkpoint'))")
    print("# print(f'Model adapters saved to {os.path.join(output_dir, 'final_checkpoint')}')")
    
    # Example of how to save full model if needed (usually for adapters it's different)
    # print("# To save the full model (if not using PEFT or after merging adapters):")
    # print("# model.save_pretrained(os.path.join(output_dir, 'final_model_full'))")
    # print("# tokenizer.save_pretrained(os.path.join(output_dir, 'final_model_full'))")
    
    print("\n--- Fine-tuning script setup finished. ---")
