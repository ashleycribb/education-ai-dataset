import json
import random
from typing import List, Dict, Any

# 1. Simulated Input Data (6 dialogue objects)
SIMULATED_AITA_DATA: List[Dict[str, Any]] = [
    {
        "dialogue_id": "kitten_main_idea",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.MainIdea", "text": "Identify the main idea..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "Let's read about a kitten..."}]
    },
    {
        "dialogue_id": "kitten_inference",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.Inference", "text": "Make simple inferences..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "What can we tell about how Lily felt...?"}]
    },
    {
        "dialogue_id": "kitten_vocab",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.Vocabulary", "text": "Determine the meaning of a word..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "The story says Lily's house was 'cozy'. What might 'cozy' mean?"}]
    },
    {
        "dialogue_id": "leaves_main_idea",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.MainIdea", "text": "Identify the main idea..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "Let's read about why leaves change color..."}]
    },
    {
        "dialogue_id": "leaves_inference",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.Inference", "text": "Make simple inferences..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "Why were the other colors hidden before autumn?"}]
    },
    {
        "dialogue_id": "leaves_vocab",
        "aita_profile": {"subject": "Reading Comprehension", "grade_level": "4", "persona_name": "ReaderAITA_Explorer_v1.3_Pilot"},
        "pedagogical_intent": {"learning_objectives": [{"id": "RC.4.LO.Vocabulary", "text": "Determine the meaning of a word..."}]},
        "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "The passage mentions 'chlorophyll, the green pigment'. What could 'pigment' mean?"}]
    }
]

# 2. Splitting Function
def split_data(
    data: List[Dict[str, Any]],
    train_frac: float = 0.7,  # Will be adjusted for small N
    val_frac: float = 0.15,   # Will be adjusted for small N
    test_frac: float = 0.15,  # Will be adjusted for small N
    random_seed: int = 42
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Splits data into training, validation, and test sets.
    Adjusts fractions for small datasets to achieve a 4-1-1 split for 6 items.
    """
    if not data:
        return {"train": [], "validation": [], "test": []}

    n_total = len(data)

    # Specific adjustment for 6 items to get 4-1-1 split
    if n_total == 6:
        n_train = 4
        n_val = 1
        n_test = 1
    else: # General case, though this script focuses on N=6
        n_train = int(train_frac * n_total)
        n_val = int(val_frac * n_total)
        n_test = n_total - n_train - n_val
        # Ensure test set gets at least 1 if fractions imply it, and adjust train accordingly
        if test_frac > 0 and n_test == 0 and n_total > n_train + n_val :
            n_test = 1
            if n_val > 0 and n_total > n_train + n_test: # if val exists, try to keep it
                 pass # n_train will be adjusted later if sum > n_total
            elif n_train > 0 : # if no val, or val cannot be kept, take from train
                n_train = n_train -1
        if val_frac > 0 and n_val == 0 and n_total > n_train + n_test :
            n_val = 1
            if n_train > 0 and n_total > n_val + n_test:
                 n_train = n_train -1

        # Final adjustment if sum is off (e.g. due to rounding)
        current_sum = n_train + n_val + n_test
        if current_sum != n_total:
            n_train = n_total - n_val - n_test # Prioritize val and test counts

    if n_train + n_val + n_test != n_total or n_train < 0 or n_val < 0 or n_test < 0:
        print(f"Warning: Calculated split ({n_train}, {n_val}, {n_test}) does not sum to total ({n_total}) or is invalid. Defaulting to proportional split or erroring for very small N.")
        # Fallback for extremely small N where 4-1-1 might not make sense, though problem specifies N=6
        if n_total < 3 and n_total > 0: # e.g. 1 or 2 items
            return {"train": list(data), "validation": [], "test": []} # Put all in train
        elif n_total == 0:
             return {"train": [], "validation": [], "test": []}
        # If still problematic, this indicates an issue with logic for general N, but for N=6 it's fixed.

    # Seed for reproducibility
    random.seed(random_seed)

    # Shuffle a copy of the data
    data_copy = list(data) # Create a shallow copy for shuffling
    random.shuffle(data_copy)

    # Perform splits
    train_data = data_copy[:n_train]
    val_data = data_copy[n_train : n_train + n_val]
    test_data = data_copy[n_train + n_val :]

    return {"train": train_data, "validation": val_data, "test": test_data}

# 3. Helper function to save data
def save_split_data(data: List[Dict[str, Any]], filename: str):
    """Saves the given data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved {len(data)} items to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

# 4. Main Execution Block
if __name__ == "__main__":
    print("--- Starting Dataset Splitting ---")

    # Use the predefined simulated data
    all_data = SIMULATED_AITA_DATA
    print(f"Total items in simulated dataset: {len(all_data)}")

    # Split the data
    # For N=6, this will result in 4 train, 1 validation, 1 test due to hardcoded logic
    split_datasets = split_data(all_data)

    train_set = split_datasets["train"]
    validation_set = split_datasets["validation"]
    test_set = split_datasets["test"]

    print(f"\nNumber of items in training set: {len(train_set)}")
    print(f"Number of items in validation set: {len(validation_set)}")
    print(f"Number of items in test set: {len(test_set)}")

    # Save each split to a file
    print("\n--- Saving Split Datasets ---")
    save_split_data(train_set, "train_split.json")
    save_split_data(validation_set, "validation_split.json")
    save_split_data(test_set, "test_split.json")

    print("\n--- Dataset Splitting Finished ---")

    # Optional: Print dialogue_ids in each set to verify the split
    print("\n--- Dialogue IDs in each split (for verification) ---")
    print(f"Train IDs: {[item['dialogue_id'] for item in train_set]}")
    print(f"Validation IDs: {[item['dialogue_id'] for item in validation_set]}")
    print(f"Test IDs: {[item['dialogue_id'] for item in test_set]}")
