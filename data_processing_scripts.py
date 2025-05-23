import json
from typing import List, Dict, Any, Optional

# --- Data Simulation ---

def load_simulated_raw_data() -> List[Dict[str, Any]]:
    """
    Returns a predefined list of dictionaries simulating raw educational content.
    """
    simulated_raw_data = [
        {
            "id": "photo_001",
            "topic": "Basic Photosynthesis",
            "raw_text": "Photosynthesis is the process plants use to convert light energy into chemical energy, producing glucose and oxygen from carbon dioxide and water.",
            "source_dataset": "simulated_oer",
            "potential_grade_level": "7"
        },
        {
            "id": "frac_001",
            "topic": "Adding Fractions",
            "raw_text": "To add 1/2 and 1/4, you first need to find a common denominator. For 2 and 4, the least common denominator is 4. So, 1/2 becomes 2/4. Then you add the numerators: 2/4 + 1/4 = 3/4.",
            "source_dataset": "simulated_oer",
            "potential_grade_level": "5"
        },
        {
            "id": "hist_001",
            "topic": "American Revolution Causes",
            "raw_text": "One major cause of the American Revolution was 'taxation without representation'.",
            "source_dataset": "simulated_oer",
            "potential_grade_level": "8"
        }
    ]
    return simulated_raw_data

# --- Transformation ---

def transform_raw_to_aita_format(
    raw_item: Dict[str, Any],
    aita_profile: Dict[str, Any],
    interaction_type: str = "concept_explanation"
) -> Dict[str, Any]:
    """
    Transforms a raw_item into the target AITA JSON structure.

    Args:
        raw_item: A dictionary containing raw content (e.g., from load_simulated_raw_data).
        aita_profile: A dictionary defining the AITA's persona and target audience.
                      Example: {"subject": "Science", "grade_level": "7", 
                                "jurisdiction": "General", "learning_objective_id": "SCI.7.PS.1"}
        interaction_type: The type of interaction (e.g., "concept_explanation", "socratic_dialogue").

    Returns:
        A dictionary structured in the AITA JSON format.
    """
    aita_json_structure = {
        "aita_id": f"aita_{raw_item.get('id', 'unknown')}_{interaction_type}", # Made ID more specific
        "version": "1.0",
        "metadata": {
            "source_content_id": raw_item.get('id', 'unknown'),
            "original_source_dataset": raw_item.get('source_dataset', 'unknown'),
            "interaction_type": interaction_type,
            "creation_date": "YYYY-MM-DD", # Placeholder, ideally set to actual creation date
            "last_modified_date": "YYYY-MM-DD", # Placeholder
            "tags": [raw_item.get('topic', 'general')] + aita_profile.get('subject', '').lower().split(),
        },
        "aita_profile": aita_profile,
        "context": {
            "topic": raw_item.get('topic', 'N/A'),
            "prerequisites": [], # Can be expanded later
            "keywords": raw_item.get('topic', '').lower().split() + aita_profile.get('subject', '').lower().split(),
            "potential_grade_level": raw_item.get("potential_grade_level", "N/A")
        },
        "dialogue": [],
        "pedagogical_notes": [], # Overall notes for the dialogue, specific notes can be in turns
        "evaluation_metrics": { # Optional, for future use
            "clarity_score": None,
            "engagement_score": None,
            "learning_objective_alignment": None
        }
    }

    raw_text = raw_item.get("raw_text", "")
    # Simple heuristic for dialogue structure based on raw_text
    if "?" in raw_text and "answer:" in raw_text.lower(): 
        parts = raw_text.split("?", 1)
        question = parts[0] + "?"
        answer_section = parts[1].strip() if len(parts) > 1 else ""
        
        answer_delimiter = "answer:"
        answer = answer_section[answer_section.lower().find(answer_delimiter) + len(answer_delimiter):].strip() if answer_delimiter in answer_section.lower() else answer_section

        aita_json_structure["dialogue"].append({"speaker": "student", "utterance": question.strip(), "pedagogical_note": "Initial student question."})
        aita_json_structure["dialogue"].append({"speaker": "AITA", "utterance": answer.strip(), "pedagogical_note": "Direct answer to student's question."})
    else:
        aita_json_structure["dialogue"].append({"speaker": "AITA", "utterance": raw_text, "pedagogical_note": "Initial content presentation/explanation."})
        if interaction_type == "concept_explanation":
             aita_json_structure["dialogue"].append({"speaker": "AITA", "utterance": "Does that make sense, or would you like to explore any part of that in more detail?", "pedagogical_note": "Checking for understanding and inviting further questions."})
    
    # Add learning objective to metadata if available in profile
    if "learning_objective_text" in aita_profile:
        aita_json_structure["metadata"]["learning_objective_text"] = aita_profile["learning_objective_text"]
    if "learning_objective_id" in aita_profile:
        aita_json_structure["metadata"]["learning_objective_id"] = aita_profile["learning_objective_id"]


    return aita_json_structure

# --- LLM Augmentation Prompt Generation ---

def prepare_llm_augmentation_prompt(
    learning_objective: str,
    raw_content_snippet: Optional[str] = None,
    aita_profile: Optional[Dict[str, Any]] = None,
    example_dialogue_json: Optional[List[Dict[str,str]]] = None # Added example dialogue
) -> str:
    """
    Constructs a detailed prompt for an LLM to generate pedagogical dialogues.

    Args:
        learning_objective: The specific learning goal for the dialogue.
        raw_content_snippet: Optional factual text related to the objective.
        aita_profile: Optional AITA profile to tailor the dialogue.
        example_dialogue_json: Optional example of a desired dialogue format.

    Returns:
        A string prompt for the LLM.
    """
    prompt = f"Objective: Generate a pedagogically sound dialogue between an AI Tutor (AITA) and a student.\n"
    prompt += f"The primary learning objective for this dialogue is: \"{learning_objective}\"\n\n"
    
    prompt += "Dialogue Style & Philosophy:\n"
    prompt += "- The AITA should embody a 'teach how to learn' philosophy.\n"
    prompt += "- Employ Socratic questioning to guide the student's discovery process.\n"
    prompt += "- Explain concepts clearly and concisely, breaking down complex ideas.\n"
    prompt += "- Actively try to identify and address potential student misconceptions.\n"
    prompt += "- Encourage student questions and foster a curiosity-driven learning environment.\n"
    prompt += "- Maintain a supportive, patient, and encouraging tone.\n"
    prompt += "- Include pedagogical notes for AITA turns, explaining the teaching strategy in that turn.\n\n"


    if aita_profile:
        prompt += "AITA Profile (for context and tailoring):\n"
        prompt += f"- Subject: {aita_profile.get('subject', 'N/A')}\n"
        prompt += f"- Grade Level: {aita_profile.get('grade_level', 'N/A')}\n"
        prompt += f"- Jurisdiction: {aita_profile.get('jurisdiction', 'N/A')}\n"
        prompt += "The AITA should tailor its language, examples, and analogies to be appropriate and relatable for this student profile.\n\n"

    if raw_content_snippet:
        prompt += "Factual Basis (use this information to inform the dialogue):\n"
        prompt += f"\"\"\"\n{raw_content_snippet}\n\"\"\"\n\n"

    prompt += "Expected Output Format:\n"
    prompt += "Please provide the dialogue as a JSON list of turns, where each turn is an object with 'speaker' ('AITA' or 'student'), 'utterance' (the text spoken), and for AITA turns, a 'pedagogical_note' (explaining the teaching strategy for that specific turn). For example:\n"
    
    if example_dialogue_json:
        prompt += json.dumps(example_dialogue_json, indent=2) + "\n"
    else: # Default example if none provided
        prompt += """
[
  { "speaker": "student", "utterance": "I'm not sure I get how photosynthesis works." },
  { "speaker": "AITA", "utterance": "No problem! Let's break it down. What's your current understanding of what plants need to grow?", "pedagogical_note": "Starting with student's prior knowledge." }
  // ... more turns
]
"""
    prompt += "\nEnsure the dialogue flows naturally and effectively helps the student achieve the learning objective."
    return prompt

# --- Data Saving ---

def save_structured_data(structured_data: List[Dict[str, Any]], filename: str) -> None:
    """
    Saves a list of structured AITA JSON dictionaries to a file.

    Args:
        structured_data: A list of AITA JSON objects.
        filename: The name of the file to save the data to.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(structured_data, f, indent=4)
        print(f"Successfully saved structured data to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

# --- Main Execution Block ---

if __name__ == "__main__":
    print("--- Loading Simulated Raw Data ---")
    raw_data = load_simulated_raw_data()
    print(f"Loaded {len(raw_data)} raw items.")
    if raw_data:
        print("First raw item:", raw_data[0])
    print("-" * 30)

    print("\n--- Transforming Raw Data to AITA Format ---")
    transformed_items = []

    # Example 1: Photosynthesis
    photo_profile = {
        "subject": "Science",
        "grade_level": "7",
        "jurisdiction": "General",
        "learning_objective_id": "SCI.7.PS.1",
        "learning_objective_text": "Explain the inputs, outputs, and basic process of photosynthesis."
    }
    if raw_data:
        photo_aita_item = transform_raw_to_aita_format(raw_data[0], photo_profile)
        transformed_items.append(photo_aita_item)
        print("\nTransformed Photosynthesis Item (AITA Format):")
        print(json.dumps(photo_aita_item, indent=2))

    # Example 2: Fractions
    math_profile = {
        "subject": "Mathematics",
        "grade_level": "5",
        "jurisdiction": "US Common Core",
        "learning_objective_id": "CCSS.MATH.CONTENT.5.NF.A.1",
        "learning_objective_text": "Add and subtract fractions with unlike denominators (including mixed numbers) by replacing given fractions with equivalent fractions in such a way as to produce an equivalent sum or difference of fractions with like denominators."
    }
    if len(raw_data) > 1:
        frac_aita_item = transform_raw_to_aita_format(raw_data[1], math_profile, interaction_type="step_by_step_explanation")
        transformed_items.append(frac_aita_item)
        print("\nTransformed Fractions Item (AITA Format):")
        print(json.dumps(frac_aita_item, indent=2))
    print("-" * 30)

    print("\n--- Preparing LLM Augmentation Prompt ---")
    sample_learning_objective_hist = "Explain why 'taxation without representation' was a major grievance for American colonists, suitable for an 8th grader."
    sample_raw_snippet_hist = raw_data[2]["raw_text"] if len(raw_data) > 2 else None
    history_profile = {
        "subject": "History",
        "grade_level": "8",
        "jurisdiction": "US History Standards",
        "learning_objective_id": "USH.8.RR.1"
    }
    
    # Example dialogue for the LLM prompt
    example_dialogue_for_prompt = [
        {"speaker": "student", "utterance": "What does 'taxation without representation' mean?"},
        {"speaker": "AITA", "utterance": "That's a great question! It's a key idea from the American Revolution. To start, what do you think 'representation' means in the context of a government?", "pedagogical_note": "Guiding student to define a core concept first."}
    ]

    llm_prompt = prepare_llm_augmentation_prompt(
        learning_objective=sample_learning_objective_hist,
        raw_content_snippet=sample_raw_snippet_hist,
        aita_profile=history_profile,
        example_dialogue_json=example_dialogue_for_prompt
    )
    print("\nGenerated LLM Augmentation Prompt:")
    print(llm_prompt)
    print("-" * 30)

    print("\n--- Saving Structured Data ---")
    if transformed_items:
        save_structured_data(transformed_items, "initial_structured_aita_data.json")
    else:
        print("No transformed items to save.")
    print("-" * 30)

    print("\nScript execution finished.")


# --- 4th Grade Reading Comprehension Sample Generation ---

# Define Sample Passages (globally or passed into the function)
DEFAULT_4TH_GRADE_PASSAGES = [
    {
        "id": "passage_kitten_001",
        "text": "Lily the little kitten was lost. She wandered through tall grass and over a bumpy road. Finally, she saw her cozy red house and ran to the door, purring loudly."
    },
    {
        "id": "passage_leaves_001",
        "text": "In autumn, many leaves change from green to bright red, yellow, and orange. This happens because trees stop making chlorophyll, the green pigment. The other colors, which were always there, can finally show through."
    }
]

def generate_4th_grade_reading_comprehension_sample_dialogues(
    aita_profile: Dict[str, Any],
    passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Generates a list of sample AITA JSON dialogues for 4th-grade reading comprehension.
    Focuses on LO1: Main Idea and LO2: Making Inferences.
    """
    sample_dialogues = []
    creation_date = "2024-07-30" # Example date

    # --- Dialogues for Passage 1: Lost Kitten ---
    passage1 = next(p for p in passages if p["id"] == "passage_kitten_001")

    # LO1: Main Idea - Kitten
    dialogue_kitten_lo1 = {
        "aita_id": "aita_reading_kitten_lo1_main_idea_001",
        "version": "1.0",
        "metadata": {
            "source_content_id": passage1["id"],
            "interaction_type": "reading_comprehension_lo1_main_idea",
            "creation_date": creation_date,
            "last_modified_date": creation_date,
            "tags": ["reading comprehension", "4th grade", "main idea", "kitten"],
            "learning_objective_id": aita_profile.get("learning_objective_id_lo1", "RC.4.LO1"),
            "learning_objective_text": aita_profile.get("learning_objective_text_lo1", "Identify the main idea of a short passage.")
        },
        "aita_profile": aita_profile,
        "context": {
            "topic": "Finding the main idea of a story about a lost kitten.",
            "passage_id": passage1["id"],
            "passage_text": passage1["text"],
            "keywords": ["main idea", "kitten", "lost", "home"],
            "potential_grade_level": "4"
        },
        "dialogue": [
            {"speaker": "AITA", "utterance": f"Let's read this short story together:\n\n\"{passage1['text']}\"\n\nWhat do you think this story is mostly about?", "pedagogical_note": "Presenting the passage and asking an open-ended question to elicit initial thoughts on the main idea."},
            {"speaker": "student", "utterance": "It's about a kitten walking around."},
            {"speaker": "AITA", "utterance": "That's true, the kitten does walk around! But if you had to tell a friend what the whole story was about in just one sentence, what would be the most important part to include?", "pedagogical_note": "Acknowledging student's response and prompting for a more concise and central theme. Using the 'tell a friend' heuristic."},
            {"speaker": "student", "utterance": "That Lily the kitten was lost but found her home!"},
            {"speaker": "AITA", "utterance": "Exactly! That's a great way to say the main idea. The story is mostly about a lost kitten finding its way home. Well done!", "pedagogical_note": "Confirming the student's correct identification of the main idea and providing positive reinforcement."}
        ],
        "pedagogical_notes": [{"note_id": "overall_1", "text": "This dialogue aims to guide the student to identify the main idea by asking for a summary of the most important information."}],
        "evaluation_metrics": {}
    }
    sample_dialogues.append(dialogue_kitten_lo1)

    # LO2: Making Inferences - Kitten
    dialogue_kitten_lo2 = {
        "aita_id": "aita_reading_kitten_lo2_inference_001",
        "version": "1.0",
        "metadata": {
            "source_content_id": passage1["id"],
            "interaction_type": "reading_comprehension_lo2_inference",
            "creation_date": creation_date,
            "last_modified_date": creation_date,
            "tags": ["reading comprehension", "4th grade", "inference", "kitten", "feelings"],
            "learning_objective_id": aita_profile.get("learning_objective_id_lo2", "RC.4.LO2"),
            "learning_objective_text": aita_profile.get("learning_objective_text_lo2", "Make simple inferences based on textual clues.")
        },
        "aita_profile": aita_profile,
        "context": {
            "topic": "Making inferences about a character's feelings.",
            "passage_id": passage1["id"],
            "passage_text": passage1["text"],
            "keywords": ["inference", "feelings", "kitten", "lost", "home", "purring"],
            "potential_grade_level": "4"
        },
        "dialogue": [
            {"speaker": "AITA", "utterance": f"We just read the story about Lily:\n\n\"{passage1['text']}\"\n\nHow do you think Lily the kitten felt when she was lost? The story doesn't tell us directly.", "pedagogical_note": "Presenting the passage and posing an inferential question about character emotions not explicitly stated."},
            {"speaker": "student", "utterance": "Maybe scared? Or sad?"},
            {"speaker": "AITA", "utterance": "Those are good ideas! What words or clues in the story make you think she might have felt scared or sad when she was lost?", "pedagogical_note": "Validating student's initial inference and prompting for textual evidence to support it."},
            {"speaker": "student", "utterance": "Because she 'wandered through tall grass and over a bumpy road.' That sounds a bit scary to be alone."},
            {"speaker": "AITA", "utterance": "That's excellent thinking! You used clues from the story to imagine how she felt. And how do you think she felt when she saw her cozy red house?", "pedagogical_note": "Praising the use of textual evidence and asking another inferential question about a contrasting emotion."},
            {"speaker": "student", "utterance": "Happy and safe! Because she 'ran to the door, purring loudly.' Cats purr when they're happy."},
            {"speaker": "AITA", "utterance": "Wonderful! You're using clues from the story like 'cozy red house' and 'purring loudly' to understand her feelings. That's exactly how we make inferences!", "pedagogical_note": "Reinforcing the concept of using textual clues for inference and confirming student's understanding."}
        ],
        "pedagogical_notes": [{"note_id": "overall_1", "text": "This dialogue guides the student to make inferences about a character's feelings by using textual clues and prior knowledge."}],
        "evaluation_metrics": {}
    }
    sample_dialogues.append(dialogue_kitten_lo2)

    # --- Dialogues for Passage 2: Leaves ---
    passage2 = next(p for p in passages if p["id"] == "passage_leaves_001")

    # LO1: Main Idea - Leaves
    dialogue_leaves_lo1 = {
        "aita_id": "aita_reading_leaves_lo1_main_idea_001",
        "version": "1.0",
        "metadata": {
            "source_content_id": passage2["id"],
            "interaction_type": "reading_comprehension_lo1_main_idea",
            "creation_date": creation_date,
            "last_modified_date": creation_date,
            "tags": ["reading comprehension", "4th grade", "main idea", "leaves", "autumn"],
            "learning_objective_id": aita_profile.get("learning_objective_id_lo1", "RC.4.LO1"),
            "learning_objective_text": aita_profile.get("learning_objective_text_lo1", "Identify the main idea of a short passage.")
        },
        "aita_profile": aita_profile,
        "context": {
            "topic": "Finding the main idea of an informational text about leaves.",
            "passage_id": passage2["id"],
            "passage_text": passage2["text"],
            "keywords": ["main idea", "leaves", "autumn", "colors", "chlorophyll"],
            "potential_grade_level": "4"
        },
        "dialogue": [
            {"speaker": "AITA", "utterance": f"Here's a short text about leaves:\n\n\"{passage2['text']}\"\n\nWhat is this text mostly trying to explain to us?", "pedagogical_note": "Presenting the passage and asking an open-ended question about the main purpose/explanation."},
            {"speaker": "student", "utterance": "It's about leaves changing colors."},
            {"speaker": "AITA", "utterance": "That's right! Can you tell me in one sentence what the most important thing the text says about why they change color?", "pedagogical_note": "Confirming the topic and asking for the core explanation, guiding towards the main idea."},
            {"speaker": "student", "utterance": "They change color because trees stop making the green stuff, so other colors show."},
            {"speaker": "AITA", "utterance": "Perfect! The main idea is that leaves change color in autumn because trees stop making green chlorophyll, which lets other hidden colors appear. You got it!", "pedagogical_note": "Affirming the student's grasp of the main idea and providing positive feedback."}
        ],
        "pedagogical_notes": [{"note_id": "overall_1", "text": "This dialogue helps the student identify the main idea of an informational text by focusing on the core explanation provided."}],
        "evaluation_metrics": {}
    }
    sample_dialogues.append(dialogue_leaves_lo1)
    
    # LO2: Making Inferences - Leaves (Analogy/CFU style)
    dialogue_leaves_lo2_analogy = {
        "aita_id": "aita_reading_leaves_lo2_inference_analogy_001",
        "version": "1.0",
        "metadata": {
            "source_content_id": passage2["id"],
            "interaction_type": "reading_comprehension_lo2_inference_analogy",
            "creation_date": creation_date,
            "last_modified_date": creation_date,
            "tags": ["reading comprehension", "4th grade", "inference", "leaves", "analogy"],
            "learning_objective_id": aita_profile.get("learning_objective_id_lo2", "RC.4.LO2"),
            "learning_objective_text": aita_profile.get("learning_objective_text_lo2", "Make simple inferences based on textual clues.")
        },
        "aita_profile": aita_profile,
        "context": {
            "topic": "Making inferences about leaves using an analogy.",
            "passage_id": passage2["id"],
            "passage_text": passage2["text"],
            "keywords": ["inference", "leaves", "colors", "chlorophyll", "analogy"],
            "potential_grade_level": "4"
        },
        "dialogue": [
            {"speaker": "AITA", "utterance": f"We read that leaves have colors that show through when the green chlorophyll goes away:\n\n\"{passage2['text']}\"\n\nImagine you have a piece of yellow paper, and you color over it completely with a green crayon. What color does it look like?", "pedagogical_note": "Setting up an analogy to help understand the concept of underlying colors being revealed."},
            {"speaker": "student", "utterance": "It looks green."},
            {"speaker": "AITA", "utterance": "Exactly! Now, what happens if you start to erase the green crayon? What might you see?", "pedagogical_note": "Continuing the analogy to illustrate the 'disappearance' of the dominant color."},
            {"speaker": "student", "utterance": "The yellow paper underneath!"},
            {"speaker": "AITA", "utterance": "That's a great way to think about it! So, the text says the other colors 'were always there.' How is that like our green crayon and yellow paper example?", "pedagogical_note": "Connecting the analogy back to the text and prompting the student to make the inferential link."},
            {"speaker": "student", "utterance": "The red and orange are like the yellow paper, hidden under the green chlorophyll crayon!"},
            {"speaker": "AITA", "utterance": "Precisely! So, the text doesn't say the red and orange colors are *new*, but that they were hidden. You used the idea of the crayon to understand that. That's making an inference based on what the text says and what you already know!", "pedagogical_note": "Confirming the student's understanding of the inference and the analogy, and explicitly naming the skill used."}
        ],
        "pedagogical_notes": [{"note_id": "overall_1", "text": "This dialogue uses an analogy to help the student infer that the non-green colors in leaves are not new but are revealed when chlorophyll fades."}],
        "evaluation_metrics": {}
    }
    sample_dialogues.append(dialogue_leaves_lo2_analogy)

    return sample_dialogues

# --- Main Execution Block ---
