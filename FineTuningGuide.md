# Fine-Tuning AITA SLMs: A Practical Guide

## 1. Overview

This guide provides instructions for fine-tuning Small Language Models (SLMs), such as Microsoft's Phi-3-mini series, to create specialized AI Tutors (AITAs) for K-12 education. The fine-tuning process adapts a general-purpose base SLM to specific pedagogical goals, subjects, and student interaction styles.

Our AITA datasets are designed with a "teach how to learn" philosophy. This means dialogues often guide students through Socratic questioning, metacognitive prompts, and strategies for problem-solving, rather than providing direct answers.

## 2. Environment Setup

### Recommended Python Version
*   Python 3.9 or higher is recommended.

### Essential Python Libraries
Install the following libraries using pip:
```bash
pip install torch torchvision torchaudio
pip install transformers datasets peft trl accelerate bitsandbytes sentencepiece
```
*   **`torch`**: The core PyTorch library.
*   **`transformers`**: Hugging Face's library for state-of-the-art NLP models.
*   **`datasets`**: For loading and processing datasets.
*   **`peft`**: Parameter-Efficient Fine-Tuning library from Hugging Face, used for LoRA.
*   **`trl`**: Transformer Reinforcement Learning library, provides `SFTTrainer` for supervised fine-tuning.
*   **`accelerate`**: Simplifies running PyTorch training scripts across different hardware setups (CPUs, GPUs, TPUs).
*   **`bitsandbytes`**: Required for QLoRA (Quantized LoRA), an option for more memory-efficient fine-tuning (though our primary script uses standard LoRA).
*   **`sentencepiece`**: Often required for tokenizers used by models like Phi-3.

### CUDA Setup for GPU Training
For practical and efficient fine-tuning, a CUDA-enabled GPU is highly recommended.
*   Ensure you have compatible NVIDIA drivers installed.
*   PyTorch with CUDA support will be installed via the `pip install torch` command if your environment is correctly set up for it.
*   Training on CPU only is possible but will be significantly slower.

## 3. Dataset Preparation

### Input Data Format
The fine-tuning process expects data in a specific AITA JSON format. Each JSON object represents a dialogue and includes:
*   `dialogue_id`: A unique identifier for the dialogue.
*   `aita_profile`: Details about the AITA's persona (subject, grade level, etc.).
*   `pedagogical_intent`: Learning objectives, expected student thinking processes, keywords.
*   `context_provided_to_aita`: Information about the student and the learning context (e.g., passage text).
*   `dialogue_turns`: A list of turns, where each turn specifies the `speaker` (AITA or student), `utterance`, and for AITA turns, crucial `pedagogical_notes` explaining the teaching strategy for that turn. Additional fields include `timestamp_utc`, `utterance_modality`, `safeguard_tags`, `xapi_verb_id`, `xapi_object_id`, and `ontology_concept_tags`.

Refer to `data_processing_scripts.py` for how this enhanced structure is generated.

### Script for Data Generation
*   **`data_processing_scripts.py`**: This script is the primary tool for creating the "gold standard" AITA dialogue datasets in the required JSON format.
*   It can generate datasets like:
    *   `pilot_dataset_reading_compre_v1.json` (for 4th-grade reading comprehension)
    *   `eco_explorer_aita_sample_data.json` (for 7th-grade science/ecology)

### Splitting the Dataset
*   **`split_dataset.py`**: This script is used to split your generated dataset into training, validation, and (optionally) test sets.
*   It typically produces files like:
    *   `train_split.json`
    *   `validation_split.json`
    *   `test_split.json`
*   **Importance**:
    *   **Training set**: Used to actually update the model's weights.
    *   **Validation set**: Used during training to monitor performance on unseen data, helping to prevent overfitting and to tune hyperparameters.
    *   **Test set**: Used after training for a final, unbiased evaluation of the fine-tuned model's performance.

## 4. Running the Fine-Tuning Script (`fine_tune_aita.py`)

The `fine_tune_aita.py` script orchestrates the supervised fine-tuning (SFT) process using LoRA.

### Key Configuration Variables
These variables are typically found at the top of `fine_tune_aita.py` and need to be configured for your specific fine-tuning run:
*   **`model_name_or_path`**: The identifier of the base SLM you want to fine-tune (e.g., `"microsoft/Phi-3-mini-4k-instruct"`).
*   **`dataset_path`**: Path to your training dataset file (e.g., `"train_split.json"` or the full dataset if not splitting for this run).
*   **`output_dir`**: Directory where the fine-tuned LoRA adapters and other training outputs (checkpoints, logs) will be saved (e.g., `"./results_phi3_aita_reading_pilot"`).
*   **(Conceptual) `eval_dataset_path`**: While not explicitly a top-level variable in the current script, if you enable evaluation in `TrainingArguments`, you would typically load an evaluation dataset and pass it to the `SFTTrainer`.

### Important Training Arguments
Within the `get_training_args()` function, several `TrainingArguments` significantly impact the training process:
*   **`num_train_epochs`**: The total number of times the training loop will iterate over the entire training dataset. (e.g., 1-3 for fine-tuning).
*   **`per_device_train_batch_size`**: The number of training examples processed per GPU (or CPU) in one forward/backward pass. Adjust based on GPU memory.
*   **`learning_rate`**: Controls how much the model's weights are updated during training. A common value for fine-tuning is `2e-4` or `2e-5`.
*   **`max_seq_length`**: The maximum length of input sequences (in tokens). Dialogues longer than this will be truncated. Phi-3-mini-4k-instruct supports up to 4096, but values like 2048 are often used.
*   Other arguments like `gradient_accumulation_steps`, `warmup_steps`, `logging_steps`, `save_steps` also play important roles.

### PEFT/LoRA Settings
Within the `get_lora_config()` function, `LoraConfig` parameters define how LoRA is applied:
*   **`r`**: The rank of the LoRA matrices. Higher `r` means more trainable parameters but can increase computational cost. Common values are 8, 16, 32.
*   **`lora_alpha`**: LoRA scaling factor. Often set to `2 * r`.
*   **`target_modules`**: A list of module names (layers) in the base model to which LoRA adapters will be applied (e.g., `["qkv_proj", "o_proj", "gate_up_proj"]` for Phi-3 models).

### Starting Training
Execute the script from your terminal:
```bash
python fine_tune_aita.py
```
Ensure your environment is activated and all paths in the script are correct.

### Expected Output
After a successful training run, the `output_dir` will contain:
*   **Checkpoints**: Subdirectories (e.g., `checkpoint-500`, `checkpoint-1000`) containing intermediate training states if `save_steps` is configured.
*   **LoRA Adapter Files**: The final LoRA adapter files, typically including:
    *   `adapter_model.bin` (or `.safetensors`): The trained LoRA weights.
    *   `adapter_config.json`: Configuration for the LoRA adapter.
*   Other files like `training_args.bin`, tokenizer files, and potentially log files.

The primary artifacts for deploying your fine-tuned AITA are the LoRA adapter files.

## 5. Fine-Tuning for a New AITA Profile

To fine-tune the base SLM for a new AITA profile (e.g., the "Eco Explorer AITA" for 7th-grade science):

1.  **Create a New Dataset**:
    *   Use `data_processing_scripts.py` to generate a new dataset specifically tailored to the new AITA's subject (e.g., Ecology), grade level (e.g., 7th), learning objectives, and pedagogical style.
    *   This will produce a new JSON file (e.g., `eco_explorer_aita_sample_data.json`).
    *   If desired, use `split_dataset.py` to create train/validation/test splits for this new dataset.

2.  **Update `fine_tune_aita.py` Configuration**:
    *   **`dataset_path`**: Change this variable to point to the new training data file (e.g., `"eco_explorer_train_split.json"` or the full `eco_explorer_aita_sample_data.json`).
    *   **`output_dir`**: Change this to a new directory to avoid overwriting previously trained adapters (e.g., `"./results_phi3_aita_eco_pilot"`).

3.  **System Prompt and Data Formatting**:
    *   The `format_dialogue_for_sft` function in `fine_tune_aita.py` uses `tokenizer.apply_chat_template` to format dialogues. This relies on the roles (`user`, `assistant`, and optionally `system`) present in your input JSON data.
    *   If your new AITA profile requires a significantly different **system prompt** than the one used for the Reading Comprehension AITA, ensure your new dataset (e.g., `eco_explorer_aita_sample_data.json`) includes this system prompt as the first turn in the `dialogue_turns` array for each dialogue. For example:
        ```json
        {
          "role": "system",
          "content": "You are Eco Explorer AITA, an AI tutor specializing in 7th-grade ecology..."
        }
        ```
    *   The `SFTTrainer` will then incorporate this system prompt when preparing sequences for training, ensuring the model learns the new persona and context.

4.  **Run Training**: Execute `python fine_tune_aita.py` as before. The script will now use the new dataset and save the resulting adapter for the "Eco Explorer AITA" to the new output directory.

By following these steps, you can create multiple specialized AITA profiles from the same base SLM.
