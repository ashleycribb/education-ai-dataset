import json
import re
from typing import List, Dict, Any, Optional

# 1. Text Cleaning Function
def clean_text(text: str) -> str:
    """
    Cleans the input text by normalizing whitespace and stripping.
    Includes conceptual examples of more advanced cleaning.
    """
    if not isinstance(text, str):
        return "" # Or raise an error, depending on desired handling

    # Normalize whitespace: replace multiple spaces/tabs/newlines with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace from the whole text
    cleaned_text = cleaned_text.strip()

    # --- Conceptual Examples for More Advanced Cleaning (commented out) ---
    # Remove Project Gutenberg headers/footers (markers vary greatly)
    # cleaned_text = re.sub(r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK.*? \*\*\*', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    # cleaned_text = re.sub(r'\*\*\* END OF THIS PROJECT GUTENBERG EBOOK.*? \*\*\*', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)

    # Remove common artifacts like "[Illustration]" or "[Image:...]"
    # cleaned_text = re.sub(r'\[Illustration:.*?\]', '', cleaned_text, flags=re.IGNORECASE)
    # cleaned_text = re.sub(r'\[Image:.*?\]', '', cleaned_text, flags=re.IGNORECASE)

    # Remove "Click here for more" type phrases
    # cleaned_text = re.sub(r'Click here for more information', '', cleaned_text, flags=re.IGNORECASE)

    # Correct common OCR errors (example: 'rn' to 'm') - highly dependent on source
    # cleaned_text = re.sub(r'rn', 'm', cleaned_text)

    # Remove extra page numbers or chapter markers if they are simple patterns
    # cleaned_text = re.sub(r'\bPage \d+\b', '', cleaned_text)

    return cleaned_text

# 2. Filtering Functions
def filter_by_length(item: Dict[str, Any], min_words: Optional[int] = None, max_words: Optional[int] = None) -> bool:
    """
    Filters an item based on the word count of its 'raw_text' field.
    """
    text_to_check = item.get('raw_text', "")
    if not isinstance(text_to_check, str): # Ensure text is string
        return False

    word_count = len(text_to_check.split())
    item['word_count'] = word_count # Update word count in the item

    if min_words is not None and word_count < min_words:
        return False
    if max_words is not None and word_count > max_words:
        return False
    return True

def filter_by_keywords(item: Dict[str, Any], keywords: Optional[List[str]] = None, case_sensitive: bool = False) -> bool:
    """
    Filters an item if its 'raw_text' contains any of the specified keywords.
    Returns True if a keyword is found or if no keywords are specified.
    """
    if not keywords: # No keywords to filter by, so pass the item
        return True

    text_to_check = item.get('raw_text', "")
    if not isinstance(text_to_check, str):
        return False # Or handle as appropriate if text is not string

    search_text = text_to_check if case_sensitive else text_to_check.lower()

    for keyword in keywords:
        search_keyword = keyword if case_sensitive else keyword.lower()
        if search_keyword in search_text:
            return True # Found at least one keyword

    return False # No keywords found

def filter_by_grade_level(item: Dict[str, Any], target_grade_str: Optional[str] = None) -> bool:
    """
    Filters an item based on whether its 'potential_grade_level' contains the target_grade_str.
    Uses simple substring matching, case-insensitive.
    """
    if not target_grade_str: # No grade level filter specified, so pass the item
        return True

    grade_level_in_item = item.get('potential_grade_level', "")
    if not isinstance(grade_level_in_item, str): # Ensure it's a string
        return False

    return target_grade_str.lower() in grade_level_in_item.lower()

# 3. Main Processing Function
def preprocess_data(raw_data_list: List[Dict[str, Any]], filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Cleans and filters a list of raw data items based on specified criteria.
    """
    processed_items = []

    min_words = filter_criteria.get("min_words")
    max_words = filter_criteria.get("max_words")
    keywords_any = filter_criteria.get("keywords_any") # Expects a list of keywords
    keywords_case_sensitive = filter_criteria.get("keywords_case_sensitive", False)
    grade_level_filter = filter_criteria.get("grade_level")

    for item in raw_data_list:
        if not isinstance(item, dict) or 'raw_text' not in item:
            print(f"Warning: Skipping invalid item (not a dict or missing 'raw_text'): {item}")
            continue

        # Clean text
        item['raw_text'] = clean_text(item['raw_text'])

        # Apply filters
        if not filter_by_length(item, min_words, max_words):
            continue
            # item['word_count'] is updated by filter_by_length

        if not filter_by_keywords(item, keywords_any, keywords_case_sensitive):
            continue

        if not filter_by_grade_level(item, grade_level_filter):
            continue

        # If all filters pass (or are not specified), add to processed list
        processed_items.append(item)

    return processed_items

# 4. Main Execution Block
def load_json_data(filepath: str) -> List[Dict[str, Any]]:
    """Loads data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list): # Ensure top level is a list
                print(f"Warning: Data in {filepath} is not a list. Wrapping it in a list.")
                return [data]
            return data
    except FileNotFoundError:
        print(f"Warning: File '{filepath}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filepath}'.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred loading '{filepath}': {e}")
        return []

def save_json_data(data: List[Dict[str, Any]], filepath: str):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved {len(data)} items to {filepath}")
    except IOError:
        print(f"Error: Could not write to file '{filepath}'.")
    except Exception as e:
        print(f"An unexpected error occurred saving to '{filepath}': {e}")


if __name__ == "__main__":
    print("--- Starting Data Preprocessing ---")

    # --- Process Gutenberg Data ---
    gutenberg_raw_file = "gutenberg_reading_passages_raw.json"
    gutenberg_processed_file = "gutenberg_reading_passages_processed.json"

    gutenberg_data = load_json_data(gutenberg_raw_file)
    if not gutenberg_data: # If file not found or empty, use dummy data
        print(f"Using dummy data for Gutenberg as '{gutenberg_raw_file}' was not found or empty.")
        gutenberg_data = [
            {"id": "dummy_story1", "raw_text": "A little rabbit loved to hop in the green forest. It was a great adventure.", "potential_grade_level": "3-5"},
            {"id": "dummy_story2", "raw_text": "The brave mouse found a big piece of cheese. Yum!", "potential_grade_level": "2-4"},
            {"id": "dummy_story3", "raw_text": "This story is very short.", "potential_grade_level": "1-2"}
        ]

    filter_criteria_reading_gr4 = {
        "min_words": 10, # Adjusted to include dummy_story1 and dummy_story2
        "max_words": 200,
        "keywords_any": ["forest", "cheese", "adventure", "hop", "rabbit", "mouse"],
        "grade_level": "3-5" # This will match "3-5" and "2-4" (as "3-5" contains "3", "4", "5")
                               # A more precise grade filter might be needed for real scenarios
    }

    print(f"\nProcessing Gutenberg data (initial count: {len(gutenberg_data)})...")
    processed_gutenberg_data = preprocess_data(list(gutenberg_data), filter_criteria_reading_gr4) # Pass a copy
    save_json_data(processed_gutenberg_data, gutenberg_processed_file)
    print(f"Gutenberg data: {len(gutenberg_data)} items before -> {len(processed_gutenberg_data)} items after processing.")

    # --- Process OpenStax Ecology Data (Optional Example) ---
    openstax_raw_file = "openstax_ecology_content_raw.json"
    openstax_processed_file = "openstax_ecology_content_processed.json"

    openstax_data = load_json_data(openstax_raw_file)
    if not openstax_data:
        print(f"\nUsing dummy data for OpenStax as '{openstax_raw_file}' was not found or empty.")
        openstax_data = [
            {"id": "dummy_eco1", "raw_text": "Ecology is the study of animals and plants. Population density is important.", "potential_grade_level": "7-9"},
            {"id": "dummy_eco2", "raw_text": "A forest fire is a natural disaster that affects populations.", "potential_grade_level": "6-8"},
            {"id": "dummy_eco3", "raw_text": "Photosynthesis is key for producers in an ecosystem. Sunlight provides energy.", "potential_grade_level": "7-9"}
        ]
        # Create dummy file if it doesn't exist, so the load function can be tested if run again
        # if not os.path.exists(openstax_raw_file):
        #     save_json_data(openstax_data, openstax_raw_file)


    filter_criteria_ecology_gr7 = {
        "min_words": 10,
        "max_words": 1000,
        "keywords_any": ["population", "ecosystem", "density", "producer", "sunlight"],
        "grade_level": "7-9"
    }

    print(f"\nProcessing OpenStax Ecology data (initial count: {len(openstax_data)})...")
    processed_openstax_data = preprocess_data(list(openstax_data), filter_criteria_ecology_gr7) # Pass a copy
    save_json_data(processed_openstax_data, openstax_processed_file)
    print(f"OpenStax data: {len(openstax_data)} items before -> {len(processed_openstax_data)} items after processing.")

    print("\n--- Data Preprocessing Finished ---")
