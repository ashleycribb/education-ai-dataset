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

# Dataset for the primary AITA profile (e.g., Reading Comprehension)
dataset_path = "initial_structured_aita_data.json"
output_dir = "./test_run_results" # Changed for smoke test

# --- Conceptual Comments for Multi-AITA Profile Training ---
# To train a different AITA (e.g., Eco Explorer):
# 1. Ensure you have a dataset for that AITA (e.g., "eco_explorer_aita_sample_data.json" or its splits).
#    This dataset should be formatted similarly, with dialogues targeting the specific AITA's subject and LOs.
#
# 2. Update `dataset_path` to point to the new dataset:
#    dataset_path = "eco_explorer_aita_sample_data.json" # Or "eco_explorer_train_split.json" if pre-split
#
# 3. Update `output_dir` to save the new AITA's adapter to a different location:
#    output_dir = "./results_phi3_aita_eco_pilot"
#
# 4. System Prompt Considerations for SFT Data Formatting:
#    The `format_dialogue_for_sft` function uses `tokenizer.apply_chat_template`.
#    If different AITA profiles require substantially different system prompts embedded within
#    the training data itself (beyond what the user-assistant turn structure provides),
#    the data generation script (`data_processing_scripts.py`) should ensure the
#    `dialogue_turns` in the JSON for that specific AITA include a system message
#    as the first turn, e.g., {"role": "system", "content": "You are Eco Explorer AITA..."}.
#    Alternatively, the `format_dialogue_for_sft` function could be modified to dynamically
#    prepend a system prompt based on the AITA profile associated with the dataset,
#    though this adds complexity if mixing datasets directly.
#    For SFT, the key is that the `text` field fed to the trainer accurately reflects
#    the full prompt structure the model should learn, including any system-level instructions.
# --- End Conceptual Comments ---


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
target_modules = ["qkv_proj", "o_proj", "gate_up_proj", "down_proj", "fc1", "fc2"]


# --- 2. Model and Tokenizer Loading ---
def load_model_and_tokenizer(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Tokenizer loaded. Pad token: {tokenizer.pad_token}, EOS token: {tokenizer.eos_token}")
    print(f"Default chat template: {tokenizer.chat_template or 'Not set in tokenizer, will use manual formatting.'}")

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if use_bf16 else (torch.float16 if use_fp16 else torch.float32)
    )
    print(f"Model '{model_name}' loaded successfully on device: {model.device}")
    return model, tokenizer

# --- 3. Dataset Loading and Preprocessing ---
def format_dialogue_for_sft(example: Dict[str, Any], tokenizer: AutoTokenizer) -> Dict[str, str]:
    # This function assumes 'dialogue_turns' field exists based on `data_processing_scripts.py`
    # For the enhanced AITA JSON, the actual turns are in 'dialogue_turns'.
    dialogue_turns_data = example.get('dialogue_turns', [])
    if not dialogue_turns_data: # Check if 'dialogue_turns' is missing or empty
        # Fallback for old format if 'dialogue' field (no 's') exists
        dialogue_turns_data = example.get('dialogue', [])
        if not dialogue_turns_data:
            return {"text": ""}

    messages = []
    # Check if the first turn is a system prompt, if so, include it.
    # This supports datasets where the system prompt is part of the dialogue history.
    if dialogue_turns_data and dialogue_turns_data[0].get("speaker", "").lower() == "system":
        messages.append({"role": "system", "content": dialogue_turns_data[0].get("utterance","")})
        dialogue_turns_data = dialogue_turns_data[1:] # Process remaining turns

    for turn in dialogue_turns_data:
        speaker = turn.get("speaker", "").lower()
        utterance = turn.get("utterance", "")

        if speaker == "student" or speaker == "user":
            messages.append({"role": "user", "content": utterance})
        elif speaker == "aita" or speaker == "assistant":
            messages.append({"role": "assistant", "content": utterance})

    if not messages or messages[-1]["role"] != "assistant":
        # SFT expects the sequence to end with an assistant's response.
        # If only a system prompt was added, or last turn isn't assistant, this is likely not a valid SFT example.
        # However, apply_chat_template with add_generation_prompt=False usually handles this correctly
        # by ensuring the template ends as if the assistant just spoke.
        pass

    formatted_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    return {"text": formatted_text}


def load_and_prepare_dataset(dataset_path: str, tokenizer: AutoTokenizer):
    """Loads and prepares the dataset for SFT."""
    try:
        # This assumes the JSON contains a list of dialogue objects.
        # If JSONL, use: dataset = load_dataset('json', data_files=dataset_path, split='train', lines=True)
        dataset = load_dataset('json', data_files=dataset_path, split='train')
        print(f"Dataset loaded from {dataset_path}. Number of examples: {len(dataset)}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        dummy_data = [ # Ensure dummy data has 'dialogue_turns' or 'dialogue'
            {"dialogue_turns": [{"speaker": "user", "utterance": "Hello"}, {"speaker": "assistant", "utterance": "Hi there!"}]},
        ]
        dataset = Dataset.from_list(dummy_data)
        print("Loaded dummy dataset due to error.")

    formatted_dataset = dataset.map(
        lambda example: format_dialogue_for_sft(example, tokenizer),
        remove_columns=[col for col in dataset.column_names if col != "text"]
    )
    formatted_dataset = formatted_dataset.filter(lambda example: len(example['text']) > 0)
    print(f"Dataset formatted. Number of examples after formatting/filtering: {len(formatted_dataset)}")
    return formatted_dataset

# --- 4. PEFT Configuration (LoRA) ---
def get_lora_config():
    peft_config = LoraConfig(
        r=lora_r, lora_alpha=lora_alpha, target_modules=target_modules,
        lora_dropout=lora_dropout, bias="none", task_type="CAUSAL_LM"
    )
    print("LoRA config created.")
    return peft_config

# --- 5. Training Arguments ---
def get_training_args():
    training_args = TrainingArguments(
        output_dir=output_dir, num_train_epochs=num_train_epochs, max_steps=3,
        per_device_train_batch_size=per_device_train_batch_size,
        per_device_eval_batch_size=per_device_eval_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        learning_rate=learning_rate, logging_steps=logging_steps,
        logging_dir="./test_run_logs", save_steps=save_steps,
        save_total_limit=save_total_limit, fp16=use_fp16, bf16=use_bf16,
        optim="paged_adamw_8bit"
    )
    print("TrainingArguments created.")
    return training_args

# --- 6. Trainer Initialization ---
def initialize_trainer(model, tokenizer, train_dataset, peft_config, training_args):
    trainer = SFTTrainer(
        model=model, tokenizer=tokenizer, train_dataset=train_dataset,
        peft_config=peft_config, dataset_text_field="text",
        max_seq_length=max_seq_length, args=training_args,
    )
    print("SFTTrainer initialized.")
    return trainer

# --- 7. Main Script Execution ---
if __name__ == "__main__":
    print("--- Starting Fine-tuning Setup for AITA on Phi-3 ---")

    print("\n--- Step 1: Loading Model and Tokenizer ---")
    model, tokenizer = load_model_and_tokenizer(model_name_or_path)

    print("\n--- Step 2: Loading and Preparing Dataset ---")
    if not os.path.exists(dataset_path):
        print(f"ERROR: Dataset file not found at {dataset_path}")
        # Create a dummy dataset with 'dialogue_turns' to match expected structure
        dummy_dialogues = [
            {"dialogue_turns": [{"speaker": "user", "utterance": "Example Q1?"}, {"speaker": "assistant", "utterance": "Example A1."}]},
            {"dialogue_turns": [{"speaker": "user", "utterance": "Example Q2?"}, {"speaker": "assistant", "utterance": "Example A2."}]}
        ]
        with open(dataset_path, 'w') as f: json.dump(dummy_dialogues, f)
        print(f"Created a dummy dataset at {dataset_path} for setup demonstration.")

    train_dataset = load_and_prepare_dataset(dataset_path, tokenizer)

    if len(train_dataset) > 0:
        print("\nSample of formatted training data (first example):")
        print(f"'{train_dataset[0]['text']}'") # Added quotes for clarity
    else:
        print("No data to display after formatting. Check dataset and formatting function.")

    print("\n--- Step 3: PEFT Configuration ---")
    peft_config = get_lora_config()

    print("\n--- Step 4: Training Arguments ---")
    training_args = get_training_args()

    print("\n--- Step 5: Initializing Trainer ---")
    trainer = initialize_trainer(model, tokenizer, train_dataset, peft_config, training_args)
    print("Trainer setup is complete and ready for training.")

    print("\n--- Step 6: Training ---")
    print("Starting training...")
    trainer.train()
    print("Training finished.")

    print("\n# To save the fine-tuned model adapters, uncomment:")
    print("# trainer.save_model(os.path.join(output_dir, 'final_checkpoint'))")
    print("# print(f'Model adapters saved to {os.path.join(output_dir, 'final_checkpoint')}')")

    print("\n--- Fine-tuning script setup finished. ---")
