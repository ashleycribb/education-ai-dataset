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
    "ExplainStrategy": "Understand why an AI tutor asks certain types of questions to help with learning.", # New LO for reasoner example
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
        if self.turn_counter > 1 or increment_seconds > 0 : # Avoid double increment on first get_timestamp(0)
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
    expected_student_thinking: str, keywords: List[str], dataset_version_suffix: str = "Pilot_Iter2_Reasoner" # Updated version suffix
) -> Dict[str, Any]:
    initial_timestamp = dialogue_ctx.get_timestamp(0)
    grade_level_tag = str(aita_profile.get("grade_level", "unknown_grade"))
    subject_tag = aita_profile.get("subject", "unknown_subject").lower().replace(" ", "_")
    # Updated version string to reflect Iteration 2 and Reasoner focus
    dialogue_version = f"1.5_enhanced_iter2_reasoner_{dataset_version_suffix.lower()}"

    return {
        "dialogue_id": dialogue_ctx.dialogue_base_id, "version": dialogue_version,
        "creation_timestamp_utc": initial_timestamp, "last_updated_timestamp_utc": initial_timestamp,
        "metadata": {
            "original_source_content_id": passage["id"],
            "original_source_dataset": f"DEFAULT_{grade_level_tag}TH_GRADE_{subject_tag.upper()}_PASSAGES",
            "tags": [subject_tag, f"{grade_level_tag}th_grade", "gold_standard", dataset_version_suffix.lower()] + additional_tags,
            "tool_source": f"generate_dialogues_v5_iter2_reasoner_{dataset_version_suffix.lower()}" # Updated tool source
        },
        "aita_profile": aita_profile,
        "pedagogical_intent": {
            "interaction_type": interaction_type,
            "learning_objectives": [{"id": f"{subject_tag.upper()}.{grade_level_tag}.LO.{lo_id_code.replace('.', '_')}", "text": lo_text}], # Ensure lo_id_code is filename friendly
            "expected_student_thinking_process": expected_student_thinking,
            "keywords": keywords, "difficulty_level": f"{grade_level_tag}th_grade_on_level"
        },
        "context_provided_to_aita": {
            "user_id": f"student_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-3]}_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}", # Adjusted for longer IDs
            "session_id": f"session_pilot_{dialogue_ctx.dialogue_base_id.split('_')[-3]}_{dialogue_ctx.dialogue_base_id.split('_')[-2]}_{dialogue_ctx.dialogue_base_id.split('_')[-1]}",
            "prior_knowledge_level": "unknown", "prior_performance_summary": "N/A for this pilot dataset.",
            "learning_context_description": f"Student is working on a {grade_level_tag}th-grade {subject_tag} task focusing on {lo_id_code}.",
            "content_item_id": passage["id"], "content_item_title": passage["title"],
            "content_item_text": passage["text"], "potential_grade_level_of_content": grade_level_tag
        },
        "dialogue_turns": [],
        "final_assessment_of_student_understanding": {
            "summary_of_understanding": "Placeholder: Assessment to be filled based on interaction.",
            "mastery_level_per_lo": [{"lo_id": f"{subject_tag.upper()}.{grade_level_tag}.LO.{lo_id_code.replace('.', '_')}", "level": "not_assessed"}],
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
        "Student should identify key elements (character, problem, resolution for narratives; key topic/details for informational) and synthesize them into a central theme.",
        ["main idea", "summary", "central theme", "story elements", "passage topic"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"Hi! Let's read '{passage['title']}'.\n\n\"{passage['text']}\"\n\nWhat is this story mostly about?",
         "pedagogical_notes": ["Greet student", "Present passage text", "Ask open-ended question to elicit initial thoughts on main idea."],
         "aita_turn_narrative_rationale": "AITA presents the passage and asks an initial open-ended question to gauge the student's understanding of the main idea."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "A kitten got lost."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "That's a very important part, you're right! What happens after the kitten gets lost? How does the story end?",
         "pedagogical_notes": ["Acknowledge correct student input.", "Prompt for the resolution of the story to guide towards a complete main idea."],
         "aita_turn_narrative_rationale": "AITA acknowledges the student identified the problem and prompts for the story's resolution to build towards a complete main idea."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "She finds her home and is happy."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "Great! So, if we put those important parts together – the kitten was lost, and then she found her home and was happy – what's the main idea of the whole story in one sentence?",
         "pedagogical_notes": ["Guide student to synthesize the problem and resolution.", "Model how to combine elements for main idea."],
         "aita_turn_narrative_rationale": "AITA prompts the student to synthesize the identified problem and resolution into a concise main idea statement."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "The main idea is that a lost kitten finds her way home and feels happy."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "That's a perfect way to say it! You looked at who the story was about, what happened, and how it ended. Excellent work!",
         "pedagogical_notes": ["Confirm correct main idea identification.", "Provide positive reinforcement.", "Briefly reiterate strategy used."],
         "aita_turn_narrative_rationale": "AITA confirms the student's correct main idea formulation and provides positive reinforcement, briefly summarizing the strategy."}
    ]
    return dialogue_json

def _create_inference_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    is_kitten = passage['id'] == "passage_kitten_001"
    q = "Why did Lily feel scared when the sun set?" if is_kitten else "Why were the other colors hidden before autumn, according to the passage?"
    a = "Because it was getting dark and she was alone." if is_kitten else "Because the green chlorophyll was so strong it covered them up."
    strategy_explanation = "This helps us understand character feelings that aren't directly stated." if is_kitten else "This helps us understand cause and effect in science texts."

    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Inference", LO_TEXTS["Inference"],
        f"guided_inference_{passage['id'].split('_')[-1]}", ["inference", passage['id'].split('_')[-1]],
        "Student uses clues to understand unstated info.", ["inference", "clues"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": f"Let's think about '{passage['title']}'. {q}",
         "pedagogical_notes": ["Prompt for inference based on textual detail."],
         "aita_turn_narrative_rationale": "AITA poses a question requiring the student to infer information not explicitly stated in the text."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": a},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"That's a very good thought! You used clues from the story and what you know to figure that out. That's called making an inference! {strategy_explanation}",
         "pedagogical_notes": ["Validate student's inference.", "Explain the concept of making an inference.", "Connect to broader reading strategy."],
         "aita_turn_narrative_rationale": "AITA validates the student's inference, explains the skill of inferring, and connects it to a reading strategy."}
    ]
    return dialogue_json

def _create_vocab_dialogue_4th_refined(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext, target_word: str, definition: str) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "Vocabulary", LO_TEXTS["Vocabulary"],
        f"contextual_vocab_refined_{target_word}_{passage['id'].split('_')[-1]}", ["vocabulary", target_word],
        "Student infers word meaning from context, with direct explanation if needed.", ["vocabulary", target_word] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"In '{passage['title']}', the text says: \"...{passage['text'][passage['text'].lower().find(target_word)-30 if passage['text'].lower().find(target_word)-30 > 0 else 0 : passage['text'].lower().find(target_word)+len(target_word)+30 ]}...\" What do you think '{target_word}' might mean here?",
         "pedagogical_notes": ["Present word in context snippet.", "Initial prompt for meaning using clues."],
         "aita_turn_narrative_rationale": "AITA presents the target word within a short context from the passage and asks the student to infer its meaning."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Hmm, I'm not sure."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"Okay, let's look for clues around '{target_word}'. For example, if it's about Lily's house, how did she feel when she saw it after being lost?",
         "pedagogical_notes": ["Encourage use of contextual clues.", "Prompt based on surrounding narrative/emotion."],
         "aita_turn_narrative_rationale": "AITA prompts the student to use contextual clues related to the character's emotions or situation."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "She was happy and purring, so it's a good thing."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"That's right! So if '{target_word}' describes her house and she felt happy and safe there, what kind of word do you think '{target_word}' is?",
         "pedagogical_notes": ["Guide student to connect context to word's connotation.", "Reinforce inferential step."],
         "aita_turn_narrative_rationale": "AITA guides the student to connect the contextual clues to the connotation of the target word."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "I still don't really know what it means."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"That's okay! '{target_word.capitalize()}' means something like: {definition}. Now that you know the definition, can you try to use '{target_word}' in a sentence about something else that feels that way?",
         "pedagogical_notes": ["Provide direct definition after student indicates continued difficulty.", "Ask for application of new vocabulary in a new context."],
         "aita_turn_narrative_rationale": "AITA provides a direct definition after the student struggles and asks for application to check understanding."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": f"My fluffy blanket makes my bed feel {target_word}."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "That's a wonderful sentence! It shows you understand what 'cozy' means. Great job!",
         "pedagogical_notes": ["Confirm correct application of the word.", "Provide positive reinforcement."],
         "aita_turn_narrative_rationale": "AITA confirms the student's correct application of the new word and offers positive reinforcement."}
    ]
    return dialogue_json

def _create_frustration_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "MainIdea", LO_TEXTS["MainIdea"],
        f"frustration_handling_main_idea_{passage['id'].split('_')[-1]}", ["frustration_handling", "main_idea"],
        "AITA responds empathetically to student frustration and re-scaffolds the task.", ["main idea", "emotion_regulation"],
        dataset_version_suffix="ReadingCompreIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"Let's think about '{passage['title']}' again. What's the biggest, most important thing the author wants us to know about Lily's adventure?",
         "pedagogical_notes": ["Ask a slightly more abstract question about the main message."],
         "aita_turn_narrative_rationale": "AITA poses a question about the main message of the story, aiming for a deeper understanding of the main idea."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "I already said she was lost. This is hard."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "You're right, you did say she was lost, and that's a key part! Sometimes figuring out the *main* message can feel a bit like solving a puzzle. What if we think about it from the very end? How did things turn out for Lily?",
         "pedagogical_notes": ["Acknowledge previous correct input.", "Validate student's feeling (it can be hard).", "Re-scaffold by suggesting a different approach (work backwards from resolution)."],
         "aita_turn_narrative_rationale": "AITA validates student's feeling, acknowledges prior correct input, and re-scaffolds by suggesting a new strategy (work backwards from resolution)."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Ugh, this is too confusing! I give up!"},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "I hear you, and it's totally okay if it feels confusing sometimes! No problem at all. How about we try something different? Instead of the main message, let's just think about Lily. What's one word you'd use to describe how Lily felt when she finally saw her cozy red house?",
         "pedagogical_notes": ["Empathetic response: Acknowledge and validate student's expressed frustration.", "Offer to change approach.", "Re-scaffold to a much simpler, more concrete question focusing on character emotion (inference)."],
         "aita_turn_narrative_rationale": "AITA responds empathetically to student's frustration, normalizes the feeling, and re-scaffolds by shifting to a simpler, more concrete question about character emotion."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Happy?"},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "Happy is a great word for it! See? You're a super clue detective! We can work from there. Thanks for trying again with me.",
         "pedagogical_notes": ["Positive reinforcement for re-engagement on simpler task.", "Build confidence.", "Acknowledge effort."],
         "aita_turn_narrative_rationale": "AITA provides positive reinforcement for the student's re-engagement and answer to the simpler question, aiming to rebuild confidence."}
    ]
    return dialogue_json

def _create_explaining_strategy_dialogue_4th(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "ExplainStrategy", LO_TEXTS["ExplainStrategy"],
        f"reasoner_explanation_inference_{passage['id'].split('_')[-1]}", ["reasoner", "explain_strategy", "inference"],
        "Student asks AITA to explain its questioning strategy, and AITA responds with an age-appropriate explanation.",
        ["inference", "pedagogy", "reasoning", "metacognition"] + passage.get("title", "").lower().split(),
        dataset_version_suffix="ReadingCompreIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": f"In the story about Lily, it says, 'The sun began to set, and Lily felt scared.' What do you think made her feel scared *at that moment*?",
         "pedagogical_notes": ["Posing an inferential question about character emotion tied to a specific event."],
         "aita_turn_narrative_rationale": "AITA asks an inferential question to prompt student to connect textual clues about setting with character emotion."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "Why are you asking me about what the kitten *might* be thinking? The story doesn't say exactly why she was scared right then."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "That's a really good question! Sometimes authors don't tell us everything directly, like with a signpost. When I ask what a character might be thinking or feeling, or why something happened, it helps us practice using clues from the story – like a reading detective! – to understand things the author wants us to figure out. It makes reading more fun too, like solving a little puzzle!",
         "pedagogical_notes": ["Acknowledge student's meta-question.", "Explain 'inference' strategy in simple terms.", "Use 'reading detective' analogy.", "Connect to engagement (fun)."],
         "aita_turn_narrative_rationale": "AITA explains the value of inferential questions using an analogy to make the concept of 'reading between the lines' accessible and engaging for a 4th grader."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text", "utterance": "Oh, okay! So it's like guessing but with clues?"},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "timestamp_utc": dialogue_ctx.get_timestamp(), "utterance_modality": "text",
         "utterance": "Exactly! It's like making a smart guess based on what the story tells us. You got it! Now, back to Lily and the setting sun, any thoughts on why that might make a lost kitten scared?",
         "pedagogical_notes": ["Confirm student's understanding of the explanation.", "Gently guide back to the original pedagogical task."],
         "aita_turn_narrative_rationale": "AITA confirms student's understanding of the pedagogical explanation and smoothly transitions back to the original learning task."}
    ]
    return dialogue_json

def generate_4th_grade_reading_comprehension_sample_dialogues(
    aita_profile: Dict[str, Any], passages: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_dialogues = []
    start_time_base = datetime.datetime.now(datetime.timezone.utc)
    # Ensure each dialogue type gets a unique start time context if needed for strict ordering
    time_offset = 0

    for i, passage in enumerate(passages):
        passage_start_time_str = (start_time_base + datetime.timedelta(minutes=time_offset)).isoformat() + "Z"

        main_idea_ctx = DialogueContext(f"gold_std_{passage['id']}_main_idea_iter2_001", passage_start_time_str)
        dialogue_main_idea = _create_main_idea_dialogue_4th(passage, aita_profile, main_idea_ctx) # Updated notes/rationale
        all_dialogues.append(dialogue_main_idea)
        time_offset += 20 # Increment time for next dialogue

        inference_ctx = DialogueContext(f"gold_std_{passage['id']}_inference_iter2_001", (start_time_base + datetime.timedelta(minutes=time_offset)).isoformat() + "Z")
        dialogue_inference = _create_inference_dialogue_4th(passage, aita_profile, inference_ctx) # Updated notes/rationale
        all_dialogues.append(dialogue_inference)
        time_offset += 20

        vocab_ctx = DialogueContext(f"gold_std_{passage['id']}_vocab_iter2_001", (start_time_base + datetime.timedelta(minutes=time_offset)).isoformat() + "Z")
        target_word = "cozy" if passage['id'] == "passage_kitten_001" else "pigment"
        definition = "comfortable, warm, and safe, making one feel relaxed." if target_word == "cozy" else "a natural substance that gives color to something, like plants or skin."
        dialogue_vocab = _create_vocab_dialogue_4th_refined(passage, aita_profile, vocab_ctx, target_word, definition) # Updated notes/rationale
        all_dialogues.append(dialogue_vocab)
        time_offset += 20

    # Add Frustration Handling example (once for kitten passage)
    passage_kitten = next((p for p in passages if p["id"] == "passage_kitten_001"), None)
    if passage_kitten:
        frustration_ctx = DialogueContext("gold_std_passage_kitten_001_frustration_iter2_001", (start_time_base + datetime.timedelta(minutes=time_offset)).isoformat() + "Z")
        dialogue_frustration = _create_frustration_dialogue_4th(passage_kitten, aita_profile, frustration_ctx) # Updated notes/rationale
        all_dialogues.append(dialogue_frustration)
        time_offset += 20

        # Add Explaining Pedagogy example (once for kitten passage)
        explaining_strategy_ctx = DialogueContext("gold_std_passage_kitten_001_explain_strat_iter2_001", (start_time_base + datetime.timedelta(minutes=time_offset)).isoformat() + "Z")
        dialogue_explain_strategy = _create_explaining_strategy_dialogue_4th(passage_kitten, aita_profile, explaining_strategy_ctx)
        all_dialogues.append(dialogue_explain_strategy)
        time_offset += 20

    # Update common fields for all dialogues
    for dialogue in all_dialogues:
        dialogue_ctx_ref = next(d_ctx for d_name, d_ctx in locals().items() if isinstance(d_ctx, DialogueContext) and d_ctx.dialogue_base_id == dialogue["dialogue_id"]) # Find the context
        dialogue["last_updated_timestamp_utc"] = dialogue_ctx_ref.get_timestamp(0) # Ensure this is the final timestamp
        dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx_ref.get_total_duration(dialogue["creation_timestamp_utc"])
        dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx_ref.turn_counter, "student_turns": len([t for t in dialogue["dialogue_turns"] if t["speaker"]=="student"]), "aita_turns": len([t for t in dialogue["dialogue_turns"] if t["speaker"]=="AITA"])}

    return all_dialogues

# --- 7th Grade Science (Ecology) Dialogue Generation ---
def _create_eco_foodweb_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoFoodWeb", LO_TEXTS["EcoFoodWeb"],
        f"guided_discovery_foodweb_{passage['id'].split('_')[-2]}", ["ecology", "food web"],
        "Student identifies organism roles and traces energy flow.", ["food web", "energy flow"],
        dataset_version_suffix="EcoIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"From '{passage['title']}', what does a producer like an oak tree do?",
         "pedagogical_notes": ["Ask about producers role."], "aita_turn_narrative_rationale": "AITA initiates by asking about the role of a producer, referencing the passage."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "Makes food with sun."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Good! And a caterpillar is a primary consumer. Why is that?",
         "pedagogical_notes": ["Confirm producer understanding.", "Ask about primary consumers role."], "aita_turn_narrative_rationale": "AITA confirms student's understanding and probes about primary consumers."}
    ]
    return dialogue_json

def _create_eco_biotic_abiotic_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoBioticAbiotic", LO_TEXTS["EcoBioticAbiotic"],
        f"classification_biotic_abiotic_{passage['id'].split('_')[-2]}", ["ecology", "biotic", "abiotic"],
        "Student differentiates biotic and abiotic factors with examples.", ["biotic", "abiotic", "living"],
        dataset_version_suffix="EcoIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"'{passage['title']}' mentions fish as biotic. What makes something biotic?",
         "pedagogical_notes": ["Ask for definition of biotic based on example."], "aita_turn_narrative_rationale": "AITA asks student to define 'biotic' using an example from the passage."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "It's a living thing."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Correct! And sunlight is abiotic. What does abiotic mean then?",
         "pedagogical_notes": ["Confirm biotic.", "Introduce abiotic with example and ask for definition."], "aita_turn_narrative_rationale": "AITA confirms 'biotic', then introduces 'abiotic' with an example and asks for its definition."}
    ]
    return dialogue_json

def _create_eco_human_impact_dialogue(passage: Dict[str, str], aita_profile: Dict[str, Any], dialogue_ctx: DialogueContext) -> Dict[str, Any]:
    dialogue_json = _create_base_aita_json(
        dialogue_ctx, passage, aita_profile, "EcoHumanImpact", LO_TEXTS["EcoHumanImpact"],
        f"explanation_human_impact_{passage['id'].split('_')[-2]}", ["ecology", "human impact"],
        "Student describes positive or negative human impact with examples.", ["human impact", "pollution"],
        dataset_version_suffix="EcoIter2_reasoner"
    )
    dialogue_json["dialogue_turns"] = [
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": f"According to '{passage['title']}', how can humans negatively impact rivers?",
         "pedagogical_notes": ["Ask for negative human impact example from text."], "aita_turn_narrative_rationale": "AITA asks student to identify a negative human impact on rivers, based on the provided text."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "student", "utterance": "Pollution from factories."},
        {"turn_id": dialogue_ctx.next_turn_id(), "speaker": "AITA", "utterance": "Good. And can you find a positive impact humans can have?",
         "pedagogical_notes": ["Acknowledge correct answer.", "Ask for positive human impact example."], "aita_turn_narrative_rationale": "AITA confirms the student's answer and asks for a positive human impact example from the text."}
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
            dialogue_ctx = DialogueContext(f"gold_std_{passage_id}_{lo_key_suffix.lower()}_iter2_001", (start_time_base + datetime.timedelta(minutes=i*10)).isoformat() + "Z")
            dialogue = creation_func(passage, aita_profile, dialogue_ctx)
            dialogue["last_updated_timestamp_utc"] = dialogue_ctx.get_timestamp(0)
            dialogue["session_metadata_for_teacher_oversight"]["session_duration_seconds"] = dialogue_ctx.get_total_duration(dialogue["creation_timestamp_utc"])
            dialogue["session_metadata_for_teacher_oversight"]["engagement_metrics"] = {"total_turns": dialogue_ctx.turn_counter, "student_turns": len([t for t in dialogue["dialogue_turns"] if t["speaker"]=="student"]), "aita_turns": len([t for t in dialogue["dialogue_turns"] if t["speaker"]=="AITA"])}
            all_dialogues.append(dialogue)
    return all_dialogues

# --- LLM Augmentation Prompt Generation (Placeholder) ---
def prepare_llm_augmentation_prompt(
    learning_objective_text: str, passage_text: Optional[str] = None,
    aita_profile: Optional[Dict[str, Any]] = None, example_aita_json_structure: Optional[Dict[str, Any]] = None
) -> str:
    prompt = f"Objective: Generate a pedagogically sound dialogue based on the following learning objective: \"{learning_objective_text}\".\n"
    if passage_text: prompt += f"Use the following passage as context: \"{passage_text}\"\n"
    if aita_profile: prompt += f"AITA Profile: {json.dumps(aita_profile)}\n"
    prompt += "Format the output as a complete AITA JSON object. Here's a condensed example of the target structure (fill all fields thoughtfully):\n"
    if example_aita_json_structure:
        condensed_example = {
            "dialogue_id": "llm_gen_example_id",
            "pedagogical_intent": {"learning_objectives": [{"text": learning_objective_text}]},
            "dialogue_turns": [{"turn_id": "turn_1", "speaker": "AITA", "utterance": "...", "pedagogical_notes": ["..."], "aita_turn_narrative_rationale":"..."}],
            "final_assessment_of_student_understanding": {"summary_of_understanding": "..."}
        }
        prompt += json.dumps(condensed_example, indent=2) + "\n"
    prompt += "Please generate the full JSON including all relevant fields like metadata, context_provided_to_aita, detailed dialogue_turns with pedagogical_notes (as a list of strings) and aita_turn_narrative_rationale, xapi tags, ontology_concept_tags, etc."
    return prompt

# --- Data Saving ---
def save_structured_data(structured_data: List[Dict[str, Any]], filename: str) -> None:
    try:
        with open(filename, 'w') as f:
            json.dump(structured_data, f, indent=4)
        print(f"Successfully saved structured data to {filename}")
    except IOError as e:
        print(f"Error saving data to {filename}: {e}")

# --- Main Execution Block (Updated for Iteration 2 - Reasoner Data) ---
if __name__ == "__main__":
    print("--- AITA Data Processing Script (Iteration 2 - Reasoner Data Changes) ---")

    reading_aita_profile_iter2 = {
        "subject": "Reading Comprehension", "grade_level": "4",
        "jurisdiction": "US Common Core ELA Alignment (Simulated)",
        "persona_name": "ReaderAITA_Explorer_v1.5_Iter2_Reasoner",
        "target_audience_description": "4th-grade students, with AITA providing explanations of its teaching strategy."
    }
    print("\n--- Generating Iteration 2 Dataset for 4th Grade Reading Comprehension ---")
    iter2_dialogues_reading = generate_4th_grade_reading_comprehension_sample_dialogues(
        aita_profile=reading_aita_profile_iter2, passages=DEFAULT_4TH_GRADE_PASSAGES
    )
    print(f"Generated {len(iter2_dialogues_reading)} Iteration 2 reading comprehension dialogues.")
    if iter2_dialogues_reading:
        save_structured_data(iter2_dialogues_reading, "pilot_dataset_reading_compre_v1_iter2_reasoner.json")
        explain_strat_example = next((d for d in iter2_dialogues_reading if "explain_strat" in d["dialogue_id"]), None)
        if explain_strat_example:
            print("\nExample 'Explaining Strategy' Dialogue:")
            print(json.dumps(explain_strat_example, indent=2))
        else:
            print("\nFirst dialogue from Iteration 2 Reading Comprehension set:")
            print(json.dumps(iter2_dialogues_reading[0], indent=2))
    print("-" * 30)

    eco_aita_profile_iter2 = {
        "subject": "Science", "grade_level": "7",
        "jurisdiction": "NGSS Alignment (Simulated)",
        "persona_name": "EcoExplorerAITA_v1.2_Iter2_Reasoner",
        "target_audience_description": "7th-grade students learning ecology, with AITA providing explanations."
    }
    print("\n--- Generating Iteration 2 Dataset for 7th Grade Science (Ecology) ---")
    eco_dialogues_iter2 = generate_7th_grade_science_eco_sample_dialogues(
        aita_profile=eco_aita_profile_iter2, passages=DEFAULT_7TH_GRADE_SCIENCE_PASSAGES
    )
    print(f"Generated {len(eco_dialogues_iter2)} Iteration 2 ecology dialogues.")
    if eco_dialogues_iter2:
        save_structured_data(eco_dialogues_iter2, "eco_explorer_aita_sample_data_iter2_reasoner.json")
    print("-" * 30)

    print("\nScript execution finished.")
