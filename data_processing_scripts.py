import json
from typing import List, Dict, Any, Optional
import datetime # For timestamps

# --- Data Simulation (Legacy - kept for reference or other potential uses) ---
def load_simulated_raw_data() -> List[Dict[str, Any]]:
    """
    Returns a predefined list of dictionaries simulating raw educational content.
    This is legacy and not used for generating the gold standard enhanced AITA JSON.
    """
    simulated_raw_data = [
        {"id": "photo_001", "topic": "Basic Photosynthesis", "raw_text": "Photosynthesis is the process plants use to convert light energy into chemical energy...", "source_dataset": "simulated_oer", "potential_grade_level": "7"},
        {"id": "frac_001", "topic": "Adding Fractions", "raw_text": "To add 1/2 and 1/4, you first need to find a common denominator...", "source_dataset": "simulated_oer", "potential_grade_level": "5"},
        {"id": "hist_001", "topic": "American Revolution Causes", "raw_text": "One major cause of the American Revolution was 'taxation without representation'.", "source_dataset": "simulated_oer", "potential_grade_level": "8"}
    ]
    return simulated_raw_data

# --- Sample Passages for Reading Comprehension ---
DEFAULT_4TH_GRADE_PASSAGES = [
    {
        "id": "passage_kitten_001",
        "title": "Lily the Lost Kitten",
        "text": "Lily the little kitten was lost. She wandered through tall grass and over a bumpy road. The sun began to set, and Lily felt scared. Finally, she saw her cozy red house and ran to the door, purring loudly when her owner, Tom, opened it."
    },
    {
        "id": "passage_leaves_001",
        "title": "Why Leaves Change Color",
        "text": "In autumn, many leaves change from green to bright red, yellow, and orange. This happens because trees stop making chlorophyll, the green pigment that helps them make food in the summer. When chlorophyll fades, the other colors, which were always there but hidden by the strong green, can finally show through."
    }
]

# --- Learning Objective Definitions ---
LO_TEXTS = {
    "MainIdea": "Identify the main idea of a short passage by recognizing key characters/events, the problem, and the resolution.",
    "Inference": "Make simple inferences about characters' feelings, motivations, or events based on textual clues and background knowledge.",
    "Vocabulary": "Determine the meaning of an unknown word or phrase using context clues within the passage."
}

# --- DialogueContext Helper Class ---
class DialogueContext:
    def __init__(self, dialogue_base_id: str, start_time_str: str = "2024-07-31T10:00:00Z"):
        self.dialogue_base_id = dialogue_base_id
        self.turn_counter = 0
        # Ensure the input string is compatible with fromisoformat
        if start_time_str.endswith('Z'):
            start_time_str = start_time_str[:-1] + "+00:00"
        self.current_time = datetime.datetime.fromisoformat(start_time_str)

    def next_turn_id(self) -> str:
        self.turn_counter += 1
        return f"{self.dialogue_base_id}_turn_{self.turn_counter}"

    def get_timestamp(self, increment_seconds: int = 5) -> str:
        if self.turn_counter > 1 or increment_seconds > 0 : # Only increment if not the very first timestamp call
             self.current_time += datetime.timedelta(seconds=increment_seconds)
        return self.current_time.isoformat() + "Z"
        
    def get_total_duration(self, initial_timestamp_str: str) -> int:
        if initial_timestamp_str.endswith('Z'):
            initial_timestamp_str = initial_timestamp_str[:-1] + "+00:00"
        initial_time = datetime.datetime.fromisoformat(initial_timestamp_str)
        return int((self.current_time - initial_time).total_seconds())

# --- Core Dialogue Generation Logic ---

def _create_base_aita_json(
    dialogue_ctx: DialogueContext,
    passage: Dict[str, str],
    aita_profile: Dict[str, Any],
    lo_id_suffix: str,
    lo_text: str,
    interaction_type: str,
    additional_tags: List[str],
    expected_student_thinking: str,
    keywords: List[str]
) -> Dict[str, Any]:
    """Helper to create the base structure of an AITA JSON object."""
    initial_timestamp = dialogue_ctx.get_timestamp(0)
    return {
        "dialogue_id": dialogue_ctx.dialogue_base_id,
        "version": "1.3_pilot_dataset",
        "creation_timestamp_utc": initial_timestamp,
        "last_updated_timestamp_utc": initial_timestamp, # Will be updated later
        "metadata": {
            "original_source_content_id": passage["id"],
            "original_source_dataset": "DEFAULT_4TH_GRADE_PASSAGES_V2_Pilot",
            "tags": ["reading comprehension", "4th grade", "gold_standard", "pilot_dataset"] + additional_tags,
            "tool_source": "generate_4th_grade_rc_v3_pilot"
        },
        "aita_profile": aita_profile,
        "pedagogical_intent": {
            "interaction_type": interaction_type,
            "learning_objectives": [{"id": f"RC.4.LO.{lo_id_suffix}", "text": lo_text}],
            "expected_student_thinking_process": expected_student_thinking,
            "keywords": keywords,
            "difficulty_level": "4th_grade_on_level"
        },
        "context_provided_to_aita": {
            "user_id": f"student_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "session_id": f"session_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "prior_knowledge_level": "unknown",
            "prior_performance_summary": "N/A for this pilot dataset.",
            "learning_context_description": f"Student is working on a 4th-grade reading comprehension task focusing on {lo_id_suffix}.",
            "content_item_id": passage["id"],
            "content_item_title": passage["title"],
            "content_item_text": passage["text"],
            "potential_grade_level_of_content": "4"
        },
        "dialogue_turns": [], # To be populated by specific LO functions
        "final_assessment_of_student_understanding": {
            "summary_of_understanding": "Placeholder: Assessment to be filled based on interaction.",
            "mastery_level_per_lo": [{"lo_id": f"RC.4.LO.{lo_id_suffix}", "level": "not_assessed"}],
            "next_steps_recommendation": "Placeholder: Suggest next steps."
        },
        "session_metadata_for_teacher_oversight": {
            "session_duration_seconds": 0, # Will be updated
            "engagement_metrics": {"total_turns": 0, "student_turns": 0, "aita_turns": 0}, # Will be updated
            "flags_for_teacher_review": [],
            "session_summary_notes": "Pilot dataset gold standard example."
        }
    }

def _create_main_idea_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "MainIdea", LO_TEXTS["MainIdea"],
        f"guided_discovery_main_idea_{passage['id'].split('_')[-1]}",
        ["main_idea", passage['id'].split('_')[-1]],
        "Student should identify key elements (character, problem, resolution for narratives; key topic/details for informational) and synthesize them into a central theme.",
        ["main idea", "summary", "central theme", "story elements", "passage topic"] + passage.get("title", "").lower().split()
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"Hi! Let's read this passage titled '{passage['title']}'. Here it is:\n\n\"{passage['text']}\"\n\nWhat do you think this passage is mostly about?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Greet, present passage, ask open-ended question for main idea.",
         "safeguard_tags": ["safe", "on-topic"], "xapi_verb_id": "asked", "ontology_concept_tags": ["main_idea_elicitation"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "It's about Lily the kitten getting lost.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["partial_main_idea"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "That's a big part of it! What else happens after Lily gets lost? How does the story end for her?",
         "confidence_score_aita": 0.97, "pedagogical_notes": "Acknowledge and guide towards resolution for a complete main idea.",
         "safeguard_tags": ["safe", "scaffolding"], "xapi_verb_id": "asked", "ontology_concept_tags": ["scaffolding_question", "narrative_resolution"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "She finds her cozy home and purrs because Tom is there.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["identifies_resolution"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Exactly! So, if we put it all together: Lily was lost, but she found her home and was happy. That's the main idea! Well done!",
         "confidence_score_aita": 0.99, "pedagogical_notes": "Synthesize and confirm the main idea, positive reinforcement.",
         "safeguard_tags": ["safe", "positive_feedback"], "xapi_verb_id": "provided_feedback", "ontology_concept_tags": ["main_idea_synthesis", "confirmation"]}
    ]
    return dialogue_json

def _create_inference_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    is_kitten_passage = passage['id'] == "passage_kitten_001"
    inference_focus = "character_feelings" if is_kitten_passage else "causal_reasoning"
    utterance1_aita = f"Let's think about what the story *doesn't* say directly. In the story '{passage['title']}', it says Lily felt scared when the sun began to set. Why do you think she felt scared *then*?" if is_kitten_passage \
        else f"In the passage '{passage['title']}', it says the other colors were 'always there but hidden by the strong green.' Why do you think they were hidden before autumn?"
    utterance2_student = "Because it was getting dark and she was alone." if is_kitten_passage else "Because the green color from chlorophyll was so strong it covered them up."
    
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Inference", LO_TEXTS["Inference"],
        f"guided_discovery_inference_{inference_focus}_{passage['id'].split('_')[-1]}",
        ["inference", inference_focus, passage['id'].split('_')[-1]],
        "Student should use textual clues and background knowledge to understand unstated information like emotions or causal relationships.",
        ["inference", "textual clues", "reading between the lines", "emotions", "reasons"] + passage.get("title", "").lower().split()
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": utterance1_aita,
         "confidence_score_aita": 0.98, "pedagogical_notes": "Prompt for inference based on textual detail.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["inference_prompt", inference_focus]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": utterance2_student, 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_makes_inference"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "That's a very good thought! The story doesn't say that exactly, but you used clues from the story and what you know about the world to figure it out. That's called making an inference!",
         "confidence_score_aita": 0.99, "pedagogical_notes": "Validate inference, explain the concept of inferring.",
         "safeguard_tags": ["safe", "positive_feedback"], "xapi_verb_id": "provided_feedback", "ontology_concept_tags": ["inference_explanation", "metacognition_prompt"]}
    ]
    return dialogue_json

def _create_vocab_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext, target_word: str, student_guess: str) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Vocabulary", LO_TEXTS["Vocabulary"],
        f"contextual_vocabulary_{target_word}_{passage['id'].split('_')[-1]}",
        ["vocabulary", "context clues", target_word, passage['id'].split('_')[-1]],
        "Student should use surrounding text (context clues) to infer the meaning of an unfamiliar word, then confirm understanding.",
        ["vocabulary", "context clues", "word meaning", target_word] + passage.get("title", "").lower().split()
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"In the story '{passage['title']}', it says Lily saw her '{target_word}' red house. What do you think '{target_word}' might mean here, thinking about how Lily felt and what she found?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Present word in context, prompt for meaning using clues.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["vocabulary_in_context", "context_clue_prompt"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": student_guess, 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_infers_vocab_meaning"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"That's a great guess! '{target_word.capitalize()}' often means something like comfortable, warm, and safe. Does that fit with how Lily might feel about her house after being lost?",
         "confidence_score_aita": 0.97, "pedagogical_notes": "Affirm student's attempt, provide definition, and connect back to context for confirmation.",
         "safeguard_tags": ["safe", "positive_feedback"], "xapi_verb_id": "provided_feedback", "ontology_concept_tags": ["vocabulary_clarification", "contextual_reinforcement"]}
    ]
    return dialogue_json


def generate_4th_grade_reading_comprehension_sample_dialogues(
    aita_profile: Dict[str, Any],
    passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Generates 6 "gold standard" AITA JSON dialogues for 4th-grade reading comprehension,
    covering Main Idea, Inference, and Vocabulary for each of the two passages.
    """
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)

    for i, passage in enumerate(passages):
        # Ensure each dialogue starts at a slightly different time for realism if needed
        passage_start_time_str = (start_time_base + datetime.timedelta(minutes=i*30)).isoformat() + "Z"

        # Main Idea
        main_idea_ctx = DialogueContext(f"gold_std_{passage['id']}_main_idea_001", passage_start_time_str)
        main_idea_dialogue = _create_main_idea_dialogue(passage, aita_profile, main_idea_ctx)
        main_idea_dialogue["last_updated_timestamp_utc"] = main_idea_ctx.get_timestamp(0)
        main_idea_dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = main_idea_ctx.get_total_duration(main_idea_dialogue["creation_timestamp_utc"])
        main_idea_dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": main_idea_ctx.turn_counter, "student_turns": main_idea_ctx.turn_counter // 2, "aita_turns": (main_idea_ctx.turn_counter + 1) // 2}
        all_dialogues.append(main_idea_dialogue)

        # Inference
        inference_ctx = DialogueContext(f"gold_std_{passage['id']}_inference_001", passage_start_time_str)
        inference_dialogue = _create_inference_dialogue(passage, aita_profile, inference_ctx)
        inference_dialogue["last_updated_timestamp_utc"] = inference_ctx.get_timestamp(0)
        inference_dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = inference_ctx.get_total_duration(inference_dialogue["creation_timestamp_utc"])
        inference_dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": inference_ctx.turn_counter, "student_turns": inference_ctx.turn_counter // 2, "aita_turns": (inference_ctx.turn_counter + 1) // 2}
        all_dialogues.append(inference_dialogue)
        
        # Vocabulary
        vocab_ctx = DialogueContext(f"gold_std_{passage['id']}_vocab_001", passage_start_time_str)
        target_word = "cozy" if passage['id'] == "passage_kitten_001" else "pigment"
        student_guess = "Like, safe and warm?" if target_word == "cozy" else "Is it like a color?"
        vocab_dialogue = _create_vocab_dialogue(passage, aita_profile, vocab_ctx, target_word, student_guess)
        vocab_dialogue["last_updated_timestamp_utc"] = vocab_ctx.get_timestamp(0)
        vocab_dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = vocab_ctx.get_total_duration(vocab_dialogue["creation_timestamp_utc"])
        vocab_dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": vocab_ctx.turn_counter, "student_turns": vocab_ctx.turn_counter // 2, "aita_turns": (vocab_ctx.turn_counter + 1) // 2}
        all_dialogues.append(vocab_dialogue)
        
    return all_dialogues

# --- LLM Augmentation Prompt Generation (Placeholder - Not primary focus of this refactor) ---
def prepare_llm_augmentation_prompt(
    learning_objective_text: str,
    passage_text: Optional[str] = None, 
    aita_profile: Optional[Dict[str, Any]] = None,
    example_aita_json_structure: Optional[Dict[str, Any]] = None
) -> str:
    prompt = f"Objective: Generate a pedagogically sound dialogue based on the following learning objective: \"{learning_objective_text}\".\n"
    if passage_text:
        prompt += f"Use the following passage as context: \"{passage_text}\"\n"
    if aita_profile:
        prompt += f"AITA Profile: {json.dumps(aita_profile)}\n"
    prompt += "Format the output as a complete AITA JSON object. Here's a condensed example of the target structure (fill all fields thoughtfully):\n"
    if example_aita_json_structure:
        condensed_example = {
            "dialogue_id": "llm_gen_example_id",
            "pedagogical_intent": {"learning_objectives": [{"text": learning_objective_text}]},
            "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "...", "pedagogical_notes": "..."}],
            "final_assessment_of_student_understanding": {"summary_of_understanding": "..."}
        }
        prompt += json.dumps(condensed_example, indent=2) + "\n"
    prompt += "Please generate the full JSON including all relevant fields like metadata, context_provided_to_aita, detailed dialogue_turns with pedagogical_notes, xapi tags, ontology_concept_tags, etc."
    return prompt

# --- Data Saving ---
def save_structured_data(structured_data: List[Dict[str, Any]], filename: str) -> None:
    try:
        with open(filename, 'w') as f:
            json.dump(structured_data, f, indent=4)
        print(f"Successfully saved structured data to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

# --- Main Execution Block (Updated for Pilot Dataset Generation) ---
if __name__ == "__main__":
    print("--- AITA Data Processing Script (Pilot Dataset Generation) ---")

    reading_aita_profile_pilot = {
        "subject": "Reading Comprehension",
        "grade_level": "4",
        "jurisdiction": "US Common Core ELA Alignment (Simulated)", 
        "persona_name": "ReaderAITA_Explorer_v1.3_Pilot",
        "target_audience_description": "4th-grade students (typically 9-10 years old) working on foundational reading skills."
    }
    
    print("\n--- Generating Pilot Dataset for 4th Grade Reading Comprehension ---")
    pilot_dialogues = generate_4th_grade_reading_comprehension_sample_dialogues(
        aita_profile=reading_aita_profile_pilot, 
        passages=DEFAULT_4TH_GRADE_PASSAGES
    )
    print(f"Generated {len(pilot_dialogues)} pilot dataset dialogues.")
    
    if pilot_dialogues:
        print("\n--- Example Dialogues from Pilot Dataset ---")
        
        # Print one example for each LO type
        example_main_idea = next((d for d in pilot_dialogues if "main_idea" in d["dialogue_id"]), None)
        example_inference = next((d for d in pilot_dialogues if "inference" in d["dialogue_id"] and "leaves" in d["dialogue_id"]), None) # Inference from leaves
        example_vocab = next((d for d in pilot_dialogues if "vocab" in d["dialogue_id"] and "kitten" in d["dialogue_id"]), None) # Vocab from kitten

        if example_main_idea:
            print("\nExample Main Idea Dialogue (Kitten):")
            print(json.dumps(example_main_idea, indent=2))
        if example_inference:
            print("\nExample Inference Dialogue (Leaves):")
            print(json.dumps(example_inference, indent=2))
        if example_vocab:
            print("\nExample Vocabulary Dialogue (Kitten - 'cozy'):")
            print(json.dumps(example_vocab, indent=2))
        
        print("-" * 30)
        print("\n--- Saving Pilot Reading Comprehension Dataset ---")
        save_structured_data(pilot_dialogues, "pilot_dataset_reading_compre_v1.json")
    else:
        print("No pilot dialogues were generated.")
    print("-" * 30)
    
    print("\nScript execution finished.")
