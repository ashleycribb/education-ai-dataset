# Open Data Integration Workflow for AITA Content

## 1. Introduction

### Purpose
This document outlines the workflow for sourcing, extracting, and preprocessing content from external open data sources. The goal is to transform this external content into a "raw input" format suitable for use with `data_processing_scripts.py`, which then generates structured AITA dialogue datasets for fine-tuning.

### Example Sources
This guide focuses on two example data sources and their respective processing pipelines:
*   **Project Gutenberg**: For 4th-grade reading comprehension passages (narrative texts).
*   **OpenStax**: For 7th-grade science content (ecology).

## 2. General Prerequisites

### Python Libraries
Ensure you have the following Python libraries installed. You can typically install them using pip:
```bash
pip install requests beautifulsoup4
```
*   **`requests`**: For making HTTP requests to fetch web content (used by `extract_openstax_ecology.py`).
*   **`beautifulsoup4`**: For parsing HTML content (used by `extract_openstax_ecology.py`).
*   Standard libraries like `json`, `os`, and `re` are also used by the scripts.

### Necessary Python Scripts
The following scripts from this project are required for this workflow:
*   **`extract_gutenberg_stories.py`**: For processing text files from Project Gutenberg.
*   **`extract_openstax_ecology.py`**: For extracting content from OpenStax HTML pages.
*   **`preprocess_extracted_data.py`**: For cleaning and filtering the raw extracted data from both sources.

## 3. Workflow for Project Gutenberg (4th Grade Reading Passages)

This workflow describes how to obtain and process narrative texts suitable for 4th-grade reading comprehension AITAs.

### 3.1. Sourcing Content
1.  **Find Content**: Navigate to the [Project Gutenberg website](https://www.gutenberg.org/). Search for children's literature, fairy tales, or short stories that are in the public domain and appropriate for a 4th-grade reading level (considering vocabulary, sentence structure, and themes).
2.  **Download Files**: Download the selected texts as "Plain Text UTF-8" (`.txt`) files.
3.  **Place Files**:
    *   Create a directory structure `source_data/gutenberg_texts/` in your project if it doesn't exist.
    *   Place the downloaded `.txt` files into this `source_data/gutenberg_texts/` directory. For example, `story1.txt`, `another_story.txt`.

### 3.2. Extraction using `extract_gutenberg_stories.py`
1.  **Run the Script**: Open your terminal, navigate to the project directory, and run:
    ```bash
    python extract_gutenberg_stories.py
    ```
2.  **Script Functionality**:
    *   This script reads all `.txt` files from the `source_data/gutenberg_texts/` directory.
    *   It performs basic text cleaning (stripping whitespace, normalizing newlines). Conceptual comments in the script suggest where more advanced cleaning (like removing Gutenberg headers/footers) would be added for real, full-length Gutenberg texts.
    *   It structures the content from each file into a JSON object.
3.  **Expected Output**:
    *   **File**: `gutenberg_reading_passages_raw.json`
    *   **Structure**: A JSON list of objects, where each object represents a story:
        ```json
        [
            {
                "id": "gutenberg_story1",
                "topic": "Story 1", 
                "raw_text": "Once upon a time, a little rabbit lived in a forest...",
                "source_name": "Project Gutenberg",
                "source_url": "Project Gutenberg - Story 1", 
                "license": "Public Domain",
                "potential_grade_level": "3-5", 
                "subject": "Reading Comprehension"
            },
            // ... more stories ...
        ]
        ```

### 3.3. Preprocessing using `preprocess_extracted_data.py`
1.  **Input**: The `preprocess_extracted_data.py` script uses `gutenberg_reading_passages_raw.json` (or a dummy list if the file is not found) as its input for this step.
2.  **Filter Criteria**: Within `preprocess_extracted_data.py`, the `filter_criteria_reading_gr4` dictionary is defined to select appropriate content. An example:
    ```python
    filter_criteria_reading_gr4 = {
        "min_words": 10,
        "max_words": 200, # Adjust based on desired passage length for dialogues
        "keywords_any": ["forest", "cheese", "adventure", "hop", "rabbit", "mouse"], # Example keywords to include
        "grade_level": "3-5" # Simple substring match on 'potential_grade_level'
    }
    ```
    You may need to adjust these criteria based on the actual content downloaded.
3.  **Script Functionality**:
    *   The script loads the "raw" JSON data.
    *   For each item, it applies `clean_text()` (which primarily normalizes whitespace in the current version).
    *   It filters items based on word count (`min_words`, `max_words`), presence of any specified `keywords_any`, and a simple substring match for `grade_level`.
    *   It adds a `word_count` field to each processed item.
4.  **Expected Output**:
    *   **File**: `gutenberg_reading_passages_processed.json`
    *   **Structure**: Similar to the raw JSON, but only containing items that passed the filters, and with cleaned `raw_text` and an added `word_count`.

### 3.4. Licensing Note
Content sourced from Project Gutenberg is typically in the **Public Domain** in the United States. Verify the license status for any specific text, especially if accessing from other countries.

## 4. Workflow for OpenStax (7th Grade Science - Ecology)

This workflow describes how to obtain and process informational texts for 7th-grade science (ecology) AITAs.

### 4.1. Sourcing Content
1.  **Identify URL**: Browse an OpenStax textbook (e.g., "Concepts of Biology" at [openstax.org](https://openstax.org/)). Navigate to a specific chapter and section relevant to your learning objectives (e.g., Chapter 19, Section 1: Population Ecology).
2.  **Copy URL**: Copy the URL of the HTML page containing the desired content.
3.  **Update Script**: Open `extract_openstax_ecology.py` and update the `TARGET_URL` variable at the top of the script with the copied URL.
    ```python
    TARGET_URL = "https://openstax.org/books/concepts-biology/pages/19-1-population-ecology" # Example
    ```

### 4.2. Extraction using `extract_openstax_ecology.py`
1.  **Run the Script**: Open your terminal, navigate to the project directory, and run:
    ```bash
    python extract_openstax_ecology.py
    ```
2.  **Script Functionality**:
    *   The script attempts to fetch the HTML content from the `TARGET_URL` using the `requests` library.
    *   It then parses the HTML using `BeautifulSoup` to find and extract text segments (primarily paragraphs and headings) from the main content area of the page.
    *   **Fallback**: If the live web request fails (e.g., no internet in the execution environment), the script will fall back to using pre-defined simulated HTML content to allow it to run and demonstrate its parsing logic.
    *   It structures the extracted text segments into JSON objects.
3.  **Expected Output**:
    *   **File**: `openstax_ecology_content_raw.json`
    *   **Structure**: A JSON list of objects, where each object represents an extracted text segment:
        ```json
        [
            {
                "id": "openstax_conbio_sec19.1_s1_p1",
                "topic": "19.1 Population Ecology", 
                "raw_text": "Populations are dynamic entities. Their size and composition fluctuate...",
                "source_name": "OpenStax Concepts of Biology",
                "source_url": "https://openstax.org/books/concepts-biology/pages/19-1-population-ecology",
                "license": "CC BY 4.0",
                "potential_grade_level": "7-9", 
                "subject": "Science - Ecology"
            },
            // ... more segments ...
        ]
        ```

### 4.3. Preprocessing using `preprocess_extracted_data.py`
1.  **Input**: The `preprocess_extracted_data.py` script uses `openstax_ecology_content_raw.json` (or a dummy list if not found) as input for this step.
2.  **Filter Criteria**: Within `preprocess_extracted_data.py`, the `filter_criteria_ecology_gr7` dictionary is defined. An example:
    ```python
    filter_criteria_ecology_gr7 = {
        "min_words": 10,
        "max_words": 1000, # Scientific text can be longer
        "keywords_any": ["population", "ecosystem", "density", "producer", "sunlight", "biotic", "abiotic"],
        "grade_level": "7-9" 
    }
    ```
    Adjust these criteria based on the specific content and needs.
3.  **Script Functionality**: Similar to the Gutenberg processing, it cleans text and applies length, keyword, and grade level filters.
4.  **Expected Output**:
    *   **File**: `openstax_ecology_content_processed.json`
    *   **Structure**: Similar to the raw JSON, but filtered and with cleaned text and `word_count`.

### 4.4. Licensing Note
OpenStax textbooks are generally licensed under **Creative Commons Attribution (CC BY 4.0)**, which allows for adaptation and redistribution with attribution. Always verify the specific license for the content you are using.

## 5. Output Format ("Raw Input" for Dialogue Generation)

After running the extraction and preprocessing scripts, you will have `*_processed.json` files (e.g., `gutenberg_reading_passages_processed.json`, `openstax_ecology_content_processed.json`). These files serve as the "raw input" for the next stage of the AITA content pipeline.

The common structure for items in these processed files is a list of JSON objects, each with fields like:
*   `id`: (String) Unique identifier for the content piece.
*   `topic`: (String) A title or topic for the content.
*   `raw_text`: (String) The cleaned text content.
*   `source_name`: (String) Name of the original data source (e.g., "Project Gutenberg", "OpenStax Concepts of Biology").
*   `source_url`: (String) URL of the specific source page or item (if applicable).
*   `license`: (String) License information (e.g., "Public Domain", "CC BY 4.0").
*   `potential_grade_level`: (String) Estimated grade level(s) for the content.
*   `subject`: (String) The educational subject (e.g., "Reading Comprehension", "Science - Ecology").
*   `word_count`: (Integer) The number of words in `raw_text`.

This structured data is then intended to be used by `data_processing_scripts.py` to generate the more detailed AITA dialogue datasets required for fine-tuning.

## 6. Important Considerations

*   **Ethical Web Scraping**:
    *   When adapting these scripts or creating new ones to extract data from other websites, always respect `robots.txt` files.
    *   Adhere to the website's Terms of Service.
    *   Avoid sending rapid, high-volume requests that could overload a server. Implement delays between requests if necessary.
    *   Prioritize using official APIs if available.

*   **License Verification**:
    *   **Crucial**: Before using any data (text, images, etc.) from any source, thoroughly verify its license and ensure your intended use complies with the terms. Not all "open" or "free" content is suitable for use in AI training or for all types of deployment.
    *   Keep records of licenses for all sourced materials.

*   **Script Adaptability**:
    *   The HTML parsing logic in `extract_openstax_ecology.py` is specific to the current structure of the OpenStax website. If the website's design changes, this script (particularly the BeautifulSoup selectors) may need to be updated.
    *   Similarly, cleaning logic for Project Gutenberg texts might need refinement based on the specific formatting of different e-books.

This workflow provides a foundation for sourcing and preparing diverse educational content for the AITA ecosystem.
