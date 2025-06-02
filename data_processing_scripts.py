import json
from typing import List, Dict, Any, Optional
import datetime # For timestamps
import os # For path checking in main for dummy data

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

# --- Sample Passages ---
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

DEFAULT_7TH_GRADE_SCIENCE_PASSAGES = [
    {
        "id": "eco_passage_foodweb_001",
        "title": "Forest Food Web",
        "text": "In a forest ecosystem, energy flows from one organism to another. It starts with the sun, which provides energy for oak trees (producers) to make their own food through photosynthesis. Caterpillars (primary consumers) eat the oak leaves. Then, a blue jay (secondary consumer) might eat the caterpillar. A hawk (tertiary consumer) could then hunt the blue jay. When these organisms die, decomposers like mushrooms break them down, returning nutrients to the soil, which helps the oak tree grow."
    },
    {
        "id": "eco_passage_biotic_abiotic_001",
        "title": "Pond Life",
        "text": "A pond is teeming with life. Fish, frogs, and tiny water plants are all living things, or biotic factors, that interact with each other. The pond also has many non-living, or abiotic factors, such as the water itself, sunlight that warms the pond, rocks that provide shelter, and the oxygen dissolved in the water that fish breathe."
    },
    {
        "id": "eco_passage_human_impact_001",
        "title": "Protecting Our Rivers",
        "text": "Rivers are important ecosystems that can be harmed by human activities like pollution from factories or trash. However, humans can also have a positive impact. Planting trees along riverbanks helps prevent soil erosion and keeps the water clean. Cleaning up litter and reducing chemical runoff also helps protect the animals and plants that live in the river."
    }
]

# --- Learning Objective Definitions ---
LO_TEXTS = {
    "MainIdea": "Identify the main idea of a short passage by recognizing key characters/events, the problem, and the resolution.",
    "Inference": "Make simple inferences about characters' feelings, motivations, or events based on textual clues and background knowledge.",
    "Vocabulary": "Determine the meaning of an unknown word or phrase using context clues within the passage.",
    "EcoFoodWeb": "Explain energy flow in a food web, identifying producers, consumers (primary, secondary, tertiary), and decomposers.",
    "EcoBioticAbiotic": "Differentiate between biotic and abiotic factors in an ecosystem and provide examples for each from a given scenario.",
    "EcoHumanImpact": "Describe one way humans can positively or negatively impact an ecosystem, providing an example."
}

# --- DialogueContext Helper Class ---
class DialogueContext:
    def __init__(self, dialogue_base_id: str, start_time_str: str = "2024-07-31T10:00:00Z"):
        self.dialogue_base_id = dialogue_base_id
        self.turn_counter = 0
        if start_time_str.endswith('Z'):
            start_time_str = start_time_str[:-1] + "+00:00"
        self.current_time = datetime.datetime.fromisoformat(start_time_str)

    def next_turn_id(self) -> str:
        self.turn_counter += 1
        return f"{self.dialogue_base_id}_turn_{self.turn_counter}"

    def get_timestamp(self, increment_seconds: int = 5) -> str:
        if self.turn_counter > 1 or increment_seconds > 0 :
             self.current_time += datetime.timedelta(seconds=increment_seconds)
        return self.current_time.isoformat() + "Z"
        
    def get_total_duration(self, initial_timestamp_str: str) -> int:
        if initial_timestamp_str.endswith('Z'):
            initial_timestamp_str = initial_timestamp_str[:-1] + "+00:00"
        initial_time = datetime.datetime.fromisoformat(initial_timestamp_str)
        return int((self.current_time - initial_time).total_seconds())

# --- Core Dialogue Generation Logic (Shared Base) ---
def _create_base_aita_json(
    dialogue_ctx: DialogueContext, passage: Dict[str, str], aita_profile: Dict[str, Any],
    lo_id_code: str, lo_text: str, interaction_type: str, additional_tags: List[str],
    expected_student_thinking: str, keywords: List[str], dataset_version_suffix: str = "Pilot"
) -> Dict[str, Any]:
    initial_timestamp = dialogue_ctx.get_timestamp(0)
    grade_level_tag = str(aita_profile.get("grade_level", "unknown_grade"))
    subject_tag = aita_profile.get("subject", "unknown_subject").lower().replace(" ", "_")
    dialogue_version = f"1.4_enhanced_iter1_{dataset_version_suffix.lower()}" # Iteration version bump

    return {
        "dialogue_id": dialogue_ctx.dialogue_base_id, "version": dialogue_version,
        "creation_timestamp_utc": initial_timestamp, "last_updated_timestamp_utc": initial_timestamp, 
        "metadata": {
            "original_source_content_id": passage["id"],
            "original_source_dataset": f"DEFAULT_{grade_level_tag}TH_GRADE_{subject_tag.upper()}_PASSAGES",
            "tags": [subject_tag, f"{grade_level_tag}th_grade", "gold_standard", dataset_version_suffix.lower()] + additional_tags,
            "tool_source": f"generate_dialogues_v4_iter1_{dataset_version_suffix.lower()}"
        },
        "aita_profile": aita_profile,
        "pedagogical_intent": {
            "interaction_type": interaction_type,
            "learning_objectives": [{"id": f"{subject_tag.upper()}.{grade_level_tag}.LO.{lo_id_code}", "text": lo_text}],
            "expected_student_thinking_process": expected_student_thinking,
            "keywords": keywords, "difficulty_level": f"{grade_level_tag}th_grade_on_level"
        },
        "context_provided_to_aita": {
            "user_id": f"student_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "session_id": f"session_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "prior_knowledge_level": "unknown", "prior_performance_summary": "N/A for this pilot dataset.",
            "learning_context_description": f"Student is working on a {grade_level_tag}th-grade {subject_tag} task focusing on {lo_id_code}.",
            "content_item_id": passage["id"], "content_item_title": passage["title"],
            "content_item_text": passage["text"], "potential_grade_level_of_content": grade_level_tag
        },
        "dialogue_turns": [],
        "final_assessment_of_student_understanding": {
            "summary_of_understanding": "Placeholder: Assessment to be filled based on interaction.",
            "mastery_level_per_lo": [{"lo_id": f"{subject_tag.upper()}.{grade_level_tag}.LO.{lo_id_code}", "level": "not_assessed"}],
            "next_steps_recommendation": "Placeholder: Suggest next steps."
        },
        "session_metadata_for_teacher_oversight": {
            "session_duration_seconds": 0, "engagement_metrics": {"total_turns": 0, "student_turns": 0, "aita_turns": 0},
            "flags_for_teacher_review": [], "session_summary_notes": f"Pilot dataset gold standard example for {subject_tag}."
        }
    }

# --- 4th Grade Reading Comprehension Dialogue Generation ---
def _create_main_idea_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "MainIdea", LO_TEXTS["MainIdea"],
        f"guided_discovery_main_idea_{passage['id'].split('_')[-1]}", ["main_idea", passage['id'].split('_')[-1]],
        "Student should identify key elements and synthesize them.", ["main idea", "summary"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"Hi! Let's read '{passage['title']}'.\n\n\"{passage['text']}\"\n\nWhat is this story mostly about?",
         "pedagogical_notes": "Greet, present passage, open-ended main idea question."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "A kitten got lost."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "True! And what happened at the end?", "pedagogical_notes": "Acknowledge, prompt for resolution."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "She found home."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Great! So, the main idea is: A lost kitten finds her way home. Well done!", "pedagogical_notes": "Synthesize and confirm."}
    ]
    return dialogue_json

def _create_inference_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    is_kitten = passage['id'] == "passage_kitten_001"
    q = "Why did Lily feel scared when the sun set?" if is_kitten else "Why were the other colors hidden before autumn?"
    a = "It was getting dark and she was alone." if is_kitten else "The green chlorophyll was too strong."
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Inference", LO_TEXTS["Inference"],
        f"guided_inference_{passage['id'].split('_')[-1]}", ["inference", passage['id'].split('_')[-1]],
        "Student uses clues to understand unstated info.", ["inference", "clues"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": f"Let's think about '{passage['title']}'. {q}",
         "pedagogical_notes": "Prompt for inference."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": a},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Good thinking! You used clues to figure that out. That's making an inference!", "pedagogical_notes": "Validate and explain inference."}
    ]
    return dialogue_json

def _create_vocab_dialogue_4th_refined(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext, target_word: str, definition: str) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Vocabulary", LO_TEXTS["Vocabulary"],
        f"contextual_vocab_refined_{target_word}_{passage['id'].split('_')[-1]}", ["vocabulary", target_word],
        "Student infers word meaning from context, with direct explanation if needed.", ["vocabulary", target_word] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"In '{passage['title']}', it says: \"{passage['text']}\" What do you think '{target_word}' means here?", 
         "pedagogical_notes": "Present word in full context, initial prompt for meaning."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Hmm, I'm not sure."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Okay, let's look at the clues. Lily saw her 'cozy' red house and ran to it purring. How do you think she felt about her house?", 
         "pedagogical_notes": "Second attempt: Prompt for contextual clues related to emotion/situation."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Happy and safe?"},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"Exactly! So if her house made her feel happy and safe, what might '{target_word}' mean? Does it sound like a good feeling?",
         "pedagogical_notes": "Third attempt: Connect feeling to word meaning, guide towards positive connotation."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "I still don't know for sure."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"No problem! '{target_word.capitalize()}' means {definition}. Now that you know the definition, can you make a new sentence using the word '{target_word}'?", 
         "pedagogical_notes": "Student still unsure after 3 prompts. Provide direct definition. Ask for application in new sentence."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": f"My bed is very {target_word} with all my blankets."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "That's a perfect way to use it! Well done!", "pedagogical_notes": "Confirm correct application, positive reinforcement."}
    ]
    return dialogue_json

def _create_frustration_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "MainIdea", LO_TEXTS["MainIdea"], # Reusing MainIdea LO for this example
        f"frustration_handling_main_idea_{passage['id'].split('_')[-1]}", ["frustration_handling", "main_idea", passage['id'].split('_')[-1]],
        "AITA responds empathetically to student frustration and re-scaffolds the task.",
        ["main idea", "emotion_regulation", "scaffolding_adjustment"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"Let's read '{passage['title']}' again: \"{passage['text']}\" What's the most important message the story is trying to tell us about Lily?",
         "pedagogical_notes": "Open-ended, slightly complex question about main message/theme."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "I don't know. It's just about a cat."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "It is about a cat named Lily, that's right! What big thing happens to Lily in the story? Is she happy all the time, or does something challenge her?",
         "pedagogical_notes": "Acknowledge and simplify, focusing on problem/challenge as a step to main idea."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Ugh, this is too confusing! I give up!"},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "I understand this can feel a bit tricky sometimes! No worries at all, we can take it step by step. How about we just look at the first part where Lily is lost? What clues tell us how she might be feeling then?",
         "pedagogical_notes": "Acknowledge student's feeling (empathy). Re-scaffold by breaking down the problem and shifting focus to a smaller, more concrete sub-question (inference about feelings)."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Well, it says she felt scared when the sun set."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "Great job finding that detail! That's an important clue. We can build on that. Thanks for sticking with it!",
         "pedagogical_notes": "Positive reinforcement for re-engagement. Prepare to continue with simpler steps."}
    ]
    return dialogue_json

def generate_4th_grade_reading_comprehension_sample_dialogues(
    aita_profile: Dict[str, Any], passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)
    for i, passage in enumerate(passages):
        passage_start_time_str = (start_time_base + datetime.timedelta(minutes=i*40)).isoformat() + "Z" # Increased spacing for more turns
        
        # Main Idea
        main_idea_ctx = DialogueContext(f"gold_std_{passage['id']}_main_idea_iter1_001", passage_start_time_str)
        dialogue_main_idea = _create_main_idea_dialogue_4th(passage, aita_profile, main_idea_ctx)
        dialogue_main_idea["last_updated_timestamp_utc"] = main_idea_ctx.get_timestamp(0)
        dialogue_main_idea["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = main_idea_ctx.get_total_duration(dialogue_main_idea["creation_timestamp_utc"])
        dialogue_main_idea["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": main_idea_ctx.turn_counter, "student_turns": main_idea_ctx.turn_counter // 2, "aita_turns": (main_idea_ctx.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_main_idea)

        # Inference
        inference_ctx = DialogueContext(f"gold_std_{passage['id']}_inference_iter1_001", passage_start_time_str) # Can reuse start time if conceptual sessions
        dialogue_inference = _create_inference_dialogue_4th(passage, aita_profile, inference_ctx)
        dialogue_inference["last_updated_timestamp_utc"] = inference_ctx.get_timestamp(0)
        dialogue_inference["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = inference_ctx.get_total_duration(dialogue_inference["creation_timestamp_utc"])
        dialogue_inference["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": inference_ctx.turn_counter, "student_turns": inference_ctx.turn_counter // 2, "aita_turns": (inference_ctx.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_inference)
        
        # Refined Vocabulary
        vocab_ctx = DialogueContext(f"gold_std_{passage['id']}_vocab_iter1_001", passage_start_time_str)
        if passage['id'] == "passage_kitten_001":
            dialogue_vocab = _create_vocab_dialogue_4th_refined(passage, aita_profile, vocab_ctx, "cozy", "comfortable, warm, and safe, making one feel relaxed.")
        elif passage['id'] == "passage_leaves_001":
            dialogue_vocab = _create_vocab_dialogue_4th_refined(passage, aita_profile, vocab_ctx, "pigment", "a natural substance that gives color to something, like plants or skin.")
        else: continue # Skip if no target word defined for other passages
        dialogue_vocab["last_updated_timestamp_utc"] = vocab_ctx.get_timestamp(0)
        dialogue_vocab["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = vocab_ctx.get_total_duration(dialogue_vocab["creation_timestamp_utc"])
        dialogue_vocab["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": vocab_ctx.turn_counter, "student_turns": vocab_ctx.turn_counter // 2, "aita_turns": (vocab_ctx.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_vocab)

    # Add one Frustration Handling example for the kitten passage
    passage_kitten = next((p for p in passages if p["id"] == "passage_kitten_001"), None)
    if passage_kitten:
        frustration_ctx = DialogueContext("gold_std_passage_kitten_001_frustration_iter1_001", (start_time_base + datetime.timedelta(minutes=len(passages)*40)).isoformat() + "Z")
        dialogue_frustration = _create_frustration_dialogue_4th(passage_kitten, aita_profile, frustration_ctx)
        dialogue_frustration["last_updated_timestamp_utc"] = frustration_ctx.get_timestamp(0)
        dialogue_frustration["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = frustration_ctx.get_total_duration(dialogue_frustration["creation_timestamp_utc"])
        dialogue_frustration["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": frustration_ctx.turn_counter, "student_turns": frustration_ctx.turn_counter // 2, "aita_turns": (frustration_ctx.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_frustration)
        
    return all_dialogues

# --- 7th Grade Science (Ecology) Dialogue Generation (Implementations from previous turn, ensure _create_base_aita_json is updated) ---
def _create_eco_foodweb_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoFoodWeb", LO_TEXTS["EcoFoodWeb"],
        f"guided_discovery_foodweb_{passage['id'].split('_')[-2]}", ["ecology", "food web"],
        "Student identifies organism roles and traces energy flow.", ["food web", "energy flow"],
        dataset_version_suffix="EcoIter1"
    )
    # Simplified turns for brevity, actual implementation would be more detailed
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"From '{passage['title']}', what does a producer like an oak tree do?", "pedagogical_notes": "Ask about producers."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "Makes food with sun."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Good! And a caterpillar is a primary consumer. Why?", "pedagogical_notes": "Ask about primary consumers."}
    ]
    return dialogue_json

def _create_eco_biotic_abiotic_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoBioticAbiotic", LO_TEXTS["EcoBioticAbiotic"],
        f"classification_biotic_abiotic_{passage['id'].split('_')[-2]}", ["ecology", "biotic", "abiotic"],
        "Student differentiates biotic and abiotic factors with examples.", ["biotic", "abiotic", "living"],
        dataset_version_suffix="EcoIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"'{passage['title']}' mentions fish as biotic. What makes something biotic?", "pedagogical_notes": "Define biotic."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "It's a living thing."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Correct! And sunlight is abiotic. What does abiotic mean?", "pedagogical_notes": "Define abiotic."}
    ]
    return dialogue_json

def _create_eco_human_impact_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoHumanImpact", LO_TEXTS["EcoHumanImpact"],
        f"explanation_human_impact_{passage['id'].split('_')[-2]}", ["ecology", "human impact"],
        "Student describes positive or negative human impact with examples.", ["human impact", "pollution"],
        dataset_version_suffix="EcoIter1"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"According to '{passage['title']}', how can humans negatively impact rivers?", "pedagogical_notes": "Ask for negative impact."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "Pollution from factories."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Good. And a positive impact?", "pedagogical_notes": "Ask for positive impact."}
    ]
    return dialogue_json

def generate_7th_grade_science_eco_sample_dialogues(
    aita_profile: Dict[str, Any], passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)
    passage_map = {p["id"]: p for p in passages}

    dialogue_configs = [
        ("eco_passage_foodweb_001", "EcoFoodWeb", _create_eco_foodweb_dialogue),
        ("eco_passage_biotic_abiotic_001", "EcoBioticAbiotic", _create_eco_biotic_abiotic_dialogue),
        ("eco_passage_human_impact_001", "EcoHumanImpact", _create_eco_human_impact_dialogue)
    ]

    for i, (passage_id, lo_key_suffix, creation_func) in enumerate(dialogue_configs):
        passage = passage_map.get(passage_id)
        if passage:
            dialogue_ctx = DialogueContext(f"gold_std_{passage_id}_{lo_key_suffix.lower()}_iter1_001", (start_time_base + datetime.timedelta(minutes=i*10)).isoformat() + "Z")
            dialogue = creation_func(passage, aita_profile, dialogue_ctx)
            dialogue["last_updated_timestamp_utc"] = dialogue_ctx.get_timestamp(0)
            dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx.get_total_duration(dialogue["creation_timestamp_utc"])
            dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx.turn_counter, "student_turns": dialogue_ctx.turn_counter // 2, "aita_turns": (dialogue_ctx.turn_counter + 1) // 2}
            all_dialogues.append(dialogue)
    return all_dialogues

# --- LLM Augmentation Prompt Generation (Placeholder) ---
def prepare_llm_augmentation_prompt(
    learning_objective_text: str, passage_text: Optional[str] = None, 
    aita_profile: Optional[Dict[str, Any]] = None, example_aita_json_structure: Optional[Dict[str, Any]] = None
) -> str:
    # (Implementation from previous turn, kept for script integrity)
    prompt = f"Objective: Generate a pedagogically sound dialogue based on the following learning objective: \"{learning_objective_text}\".\n" # ... (rest of the prompt generation)
    if passage_text: prompt += f"Use the following passage as context: \"{passage_text}\"\n"
    if aita_profile: prompt += f"AITA Profile: {json.dumps(aita_profile)}\n"
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

# --- Main Execution Block (Updated for Iteration 1 Changes) ---
if __name__ == "__main__":
    print("--- AITA Data Processing Script (Iteration 1 Changes) ---")

    # --- 4th Grade Reading Comprehension (with refined vocab and frustration handling) ---
    reading_aita_profile_iter1 = {
        "subject": "Reading Comprehension", "grade_level": "4",
        "jurisdiction": "US Common Core ELA Alignment (Simulated)", 
        "persona_name": "ReaderAITA_Explorer_v1.4_Iter1", # Version bump for persona
        "target_audience_description": "4th-grade students working on reading skills, with improved AITA adaptability."
    }
    print("\n--- Generating Iteration 1 Dataset for 4th Grade Reading Comprehension ---")
    # This will now include the refined vocabulary dialogues and the new frustration handling dialogue
    iter1_dialogues_reading = generate_4th_grade_reading_comprehension_sample_dialogues(
        aita_profile=reading_aita_profile_iter1, passages=DEFAULT_4TH_GRADE_PASSAGES
    )
    print(f"Generated {len(iter1_dialogues_reading)} Iteration 1 reading comprehension dialogues.")
    if iter1_dialogues_reading:
        # Save to a new file for this iteration to distinguish from previous pilot
        save_structured_data(iter1_dialogues_reading, "pilot_dataset_reading_compre_v1_iter1.json")
        
        # Print one of the new/refined dialogues for verification
        frustration_example = next((d for d in iter1_dialogues_reading if "frustration" in d["dialogue_id"]), None)
        if frustration_example:
            print("\nExample Frustration Handling Dialogue (Kitten - Main Idea Focus):")
            print(json.dumps(frustration_example, indent=2))
        else: # Fallback to printing first dialogue if specific one not found
            print("\nFirst dialogue from Iteration 1 Reading Comprehension set:")
            print(json.dumps(iter1_dialogues_reading[0], indent=2))

    print("-" * 30)

    # --- 7th Grade Science (Ecology) - Unchanged generation logic, but using updated base function ---
    eco_aita_profile_iter1 = { # Potentially update persona name if any base logic changed
        "subject": "Science", "grade_level": "7",
        "jurisdiction": "NGSS Alignment (Simulated)",
        "persona_name": "EcoExplorerAITA_v1.1_Iter1", # Slight version bump
        "target_audience_description": "7th-grade students (typically 12-13 years old) learning about ecology."
    }
    print("\n--- Generating Iteration 1 Dataset for 7th Grade Science (Ecology) ---")
    eco_dialogues_iter1 = generate_7th_grade_science_eco_sample_dialogues(
        aita_profile=eco_aita_profile_iter1, passages=DEFAULT_7TH_GRADE_SCIENCE_PASSAGES
    )
    print(f"Generated {len(eco_dialogues_iter1)} Iteration 1 ecology dialogues.")
    if eco_dialogues_iter1:
        save_structured_data(eco_dialogues_iter1, "eco_explorer_aita_sample_data_iter1.json")
    print("-" * 30)
    
    print("\nScript execution finished.")
