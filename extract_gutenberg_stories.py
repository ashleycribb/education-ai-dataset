import os
import json

# Define the input directory path relative to the script's location
INPUT_DIR = "source_data/gutenberg_texts"
OUTPUT_FILE = "gutenberg_reading_passages_raw.json"

def process_gutenberg_files(input_dir: str, output_file: str):
    """
    Processes .txt files from the input directory, extracts content,
    and saves it in a structured JSON format.
    """
    all_stories_data = []
    processed_files_count = 0

    # Ensure the input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)
            story_id_base = os.path.splitext(filename)[0] # e.g., "story1"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_text_content = f.read()

                # --- Conceptual Basic Cleaning ---
                # 1. Remove Project Gutenberg headers/footers (if present in real files)
                #    Example (conceptual, actual markers vary):
                #    text = text.split("*** START OF THIS PROJECT GUTENBERG EBOOK")[1]
                #    text = text.split("*** END OF THIS PROJECT GUTENBERG EBOOK")[0]
                #    For this prototype, our placeholder files are assumed clean.
                cleaned_text = raw_text_content.strip() 
                # 2. Normalize whitespace (e.g., multiple newlines to one)
                cleaned_text = "\n".join([line.strip() for line in cleaned_text.splitlines() if line.strip()])


                if not cleaned_text: # Skip if file is empty after cleaning
                    print(f"Warning: File '{filename}' is empty after cleaning. Skipping.")
                    continue

                story_data = {
                    "id": f"gutenberg_{story_id_base}",
                    "topic": story_id_base.replace("_", " ").title(), # e.g., "Story 1"
                    "raw_text": cleaned_text,
                    "source_name": "Project Gutenberg",
                    "source_url": f"Project Gutenberg - {story_id_base.replace('_', ' ').title()}", # Placeholder
                    "license": "Public Domain",
                    "potential_grade_level": "3-5", # Placeholder
                    "subject": "Reading Comprehension"
                }
                all_stories_data.append(story_data)
                processed_files_count += 1
                print(f"Processed: {filename}")

            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    # Save the structured data to the output JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_stories_data, f, indent=4)
        print(f"\nSuccessfully processed {processed_files_count} stories.")
        print(f"Output saved to {output_file}")
    except IOError as e:
        print(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")


if __name__ == "__main__":
    # Create the input directory if it doesn't exist (for robustness, though task implies it's pre-created)
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        print(f"Created input directory: {INPUT_DIR}")
        # Optionally, create dummy files here if they weren't made by the bash command
        # For this task, we assume they were created by the previous bash step.

    process_gutenberg_files(INPUT_DIR, OUTPUT_FILE)

    # Verify content of dummy files if needed for testing
    # print("\nVerifying dummy file content (if they were meant to be created by this script):")
    # for i in range(1,3):
    #     dummy_file_path = os.path.join(INPUT_DIR, f"story{i}.txt")
    #     if os.path.exists(dummy_file_path):
    #         with open(dummy_file_path, 'r') as f_verify:
    #             print(f"Content of {dummy_file_path}: '{f_verify.read().strip()}'")
    #     else:
    #         print(f"{dummy_file_path} not found for verification.")
