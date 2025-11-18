# Long-Term Data Sourcing Strategy for AITA Project

## 1. Introduction

### Importance
A robust and continuous data sourcing strategy is paramount for the AITA (AI Tutor) project. To create diverse, knowledgeable, engaging, and up-to-date AITAs, we must consistently acquire high-quality educational content. This strategy ensures that our AITAs can evolve, cover a wider range of subjects and grade levels, and adapt to new pedagogical insights and curriculum changes.

### Goal
The primary goal of this strategy is to establish a scalable, maintainable, and ethically sound pipeline for identifying, vetting, extracting, preprocessing, and managing raw educational content from open data sources. This pipeline will feed the subsequent stages of AITA dialogue generation and model fine-tuning.

## 2. Key Roles (Future Vision)

As the AITA project scales, dedicated roles will be crucial for effective data sourcing and management:

*   **Content Curators/Subject Matter Experts (SMEs)**:
    *   Identify and evaluate potential data sources for specific subjects and grade levels.
    *   Assess content for pedagogical relevance, accuracy, and appropriateness.
    *   Define metadata, tags, and learning objective alignments for sourced content.
*   **Data Engineers**:
    *   Develop and maintain scripts and tools for extracting, transforming, and loading data from various sources.
    *   Manage the content registry/database and ensure data quality and integrity.
    *   Implement versioning for datasets and processing scripts.
*   **AI/NLP Specialists**:
    *   Analyze sourced content for suitability for SLM fine-tuning (e.g., text complexity, dialogue potential).
    *   Develop and refine preprocessing techniques to optimize content for AITA development.
    *   Collaborate on defining the "Raw Input" schema.
*   **Librarian/Archivist/License Specialist**:
    *   Oversee license verification and compliance for all sourced materials.
    *   Manage metadata standards and ensure proper content provenance.
    *   Track content usage rights and any changes to source licenses.

## 3. Process for Identifying and Vetting New Open Data Sources

### Continuous Scouting Methods
*   **OER Repositories**: Regularly monitor platforms like OER Commons, MERLOT, OpenStax, CK-12, etc.
*   **Academic Directories**: Explore university open courseware, institutional repositories, and open access journal databases (e.g., DOAJ).
*   **Government & NGO Portals**: Check educational sections of government agencies (e.g., NASA, EPA, Library of Congress, National Archives) and NGOs with educational missions.
*   **Hugging Face Datasets Hub**: Continuously search for new datasets relevant to K-12 education, filtering by license and content type.
*   **Community Recommendations**: Establish a mechanism for community members to suggest new sources (see Section 7).
*   **Automated Alerts**: Set up alerts for new content in relevant open access journals or repositories.

### Triage Checklist for New Sources
Before significant effort is invested in a new data source, it should undergo a preliminary triage based on the following criteria:

1.  **License Verification (Primary Filter)**:
    *   **Crucial First Step**: Is the content under a permissive license suitable for AITA development and deployment (e.g., Public Domain, CC0, CC BY, CC BY-SA, MIT, Apache 2.0)?
    *   Are there any restrictions (e.g., Non-Commercial "NC", No-Derivatives "ND") that conflict with intended use?
    *   Is the license clearly stated and verifiable?
    *   **Action**: If licensing is restrictive or unclear, the source is typically deprioritized or flagged for legal review.

2.  **Content Relevance**:
    *   Does the content align with target subjects (e.g., Reading Comprehension, Science - Ecology)?
    *   Is it appropriate for the target grade levels (e.g., 4th Grade, 7th Grade)?
    *   Can it be mapped to specific Learning Objectives (LOs)?
    *   Does it offer potential for generating pedagogically sound dialogues?

3.  **Content Quality**:
    *   **Accuracy**: Is the information factually correct and up-to-date?
    *   **Authority**: Is the source reputable and authoritative in its domain?
    *   **Clarity & Readability**: Is the content well-written and understandable for the target audience?
    *   **Bias**: Is the content relatively free from harmful biases? If biases are present, can they be easily identified and mitigated?

4.  **Data Accessibility & Format**:
    *   **APIs**: Does the source offer an API for programmatic access?
    *   **Bulk Downloads**: Is content available for download in manageable formats (e.g., TXT, HTML, JSON, XML, PDF)?
    *   **Scrapability**: If direct download or API is not available, can the content be reasonably extracted via web scraping? (Requires adherence to `robots.txt` and terms of service).
    *   **Format Structure**: Is the data reasonably structured, or will it require extensive parsing?

5.  **Source Stability & Persistence**:
    *   Is the source likely to be maintained and available long-term?
    *   Are there persistent identifiers (e.g., DOIs, PURLs) for the content?

### Prioritization Framework (Conceptual)
Based on the triage checklist, sources will be prioritized. High priority would be given to sources that score well on:
*   Permissive Licensing
*   High Content Relevance & Quality
*   Easy Data Accessibility

A simple scoring system or a qualitative review board (involving SMEs, librarians, and AI specialists) could be used.

## 4. Extraction and Preprocessing Pipeline (Iterative Refinement)

### Leveraging Existing Scripts
*   The existing scripts (`extract_gutenberg_stories.py`, `extract_openstax_ecology.py`) serve as initial templates.
*   `preprocess_extracted_data.py` provides a foundation for cleaning and filtering.

### Need for New Extraction Scripts
*   Each new data source or format will likely require a custom extraction script (or significant adaptation of existing ones).
*   These scripts should handle source-specific structures, authentication (if any), rate limiting, and error handling.

### Standardized "Raw Input" JSON Format
*   A critical goal is to transform diverse source data into a consistent "Raw Input" JSON format. This format is the output of `preprocess_extracted_data.py`.
*   Key fields include `id`, `topic`, `raw_text`, `source_name`, `source_url`, `license`, `potential_grade_level`, `subject`, `word_count`.
*   This standardization simplifies the input requirements for `data_processing_scripts.py` (which generates the final AITA dialogue JSON).

### Quality Gates
*   **After Extraction**: Automated checks for empty content, very short texts, or obvious formatting issues. Manual spot-checks by curators.
*   **After Preprocessing**: Automated checks on word counts, keyword presence (if applicable). Curators review samples to ensure cleaning didn't corrupt content and filters were applied correctly.
*   **Feedback Loop**: Issues found at quality gates should feedback into improving extraction/preprocessing scripts or adjusting source vetting.

## 5. Content Registry/Database for Sourced Materials (Conceptual)

### Purpose
To effectively manage and track raw educational content *before* it's transformed into AITA dialogue datasets, a dedicated Content Registry (or database) is envisioned.

### Key Schema Fields (Conceptual)
*   `sourced_content_id`: (Primary Key) Unique internal ID for the sourced item.
*   `original_source_name`: (String) E.g., "Project Gutenberg", "OpenStax Concepts of Biology".
*   `original_source_url`: (String) Direct URL to the specific content item.
*   `retrieval_date`: (Date) When the content was downloaded/ingested.
*   `license_type`: (String) E.g., "Public Domain", "CC BY 4.0", "CC BY-NC-SA 3.0".
*   `license_url`: (String) Link to the license text.
*   `subject_tags`: (List of Strings) E.g., ["Reading Comprehension", "Ecology", "Photosynthesis"].
*   `estimated_grade_level_tags`: (List of Strings) E.g., ["Grade 4", "Middle School", "7-9"].
*   `content_type`: (String) E.g., "Narrative Text", "Informational Text", "Lesson Plan Snippet", "Scientific Article Section".
*   `raw_extracted_text_or_path_to_file`: (Text or String) Either the full raw text (if short) or a path to the stored raw file.
*   `preprocessing_status`: (String) E.g., "New", "Needs Cleaning", "Cleaned", "Filtered", "Approved for Dialogue Generation", "Deprecated".
*   `curator_notes`: (Text) Notes from SMEs or curators regarding quality, suitability, potential uses, or issues.
*   `version_of_source_content`: (String, Optional) If the source content itself has versions.

### Benefits
*   **Provenance**: Clear record of where content came from and when.
*   **License Management**: Central place to track usage rights.
*   **Versioning**: Track changes to raw content if re-downloaded or updated.
*   **Review Tracking**: Monitor the status of content as it moves through the curation pipeline.
*   **Reduces Redundancy**: Avoid re-extracting the same content.
*   **Facilitates Collaboration**: Allows multiple team members to work with a shared understanding of available raw materials.

## 6. Versioning Strategy

A comprehensive versioning strategy is essential for maintainability and reproducibility:

*   **Source Extraction Scripts**: Use Git for version control of all scripts (`extract_*.py`, `preprocess_extracted_data.py`, etc.).
*   **Downloaded Datasets/Raw Content**:
    *   Store raw downloaded files in a structured way, perhaps with a timestamp or version in the filename/path.
    *   Consider using a data versioning tool (like DVC - Data Version Control) for large raw files if they are stored in a Git repository (often via Git LFS).
*   **Preprocessed "Raw Input" Datasets**: Version these JSON files (e.g., `gutenberg_reading_passages_processed_v1.json`, `gutenberg_reading_passages_processed_v2.json`).
*   **Final AITA Dialogue Fine-Tuning Datasets**: Version these as well (e.g., `pilot_dataset_reading_compre_v1.1.json`).
*   **Ontologies and Database Schemas**: If/when formalized, these also need version control.

## 7. Community Contributions (Future Vision)

A future project landing page or community portal could significantly enhance data sourcing:

*   **Suggesting New Sources**: Provide a form or forum for community members (educators, parents, students) to suggest new open data sources.
*   **Community Vetting**: Implement a system where community members can review and rate the quality, appropriateness, and relevance of potential content items.
*   **Contributions to Data Preparation**:
    *   **Transcription**: For audio or video content (if the project expands to these modalities).
    *   **Initial Tagging**: Community members could help with initial tagging of content (subject, grade level, keywords).
    *   **Identifying Biases**: Crowdsourcing the identification of potential biases in content.
*   **Drafting/Reviewing AITA Dialogues (Advanced)**: A more advanced stage could involve community members drafting initial AITA dialogue structures based on sourced content, or reviewing AI-generated dialogues.

**Caveats**:
*   **Clear Guidelines**: Strict guidelines for content submission, tagging, and review would be essential.
*   **Moderation & Review Process**: A strong internal team would still be needed to moderate community contributions, verify licenses, and ensure overall quality and pedagogical alignment before content is used for AITA training.

## 8. Regular Review and Deprecation of Data

*   **Ongoing Relevance**: Educational content and curricula evolve. Sourced materials should be periodically reviewed (e.g., annually or biannually) for continued relevance and accuracy by SMEs.
*   **License Validity**: Licenses can change, or the interpretation of a license might evolve. Periodically re-verify the licenses of key data sources.
*   **Source Stability**: Check if original sources are still available and maintained.
*   **Deprecation Process**:
    *   Establish a clear process for marking content as "deprecated" in the Content Registry.
    *   Decide whether to remove deprecated content from active use in AITA training datasets.
    *   Consider implications for AITAs already fine-tuned on deprecated content.

This long-term strategy aims to create a sustainable flow of high-quality, appropriately licensed data to fuel the continuous improvement and expansion of the AITA ecosystem.
