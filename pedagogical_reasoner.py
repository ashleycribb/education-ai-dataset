from typing import List, Dict, Any, Optional
import re

class PedagogicalReasoner:
    """
    A heuristic-based reasoner to infer pedagogical strategies and generate rationales
    for AITA interactions (V1 Implementation).
    """

    def __init__(self, logger=None):
        self.logger = logger
        # Define heuristics mapping: (Category, Keyword Regex, Note/Tag)
        self.heuristics = [
            ("Feedback", r"(?i)\b(good job|great work|great start|well done|that's right|correct|excellent)\b", "Positive reinforcement"),
            ("Feedback", r"(?i)\b(not quite|try again|almost)\b", "Constructive feedback"),
            ("Strategy", r"(?i)\b(evidence|clue|where in the text|find)\b", "Prompt for textual evidence"),
            ("Strategy", r"(?i)\b(why|how|what do you think)\b", "Socratic question"),
            ("Strategy", r"(?i)\b(step|first|next|break down)\b", "Break down problem"),
            ("Empathy", r"(?i)\b(feel|worry|understand|hard|difficult)\b", "Acknowledge student emotion"),
            ("Strategy", r"(?i)\b(example|instance|like)\b", "Provided Example"),
            ("Strategy", r"(?i)\b(mean|definition|word)\b", "Contextual clues for vocabulary"),
            ("Clarification", r"(?i)\b(mean|saying|clarify|elaborate)\b", "Clarify student response"),
        ]

    def analyze_turn(self, user_utterance: str, aita_response: str, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes the turn to generate pedagogical notes and a narrative rationale.
        """
        notes = []
        tags = []

        # 1. Analyze AITA Response for Strategies
        for category, regex, note in self.heuristics:
            if re.search(regex, aita_response):
                if note not in notes:
                    notes.append(note)
                    # Create a tag like STRAT.Category.Note (simplified)
                    tag = f"STRAT.{category}.{note.replace(' ', '')}"
                    tags.append(tag)

        # 2. Heuristics based on interaction characteristics
        if "?" in aita_response and "Socratic question" not in notes:
             # Fallback: if it ends with a question mark, it's likely a question
             if aita_response.strip().endswith("?"):
                notes.append("Socratic question")
                tags.append("STRAT.Strategy.SocraticQuestion")

        if len(aita_response.split()) < 15 and "Concise Response" not in notes:
             notes.append("Concise Response")
             tags.append("STYLE.Concise")

        # 3. Generate Rationale
        rationale = self._generate_rationale(notes, tags, context_data)

        return {
            "pedagogical_notes": notes,
            "ontology_concept_tags": tags,
            "aita_turn_narrative_rationale": rationale
        }

    def _generate_rationale(self, notes: List[str], tags: List[str], context_data: Optional[Dict[str, Any]]) -> str:
        """
        Generates a human-readable rationale based on the identified notes.
        """
        if not notes:
            return "Provided a response to guide the student's learning."

        # Prioritize certain notes for the narrative
        primary_strategies = [n for n in notes if n in ["Prompt for textual evidence", "Socratic question", "Break down problem", "Clarify student response"]]
        secondary_strategies = [n for n in notes if n in ["Positive reinforcement", "Acknowledge student emotion", "Constructive feedback"]]

        narrative_parts = []

        if primary_strategies:
            strat = primary_strategies[0]
            if strat == "Prompt for textual evidence":
                narrative_parts.append("Prompted the student to find evidence in the text to support their answer.")
            elif strat == "Socratic question":
                narrative_parts.append("Used a question to elicit the student's own thinking rather than giving the answer.")
            elif strat == "Break down problem":
                narrative_parts.append("Attempted to break the problem down into smaller steps.")
            elif strat == "Clarify student response":
                narrative_parts.append("Asked for clarification to ensure understanding of the student's idea.")
            else:
                narrative_parts.append(f"Used {strat.lower()} to guide the student.")
        else:
             narrative_parts.append("Responded to the student's input.")

        if secondary_strategies:
             strat = secondary_strategies[0]
             if strat == "Positive reinforcement":
                 narrative_parts.append("Included positive reinforcement to encourage the student.")
             elif strat == "Acknowledge student emotion":
                 narrative_parts.append("Acknowledged the student's feelings to build rapport.")

        return " ".join(narrative_parts)

if __name__ == "__main__":
    # Simple test
    reasoner = PedagogicalReasoner()
    test_response = "That's a great start! Can you find the sentence in the story that tells us why the kitten was scared?"
    result = reasoner.analyze_turn("I think the kitten was sad.", test_response)
    print(f"Response: {test_response}")
    print(f"Analysis: {result}")
