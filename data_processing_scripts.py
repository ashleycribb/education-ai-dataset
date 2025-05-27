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
        "id": "eco_passage_human_impact_001", # For the third LO
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
    dialogue_ctx: DialogueContext,
    passage: Dict[str, str],
    aita_profile: Dict[str, Any],
    lo_id_code: str, # e.g., "MainIdea", "EcoFoodWeb"
    lo_text: str,
    interaction_type: str,
    additional_tags: List[str],
    expected_student_thinking: str,
    keywords: List[str],
    dataset_version_suffix: str = "Pilot" # e.g., "Pilot", "EcoPilot"
) -> Dict[str, Any]:
    initial_timestamp = dialogue_ctx.get_timestamp(0)
    grade_level_tag = aita_profile.get("grade_level", "unknown_grade")
    subject_tag = aita_profile.get("subject", "unknown_subject").lower().replace(" ", "_")

    return {
        "dialogue_id": dialogue_ctx.dialogue_base_id,
        "version": f"1.3_enhanced_gold_standard_{dataset_version_suffix.lower()}",
        "creation_timestamp_utc": initial_timestamp,
        "last_updated_timestamp_utc": initial_timestamp, 
        "metadata": {
            "original_source_content_id": passage["id"],
            "original_source_dataset": f"DEFAULT_{grade_level_tag}TH_GRADE_{subject_tag.upper()}_PASSAGES",
            "tags": [subject_tag, f"{grade_level_tag}th_grade", "gold_standard", dataset_version_suffix.lower()] + additional_tags,
            "tool_source": f"generate_dialogues_v3_{dataset_version_suffix.lower()}"
        },
        "aita_profile": aita_profile,
        "pedagogical_intent": {
            "interaction_type": interaction_type,
            "learning_objectives": [{"id": f"{subject_tag.upper()}.{grade_level_tag}.LO.{lo_id_code}", "text": lo_text}],
            "expected_student_thinking_process": expected_student_thinking,
            "keywords": keywords,
            "difficulty_level": f"{grade_level_tag}th_grade_on_level"
        },
        "context_provided_to_aita": {
            "user_id": f"student_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}", # e.g. student_pilot_eco_001
            "session_id": f"session_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "prior_knowledge_level": "unknown",
            "prior_performance_summary": "N/A for this pilot dataset.",
            "learning_context_description": f"Student is working on a {grade_level_tag}th-grade {subject_tag} task focusing on {lo_id_code}.",
            "content_item_id": passage["id"],
            "content_item_title": passage["title"],
            "content_item_text": passage["text"],
            "potential_grade_level_of_content": str(grade_level_tag)
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
    # (Implementation from previous step, slightly adapted to use new _create_base_aita_json structure)
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "MainIdea", LO_TEXTS["MainIdea"],
        f"guided_discovery_main_idea_{passage['id'].split('_')[-1]}",
        ["main_idea", passage['id'].split('_')[-1]],
        "Student should identify key elements (character, problem, resolution for narratives; key topic/details for informational) and synthesize them into a central theme.",
        ["main idea", "summary", "central theme", "story elements", "passage topic"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingComprePilot"
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

def _create_inference_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
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
        ["inference", "textual clues", "reading between the lines", "emotions", "reasons"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingComprePilot"
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

def _create_vocab_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext, target_word: str, student_guess: str) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Vocabulary", LO_TEXTS["Vocabulary"],
        f"contextual_vocabulary_{target_word}_{passage['id'].split('_')[-1]}",
        ["vocabulary", "context clues", target_word, passage['id'].split('_')[-1]],
        "Student should use surrounding text (context clues) to infer the meaning of an unfamiliar word, then confirm understanding.",
        ["vocabulary", "context clues", "word meaning", target_word] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingComprePilot"
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
    aita_profile: Dict[str, Any], passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)
    for i, passage in enumerate(passages):
        passage_start_time_str = (start_time_base + datetime.timedelta(minutes=i*30)).isoformat() + "Z"
        for lo_key, lo_text_val in [("MainIdea",LO_TEXTS["MainIdea"]), ("Inference",LO_TEXTS["Inference"]), ("Vocabulary",LO_TEXTS["Vocabulary"])]:
            dialogue_ctx = DialogueContext(f"gold_std_{passage['id']}_{lo_key.lower()}_001", passage_start_time_str)
            if lo_key == "MainIdea":
                dialogue = _create_main_idea_dialogue_4th(passage, aita_profile, dialogue_ctx)
            elif lo_key == "Inference":
                dialogue = _create_inference_dialogue_4th(passage, aita_profile, dialogue_ctx)
            elif lo_key == "Vocabulary":
                target_word = "cozy" if passage['id'] == "passage_kitten_001" else "pigment"
                student_guess = "Like, safe and warm?" if target_word == "cozy" else "Is it like a color?"
                dialogue = _create_vocab_dialogue_4th(passage, aita_profile, dialogue_ctx, target_word, student_guess)
            else: continue
            
            dialogue["last_updated_timestamp_utc"] = dialogue_ctx.get_timestamp(0)
            dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx.get_total_duration(dialogue["creation_timestamp_utc"])
            dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx.turn_counter, "student_turns": dialogue_ctx.turn_counter // 2, "aita_turns": (dialogue_ctx.turn_counter + 1) // 2}
            all_dialogues.append(dialogue)
    return all_dialogues

# --- 7th Grade Science (Ecology) Dialogue Generation ---
def _create_eco_foodweb_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoFoodWeb", LO_TEXTS["EcoFoodWeb"],
        f"guided_discovery_foodweb_{passage['id'].split('_')[-2]}", # e.g. foodweb_foodweb
        ["ecology", "food web", "producer", "consumer", "decomposer", passage['id'].split('_')[-2]],
        "Student should identify roles of organisms in the food web (producer, consumer types, decomposer) and trace energy flow.",
        ["food web", "energy flow", "producer", "consumer", "decomposer", "ecosystem", "photosynthesis"],
        dataset_version_suffix="EcoPilot"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"Let's explore the '{passage['title']}' passage:\n\n\"{passage['text']}\"\n\nThe passage mentions the oak tree is a producer. What does a producer do in a food web?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Present passage, then ask a targeted question about a key concept (producer) mentioned in the text.",
         "safeguard_tags": ["safe", "on-topic"], "xapi_verb_id": "asked", "ontology_concept_tags": ["food_web_producer_definition"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "It makes its own food using the sun.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_defines_producer"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Exactly! And where does the oak tree get its energy from? The passage mentions it.",
         "confidence_score_aita": 0.97, "pedagogical_notes": "Confirm understanding and ask for source of energy for producer, linking to text.",
         "safeguard_tags": ["safe", "scaffolding"], "xapi_verb_id": "asked", "ontology_concept_tags": ["energy_source_producer"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "From the sun!", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_identifies_sun"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Great! Now, what about the caterpillar? It's called a primary consumer. What does that mean based on what it eats?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Introduce new term (primary consumer) and ask student to infer meaning from context.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["primary_consumer_definition_inference"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "It eats the producer, the oak tree leaves.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_defines_primary_consumer"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Perfect! So energy flows from the sun to the oak tree, then to the caterpillar. Can you trace the energy to the hawk based on the passage?",
         "confidence_score_aita": 0.99, "pedagogical_notes": "Summarize energy flow so far and ask student to extend it based on the text.",
         "safeguard_tags": ["safe", "positive_feedback"], "xapi_verb_id": "asked", "ontology_concept_tags": ["energy_flow_tracing", "food_web_path"]}
    ]
    return dialogue_json

def _create_eco_biotic_abiotic_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoBioticAbiotic", LO_TEXTS["EcoBioticAbiotic"],
        f"classification_biotic_abiotic_{passage['id'].split('_')[-2]}",
        ["ecology", "biotic", "abiotic", "ecosystem factors", passage['id'].split('_')[-2]],
        "Student should correctly classify examples from the passage as biotic or abiotic and explain the difference.",
        ["biotic", "abiotic", "living", "non-living", "ecosystem components"],
        dataset_version_suffix="EcoPilot"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"Let's look at the '{passage['title']}' passage:\n\n\"{passage['text']}\"\n\nThe passage says fish and frogs are 'biotic factors'. What do you think 'biotic' means based on these examples?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Present passage and ask for definition of 'biotic' based on examples.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["biotic_definition_from_examples"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Living things?", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_infers_biotic"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "That's right! Biotic factors are all the living or once-living organisms in an ecosystem. Now, the passage mentions water and sunlight as 'abiotic factors'. What could 'abiotic' mean?",
         "confidence_score_aita": 0.97, "pedagogical_notes": "Confirm biotic, then introduce abiotic with examples and ask for definition.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["abiotic_definition_from_examples", "contrastive_learning"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Non-living things?", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_infers_abiotic"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Exactly! So, can you name one more biotic factor and one more abiotic factor from the pond description in the passage?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Confirm abiotic. Ask for additional examples from text to check understanding.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["example_identification_biotic_abiotic", "comprehension_check"]}
    ]
    return dialogue_json

def _create_eco_human_impact_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoHumanImpact", LO_TEXTS["EcoHumanImpact"],
        f"explanation_human_impact_{passage['id'].split('_')[-2]}",
        ["ecology", "human impact", "ecosystems", "pollution", "conservation", passage['id'].split('_')[-2]],
        "Student should describe a positive or negative human impact on an ecosystem using an example from the text.",
        ["human impact", "pollution", "conservation", "positive impact", "negative impact", "ecosystem health"],
        dataset_version_suffix="EcoPilot"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": f"We've been reading about ecosystems. Let's look at the '{passage['title']}' passage:\n\n\"{passage['text']}\"\n\nThis passage talks about how humans can affect rivers. Can you tell me one *negative* way humans can impact a river, based on the text?",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Present passage. Ask for a negative human impact example from the text.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["human_impact_negative_example_elicitation"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Pollution from factories or trash.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_identifies_negative_impact"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "That's a key one. Now, can you find an example in the passage of a *positive* way humans can help rivers?",
         "confidence_score_aita": 0.97, "pedagogical_notes": "Acknowledge correct answer. Ask for a positive human impact example from the text.",
         "safeguard_tags": ["safe"], "xapi_verb_id": "asked", "ontology_concept_tags": ["human_impact_positive_example_elicitation"]},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Planting trees along riverbanks or cleaning up litter.", 
         "safeguard_tags": ["safe"], "xapi_verb_id": "responded", "ontology_concept_tags": ["student_identifies_positive_impact"]},
         {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", 
         "utterance": "Excellent! So humans can both harm and help ecosystems. Understanding these impacts is important for protecting our environment.",
         "confidence_score_aita": 0.98, "pedagogical_notes": "Summarize and state the importance of understanding human impact.",
         "safeguard_tags": ["safe", "positive_feedback"], "xapi_verb_id": "provided_feedback", "ontology_concept_tags": ["summary_human_impact", "environmental_awareness"]}
    ]
    return dialogue_json


def generate_7th_grade_science_eco_sample_dialogues(
    aita_profile: Dict[str, Any], passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Generates 3-4 "gold standard" AITA JSON dialogues for 7th-grade science (ecology).
    """
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)

    # Food Web dialogue for passage 1
    passage_foodweb = next((p for p in passages if p["id"] == "eco_passage_foodweb_001"), None)
    if passage_foodweb:
        dialogue_ctx_fw = DialogueContext("gold_std_eco_foodweb_001", (start_time_base + datetime.timedelta(minutes=0)).isoformat() + "Z")
        dialogue_fw = _create_eco_foodweb_dialogue(passage_foodweb, aita_profile, dialogue_ctx_fw)
        dialogue_fw["last_updated_timestamp_utc"] = dialogue_ctx_fw.get_timestamp(0)
        dialogue_fw["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx_fw.get_total_duration(dialogue_fw["creation_timestamp_utc"])
        dialogue_fw["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx_fw.turn_counter, "student_turns": dialogue_ctx_fw.turn_counter // 2, "aita_turns": (dialogue_ctx_fw.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_fw)

    # Biotic/Abiotic dialogue for passage 2
    passage_biotic_abiotic = next((p for p in passages if p["id"] == "eco_passage_biotic_abiotic_001"), None)
    if passage_biotic_abiotic:
        dialogue_ctx_ba = DialogueContext("gold_std_eco_biotic_abiotic_001", (start_time_base + datetime.timedelta(minutes=10)).isoformat() + "Z")
        dialogue_ba = _create_eco_biotic_abiotic_dialogue(passage_biotic_abiotic, aita_profile, dialogue_ctx_ba)
        dialogue_ba["last_updated_timestamp_utc"] = dialogue_ctx_ba.get_timestamp(0)
        dialogue_ba["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx_ba.get_total_duration(dialogue_ba["creation_timestamp_utc"])
        dialogue_ba["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx_ba.turn_counter, "student_turns": dialogue_ctx_ba.turn_counter // 2, "aita_turns": (dialogue_ctx_ba.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_ba)
        
    # Human Impact dialogue for passage 3
    passage_human_impact = next((p for p in passages if p["id"] == "eco_passage_human_impact_001"), None)
    if passage_human_impact:
        dialogue_ctx_hi = DialogueContext("gold_std_eco_human_impact_001", (start_time_base + datetime.timedelta(minutes=20)).isoformat() + "Z")
        dialogue_hi = _create_eco_human_impact_dialogue(passage_human_impact, aita_profile, dialogue_ctx_hi)
        dialogue_hi["last_updated_timestamp_utc"] = dialogue_ctx_hi.get_timestamp(0)
        dialogue_hi["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx_hi.get_total_duration(dialogue_hi["creation_timestamp_utc"])
        dialogue_hi["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx_hi.turn_counter, "student_turns": dialogue_ctx_hi.turn_counter // 2, "aita_turns": (dialogue_ctx_hi.turn_counter + 1) // 2}
        all_dialogues.append(dialogue_hi)
        
    return all_dialogues


# --- LLM Augmentation Prompt Generation (Placeholder - Not primary focus of this refactor) ---
def prepare_llm_augmentation_prompt(
    learning_objective_text: str,
    passage_text: Optional[str] = None, 
    aita_profile: Optional[Dict[str, Any]] = None,
    example_aita_json_structure: Optional[Dict[str, Any]] = None
) -> str:
    # (Implementation from previous step, kept for script integrity but not the focus here)
    prompt = f"Objective: Generate a pedagogically sound dialogue based on the following learning objective: \"{learning_objective_text}\".\n"
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

# --- Main Execution Block (Updated for Pilot Dataset Generation) ---
if __name__ == "__main__":
    print("--- AITA Data Processing Script ---")

    # --- 4th Grade Reading Comprehension ---
    reading_aita_profile_pilot = {
        "subject": "Reading Comprehension", "grade_level": "4",
        "jurisdiction": "US Common Core ELA Alignment (Simulated)", 
        "persona_name": "ReaderAITA_Explorer_v1.3_Pilot",
        "target_audience_description": "4th-grade students (typically 9-10 years old) working on foundational reading skills."
    }
    print("\n--- Generating Pilot Dataset for 4th Grade Reading Comprehension ---")
    pilot_dialogues_reading = generate_4th_grade_reading_comprehension_sample_dialogues(
        aita_profile=reading_aita_profile_pilot, passages=DEFAULT_4TH_GRADE_PASSAGES
    )
    print(f"Generated {len(pilot_dialogues_reading)} pilot reading comprehension dialogues.")
    if pilot_dialogues_reading:
        save_structured_data(pilot_dialogues_reading, "pilot_dataset_reading_compre_v1.json")
    print("-" * 30)

    # --- 7th Grade Science (Ecology) ---
    eco_aita_profile = {
        "subject": "Science", "grade_level": "7",
        "jurisdiction": "NGSS Alignment (Simulated)",
        "persona_name": "EcoExplorerAITA_v1.0",
        "target_audience_description": "7th-grade students (typically 12-13 years old) learning about ecology."
    }
    print("\n--- Generating Sample Dataset for 7th Grade Science (Ecology) ---")
    eco_dialogues = generate_7th_grade_science_eco_sample_dialogues(
        aita_profile=eco_aita_profile, passages=DEFAULT_7TH_GRADE_SCIENCE_PASSAGES
    )
    print(f"Generated {len(eco_dialogues)} sample ecology dialogues.")
    if eco_dialogues:
        print("\nExample Ecology Dialogue (Food Web):")
        # Find a food web dialogue to print
        foodweb_example = next((d for d in eco_dialogues if "foodweb" in d["dialogue_id"]), None)
        if foodweb_example:
            print(json.dumps(foodweb_example, indent=2))
        else:
            print(" (No food web example found to display, printing first eco dialogue if available)")
            if eco_dialogues: print(json.dumps(eco_dialogues[0], indent=2))

        save_structured_data(eco_dialogues, "eco_explorer_aita_sample_data.json")
    print("-" * 30)
    
    print("\nScript execution finished.")
