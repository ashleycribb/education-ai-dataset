import json
from typing import Dict, List, Any, Optional

from modelcontextprotocol.server import ResourceHandler, ResourceResponse, MCPStdIOServer

# --- Mock Data Definitions ---

# Copied from data_processing_scripts.py for self-containment
DEFAULT_4TH_GRADE_PASSAGES: List[Dict[str, str]] = [
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

def get_passage_snippet(passage_text: str, word_count: int = 15) -> str:
    """Extracts a snippet from the passage text."""
    words = passage_text.split()
    return " ".join(words[:word_count]) + "..." if len(words) > word_count else passage_text

MOCK_DB: Dict[str, Any] = {
    "student_activity_contexts": {
        "student001_ReadingComprehension_passage_kitten_001": {
            "student_id_anonymized": "student001",
            "subject": "ReadingComprehension",
            "current_passage_id": "passage_kitten_001",
            "current_passage_title": DEFAULT_4TH_GRADE_PASSAGES[0]["title"],
            "current_passage_text_snippet": get_passage_snippet(DEFAULT_4TH_GRADE_PASSAGES[0]["text"]),
            "target_learning_objectives_for_activity": [
                {"lo_id": "RC.4.LO1.MainIdea.Narrative", "description": "Identify the main idea of a short narrative passage by recognizing key characters, the problem, and the resolution."},
                {"lo_id": "RC.4.LO3.Vocabulary", "description": "Determine the meaning of an unknown word ('cozy') using context clues."}
            ],
            "recent_attempts_on_this_lo_or_passage": 2,
            "teacher_notes_for_student_on_lo": "Remember to look for both the problem and how it's solved for the main idea, Alex!"
        },
        "student002_ReadingComprehension_passage_leaves_001": {
            "student_id_anonymized": "student002",
            "subject": "ReadingComprehension",
            "current_passage_id": "passage_leaves_001",
            "current_passage_title": DEFAULT_4TH_GRADE_PASSAGES[1]["title"],
            "current_passage_text_snippet": get_passage_snippet(DEFAULT_4TH_GRADE_PASSAGES[1]["text"]),
            "target_learning_objectives_for_activity": [
                {"lo_id": "RC.4.LO2.Inference.Causal", "description": "Make simple inferences about causal relationships based on textual clues."},
                {"lo_id": "RC.4.LO3.Vocabulary", "description": "Determine the meaning of an unknown word ('pigment') using context clues."}
            ],
            "recent_attempts_on_this_lo_or_passage": 0,
            "teacher_notes_for_student_on_lo": None # Optional field
        },
        "student001_Mathematics_topic_fractions_intro": { # A different subject for variety
            "student_id_anonymized": "student001",
            "subject": "Mathematics",
            "current_item_id": "topic_fractions_intro", # Using item_id as passage_id might not always fit
            "current_item_title": "Introduction to Equivalent Fractions",
            "current_item_text_snippet": "To understand equivalent fractions, imagine you have a pizza. If you eat 1/2 of the pizza...",
            "target_learning_objectives_for_activity": [
                {"lo_id": "MATH.4.NF.A.1", "description": "Explain why a fraction a/b is equivalent to a fraction (n*a)/(n*b)..."}
            ],
            "recent_attempts_on_this_lo_or_passage": 1,
            "teacher_notes_for_student_on_lo": "Great start on fractions, Alex! Remember to draw pictures if it helps."
        }
    }
    # "course_contexts": {} # Skipped for this subtask as optional
}

# --- Resource Handlers ---

class StudentActivityContextResourceHandler(ResourceHandler):
    """Handles requests for student activity context."""

    def get_resource(
        self, path_params: Dict[str, str], query_params: Dict[str, str], **kwargs
    ) -> ResourceResponse:
        """
        Retrieves student activity context based on student_id, subject, and item_id.
        Query parameters expected: ?subject=<SubjectName>&item_id=<ItemID>
        """
        student_id = path_params.get("student_id")
        subject = query_params.get("subject")
        item_id = query_params.get("item_id") # Using item_id as a general term

        if not all([student_id, subject, item_id]):
            return ResourceResponse(
                status_code=400,
                payload={
                    "error": "Missing required parameters. Provide student_id in path, and subject & item_id in query parameters."
                },
            )

        resource_key = f"{student_id}_{subject}_{item_id}"
        print(f"Attempting to retrieve resource for key: {resource_key}") # Server-side log

        context_data = MOCK_DB.get("student_activity_contexts", {}).get(resource_key)

        if context_data:
            return ResourceResponse(status_code=200, payload=context_data)
        else:
            return ResourceResponse(
                status_code=404,
                payload={"error": f"Student activity context not found for key: {resource_key}"},
            )

# --- Server Setup and Run ---

if __name__ == "__main__":
    print("--- Mock LMS-MCP Server Starting ---")

    # Instantiate handlers
    student_activity_handler = StudentActivityContextResourceHandler()

    # Register handlers with the server
    # The path pattern uses named segments that will be passed in path_params
    handlers = {
        "/student/{student_id}/activity_context": student_activity_handler
    }

    server = MCPStdIOServer(handlers=handlers)

    print("Registered StudentActivityContextResourceHandler at /student/{student_id}/activity_context")
    print("Mock data available for keys:")
    for key in MOCK_DB.get("student_activity_contexts", {}).keys():
        print(f"  - {key}")
    print("Server is now listening for MCP requests via stdio...")

    server.run()

    print("--- Mock LMS-MCP Server Stopped ---")
