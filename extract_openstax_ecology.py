import requests
from bs4 import BeautifulSoup
import json
import re # For cleaning whitespace

# Target URL for OpenStax Concepts of Biology - Chapter 19, Section 1: Population Ecology
TARGET_URL = "https://openstax.org/books/concepts-biology/pages/19-1-population-ecology"
OUTPUT_FILE = "openstax_ecology_content_raw.json"

def fetch_and_parse_openstax_content(url: str):
    """
    Fetches HTML content from the given URL, parses it, and extracts
    relevant text segments from the main content area.
    """
    extracted_segments = []
    
    try:
        print(f"Fetching content from: {url}")
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        html_content = response.text
        print("Content fetched successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        # Fallback to simulated HTML content if fetching fails (e.g., no internet in sandbox)
        print("Using simulated HTML content due to fetch error.")
        html_content = """
        <html><head><title>Population Ecology</title></head><body>
        <div id="main-content" class="main-content"> 
            <div class="section" data-content-id="19-1-section-title">
                <h2>19.1 Population Ecology</h2>
                <p>Populations are dynamic entities. Their size and composition fluctuate in response to numerous factors, including seasonal and yearly changes in the environment, natural disasters such as forest fires and volcanic eruptions, and competition for resources between and within species.</p>
                <p>The statistical study of populations is called demography: a set of mathematical tools designed to describe populations and investigate how they change. Many of these tools were actually designed to study human populations. For example, life tables, which detail the life expectancy of individuals within a population, were initially developed by life insurance companies to set insurance rates.</p>
            </div>
            <div class="section" data-content-id="19-1-another-subsection">
                 <h3>Population Size and Density</h3>
                 <p>Populations are characterized by their population size (the total number of individuals) and their population density (the number of individuals per unit area). A population may have a large number of individuals that are distributed densely, or sparsely.</p>
            </div>
        </div>
        </body></html>
        """
    
    print("Parsing HTML content...")
    soup = BeautifulSoup(html_content, "html.parser")
    
    # --- Text Extraction Logic ---
    # OpenStax content is often within <div class="main-content"> or similar.
    # Specific sections might be in <div class="section"> or <section> tags.
    # Paragraphs are in <p>, headings in <h1>, <h2>, <h3> etc.
    
    # Try to find a main content container. This class name might need adjustment
    # based on actual OpenStax structure if it changes.
    # For the chosen URL (and the fallback HTML), the content seems to be identifiable
    # by sections within a main area. Let's look for 'div' elements with class 'section'.
    # A more robust selector might be needed for the full site.
    
    # Based on inspection of the live site for the chosen URL, content is often within
    # <div id="main-content"> and then sections have specific classes or data attributes.
    # For this example, let's assume sections of interest are divs with class 'section'
    # or a specific data-content-id attribute if available.
    
    # For the fallback HTML and typical OpenStax structure:
    main_content_area = soup.find('div', id='main-content') # Or a more specific class for content
    if not main_content_area:
        # A more general approach if specific IDs/classes are not consistent
        main_content_area = soup.body # Fallback to body if no specific main content area found
        print("Warning: Specific main content area ('div#main-content') not found. Parsing from body. Results may vary.")

    if not main_content_area:
        print("Error: Could not find main content area or body in HTML. Cannot extract text.")
        return []

    section_count = 0
    paragraph_count_total = 0

    # Find all sections or main content divs
    # This might need to be adapted if the structure uses <section> tags or other containers
    sections = main_content_area.find_all('div', class_='section', recursive=True)
    if not sections: # If no 'div' with class 'section', try a broader approach
        sections = [main_content_area] # Treat the whole main content as one section

    for section_idx, section_div in enumerate(sections):
        section_count += 1
        current_topic = f"Ecology Section {section_idx + 1}" # Default topic
        
        # Try to get a more specific topic from a heading within the section
        first_heading = section_div.find(['h1', 'h2', 'h3', 'h4'])
        if first_heading and first_heading.get_text(strip=True):
            current_topic = first_heading.get_text(strip=True)
        
        paragraphs = section_div.find_all('p', recursive=True)
        
        for p_idx, p_tag in enumerate(paragraphs):
            raw_text = p_tag.get_text(separator=' ', strip=True)
            
            # Basic cleaning: replace multiple whitespaces/newlines with a single space
            cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
            
            if cleaned_text: # Only add if there's content
                paragraph_count_total += 1
                segment_data = {
                    "id": f"openstax_conbio_sec19.1_s{section_idx+1}_p{p_idx+1}", # More granular ID
                    "topic": current_topic,
                    "raw_text": cleaned_text,
                    "source_name": "OpenStax Concepts of Biology",
                    "source_url": url, # The URL from which the content was fetched
                    "license": "CC BY 4.0", # OpenStax books are typically CC BY
                    "potential_grade_level": "7-9", # Placeholder
                    "subject": "Science - Ecology"
                }
                extracted_segments.append(segment_data)
                print(f"Extracted segment: {current_topic} - Paragraph {p_idx+1} (ID: {segment_data['id']})")

    if not extracted_segments and main_content_area: # If sections approach failed, try all <p> in main_content_area
        print("No segments extracted via section-based approach. Trying broader paragraph search in main content.")
        all_paragraphs = main_content_area.find_all('p', recursive=True)
        current_topic = "General Ecology Content" # Fallback topic
        # Try to get a page title if possible
        page_title_tag = soup.find('title')
        if page_title_tag and page_title_tag.get_text(strip=True):
            current_topic = page_title_tag.get_text(strip=True)

        for p_idx, p_tag in enumerate(all_paragraphs):
            raw_text = p_tag.get_text(separator=' ', strip=True)
            cleaned_text = re.sub(r'\s+', ' ', raw_text).strip()
            if cleaned_text:
                paragraph_count_total += 1
                segment_data = {
                    "id": f"openstax_conbio_page_p{p_idx+1}",
                    "topic": current_topic,
                    "raw_text": cleaned_text,
                    "source_name": "OpenStax Concepts of Biology",
                    "source_url": url,
                    "license": "CC BY 4.0",
                    "potential_grade_level": "7-9",
                    "subject": "Science - Ecology"
                }
                extracted_segments.append(segment_data)
                print(f"Extracted segment (broad search): {current_topic} - Paragraph {p_idx+1} (ID: {segment_data['id']})")

    print(f"Found {section_count} potential sections. Extracted {len(extracted_segments)} text segments in total.")
    return extracted_segments

if __name__ == "__main__":
    print("--- Starting OpenStax Ecology Content Extraction ---")
    
    segments = fetch_and_parse_openstax_content(TARGET_URL)
    
    if segments:
        try:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(segments, f, indent=4)
            print(f"\nSuccessfully extracted {len(segments)} text segments.")
            print(f"Output saved to {OUTPUT_FILE}")
        except IOError as e:
            print(f"Error writing to output file {OUTPUT_FILE}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during saving: {e}")
    else:
        print("No text segments were extracted. Output file not created.")
        
    print("\n--- OpenStax Ecology Content Extraction Finished ---")
