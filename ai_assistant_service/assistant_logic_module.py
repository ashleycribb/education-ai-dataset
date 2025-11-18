# ai_assistant_service/assistant_logic_module.py
import json
import datetime
from typing import List, Dict, Any, Tuple, Optional

# --- Evaluation Status Constants (Global Scope) ---
STATUS_CORRECT = "correct"
STATUS_NEEDS_HELP = "needs_help"
STATUS_INCORRECT_GENERIC = "incorrect_generic"
STATUS_PARTIALLY_CORRECT_COMMON_MULTIPLE = "partially_correct_common_multiple"
STATUS_FLAWED_STRATEGY_ADDED_DENOMINATORS = "flawed_strategy_added_denominators"
STATUS_FLAWED_STRATEGY_MULTIPLIED_DENOMINATORS_ONLY = "flawed_strategy_multiplied_denominators_only"
STATUS_PARTIALLY_CORRECT_SETTING = "partially_correct_setting"
STATUS_INCORRECT_OPPOSITE = "incorrect_opposite"
STATUS_INCORRECT_UNRELATED = "incorrect_unrelated"

# --- xAPI Constants (Module Level) ---
XAPI_ACTOR = {"mbox": "mailto:student@example.com", "name": "Simulated Student", "objectType": "Agent"}
XAPI_VERB_EXPERIENCED = {"id": "http://adlnet.gov/expapi/verbs/experienced", "display": {"en-US": "experienced"}}
XAPI_VERB_ATTEMPTED = {"id": "http://adlnet.gov/expapi/verbs/attempted", "display": {"en-US": "attempted"}}
XAPI_VERB_COMPLETED = {"id": "http://adlnet.gov/expapi/verbs/completed", "display": {"en-US": "completed"}}
XAPI_VERB_INTERACTED = {"id": "http://adlnet.gov/expapi/verbs/interacted", "display": {"en-US": "interacted"}}
XAPI_ACTIVITY_BASE_IRI = "http://example.com/xapi/activities/4th-reading/"

# --- Database Integration (Module Level) ---
# This will be imported from .db in the actual FastAPI app,
# but for the module to be self-contained for understanding,
# we might consider how it gets access if used standalone (though not the primary goal here).
# For now, we assume 'database' object will be available in the scope where _send_xapi_statement_to_db is called.
# This will be properly handled by importing from .db in the FastAPI context.
from .db import database # This line is for when this module is part of the FastAPI app via .db

# --- Helper Functions (Module Level) ---
def create_xapi_statement(actor: Dict[str, Any], verb_id: str, verb_display_map: Dict[str, str],
                          object_id: str, object_name_map: Dict[str, str],
                          object_description_map: Dict[str, str], object_type: str,
                          context_extensions: Optional[Dict[str, Any]] = None,
                          result_extensions: Optional[Dict[str, Any]] = None,
                          result_success: Optional[bool] = None,
                          result_completion: Optional[bool] = None,
                          student_response: Optional[str] = None,
                          parent_activity_id: Optional[str] = None,
                          interaction_type: Optional[str] = None) -> Dict[str, Any]:
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    statement: Dict[str, Any] = {
        "actor": actor,
        "verb": {"id": verb_id, "display": verb_display_map},
        "object": { "id": object_id, "definition": { "name": object_name_map, "description": object_description_map, "type": object_type }, "objectType": "Activity" },
        "timestamp": timestamp
    }
    context_part: Dict[str, Any] = {}
    context_activities: Dict[str, Any] = {}
    if parent_activity_id: context_activities["parent"] = [{"id": parent_activity_id, "objectType": "Activity"}]
    if context_extensions: context_part["extensions"] = context_extensions
    if context_activities: context_part["contextActivities"] = context_activities
    if context_part: statement["context"] = context_part
    result_part: Dict[str, Any] = {}
    if result_success is not None: result_part["success"] = result_success
    if result_completion is not None: result_part["completion"] = result_completion
    if student_response is not None: result_part["response"] = str(student_response)
    if result_extensions: result_part["extensions"] = result_extensions
    if result_part: statement["result"] = result_part
    return statement

def get_student_model(user_id: str) -> Dict[str, Any]:
    models = { "student_reading_story1": {"recent_topic": "basic sentence structure"} }
    return models.get(user_id, {"recent_topic": None, "interests": []})

def get_current_activity(user_id: str, activity_key: str) -> Optional[Dict[str, Any]]:
    if activity_key == "lost_kite_activity":
        activity_iri_base = XAPI_ACTIVITY_BASE_IRI + "story_lost_kite/"
        return {
            "object_id": activity_iri_base + "activity", "object_name_map": {"en-US": "Story Comprehension: The Lost Kite"},
            "object_description_map": {"en-US": "A lesson about understanding the main idea and key details of the story 'The Lost Kite'."},
            "object_type": "http://adlnet.gov/expapi/activities/lesson",
            "objective_id": activity_iri_base + "objective", "objective_name_map": {"en-US": "Learning Objective: Main Idea and Details"},
            "objective_description_map": {"en-US": "Understand the main idea and key details of the story 'The Lost Kite'."},
            "objective_type": "http://adlnet.gov/expapi/activities/objective",
            "id": "reading_story1_lost_kite", "name": "Reading: The Lost Kite", "type": "reading_comprehension", "subject": "Reading",
            "details": "We will read 'The Lost Kite' and then answer some questions about its main idea and vocabulary.",
            "sub_tasks": [
                {
                    "object_id": activity_iri_base + "subtask_read_story", "object_name_map": {"en-US": "Reading the Story: The Lost Kite"},
                    "object_description_map": {"en-US": "Student reads the provided story text."}, "object_type": "http://adlnet.gov/expapi/activities/interaction",
                    "interaction_type": "other", "name": "Reading the Story",
                    "description": "First, please read the story 'The Lost Kite'. (Imagine the story is displayed here). Once you're done, let me know.",
                    "correct_answer_keywords": ["done", "finished", "read it", "ok", "yes"], "max_attempts": 1, "response_evaluations": [], "help_levels": []
                },
                {
                    "object_id": activity_iri_base + "subtask_main_idea", "object_name_map": {"en-US": "Identify Main Idea: The Lost Kite"},
                    "object_description_map": {"en-US": "What is the main idea of 'The Lost Kite'?"}, "object_type": "http://adlnet.gov/expapi/activities/interaction",
                    "interaction_type": "fill-in", "name": "Identify Main Idea",
                    "description": "What do you think is the main idea of 'The Lost Kite'?",
                    "correct_answer_keywords": ["lost kite", "sad then happy", "found his kite", "friendship helps"], "max_attempts": 3,
                    "response_evaluations": [{"keywords": ["windy", "park"], "status": STATUS_PARTIALLY_CORRECT_SETTING, "feedback": "You mentioned the setting (windy, park), which is good! But what's the main thing that happens to the character related to the kite?", "next_action_prompt": "Focus on the kite and the character's feelings."}],
                    "help_levels": [
                        {"id": "help1", "type": "hint", "content": "Think about what the story is mostly about. What problem does the main character face and how is it solved?"},
                        {"id": "help2", "type": "explanation", "content": "The main idea is the most important point of the story. It's what the author wants you to remember most."}
                    ]
                },
                {
                    "object_id": activity_iri_base + "subtask_vocab_anxious", "object_name_map": {"en-US": "Vocabulary Check: 'Anxious'"},
                    "object_description_map": {"en-US": "What does the word 'anxious' mean in the story?"}, "object_type": "http://adlnet.gov/expapi/activities/interaction",
                    "interaction_type": "choice", "name": "Vocabulary Check: 'Anxious'",
                    "description": "The story says, 'Tom felt anxious when he couldn't find his kite.' What does 'anxious' mean here? A) Happy, B) Worried, C) Sleepy",
                    "correct_answer_keywords": ["b", "worried"], "max_attempts": 2,
                    "response_evaluations": [
                         {"keywords": ["a", "happy"], "status": STATUS_INCORRECT_OPPOSITE, "feedback": "'Happy' is the opposite of how Tom felt. He lost his kite, so how would that make him feel?", "next_action_prompt": "Try another option."},
                         {"keywords": ["c", "sleepy"], "status": STATUS_INCORRECT_UNRELATED, "feedback": "'Sleepy' doesn't quite fit. Losing something important usually makes you feel something else.", "next_action_prompt": "Think about how you'd feel if you lost your favorite toy."}
                    ],
                    "help_levels": [ {"id": "help1", "type": "hint", "content": "When you're anxious, you might feel your heart beat a little faster..."} ]
                }
            ]
        }
    return None

class AIAssistant:
    def __init__(self):
        self.user_id: Optional[str] = None
        self.student_model: Dict[str, Any] = {}
        self.current_activity_key: Optional[str] = None
        self.current_activity_data: Optional[Dict[str, Any]] = None
        self.current_activity_object_id: Optional[str] = None
        self.current_sub_task_index: int = 0
        self.sub_task_state: Dict[str, int] = {}
        self.is_activity_complete: bool = False
        self.pending_ai_messages: List[str] = []
        self.pending_xapi_statements: List[Dict[str, Any]] = []

    def _send_ai_message(self, message: str):
        self.pending_ai_messages.append(message)

    async def _send_xapi_statement_to_db(self, statement: Dict[str, Any]):
        """Helper to format and save xAPI statement to DB."""
        actor = statement.get('actor', {})
        actor_mbox = actor.get('mbox') if isinstance(actor, dict) else None
        verb = statement.get('verb', {})
        verb_id = verb.get('id') if isinstance(verb, dict) else None
        obj_data = statement.get('object', {})
        activity_id = obj_data.get('id') if isinstance(obj_data, dict) else None

        query = """
        INSERT INTO raw_xapi_statements (statement, actor_mbox, verb_id, activity_id)
        VALUES (:statement_json, :actor_mbox, :verb_id, :activity_id) RETURNING id;
        """
        values = {
            "statement_json": json.dumps(statement),
            "actor_mbox": actor_mbox,
            "verb_id": verb_id,
            "activity_id": activity_id
        }
        try:
            if not database.is_connected: # Ensure connection before executing
                await database.connect() # This might be an issue if called outside FastAPI startup/shutdown
                                        # For now, assume connect_db is called at app startup.
                                        # A more robust solution might involve passing the DB connection or using a context manager.
            await database.execute(query=query, values=values)
        except Exception as e:
            print(f"Error saving xAPI statement to DB: {e}")
            # Decide how to handle DB errors: log, raise, or ignore for pending_xapi_statements

    async def _send_xapi_statement(self, statement: Dict[str, Any]):
        self.pending_xapi_statements.append(statement)
        await self._send_xapi_statement_to_db(statement)


    def get_pending_outputs(self) -> Tuple[List[str], List[Dict[str, Any]], bool]:
        messages_to_send = list(self.pending_ai_messages)
        statements_to_send = list(self.pending_xapi_statements)
        self.pending_ai_messages.clear()
        self.pending_xapi_statements.clear()
        return messages_to_send, statements_to_send, self.is_activity_complete

    def _evaluate_student_response(self, response: str, sub_task: Dict[str, Any]) -> Dict[str, Any]:
        response_lower = response.lower()
        for eval_config in sub_task.get("response_evaluations", []):
            if any(keyword in response_lower for keyword in eval_config.get("keywords", [])):
                return {"status": eval_config.get("status", STATUS_INCORRECT_GENERIC),
                        "feedback": eval_config.get("feedback", "Let's look at that a different way."),
                        "next_action_prompt": eval_config.get("next_action_prompt")}
        if any(keyword in response_lower for keyword in sub_task.get("correct_answer_keywords", [])):
            return {"status": STATUS_CORRECT, "feedback": "That's correct! Well done."}
        if response_lower in ["help", "idk", "i don't know", "clue", "hint"]:
            return {"status": STATUS_NEEDS_HELP, "feedback": "No problem, let's see if this helps."}
        return {"status": STATUS_INCORRECT_GENERIC, "feedback": "That's not quite it. Let's try a hint."}

    async def _provide_graduated_help(self, sub_task: Dict[str, Any]) -> bool:
        help_level_index = self.sub_task_state.get('help_provided_count', 0)
        help_levels = sub_task.get("help_levels", [])
        if help_level_index < len(help_levels):
            help_item = help_levels[help_level_index]
            help_content = help_item.get('content')
            help_type = help_item.get('type')
            help_id_suffix = help_item.get('id', f"level{help_level_index}")
            self._send_ai_message(f"Hint ({help_type}): {help_content}")
            interacted_help_stmt = create_xapi_statement(
                actor=XAPI_ACTOR, verb_id=XAPI_VERB_INTERACTED["id"], verb_display_map=XAPI_VERB_INTERACTED["display"],
                object_id=f"{sub_task.get('object_id')}/help/{help_id_suffix}",
                object_name_map={"en-US": f"Help for {sub_task.get('name')}: {help_type}"},
                object_description_map={"en-US": help_content},
                object_type="http://adlnet.gov/expapi/activities/community",
                parent_activity_id=sub_task.get('object_id'))
            await self._send_xapi_statement(interacted_help_stmt)
            self.sub_task_state['help_provided_count'] = help_level_index + 1
            return True
        else:
            self._send_ai_message("I've given all the help I have for this part. Let's try your best!")
            return False

    async def _introduce_sub_task(self, sub_task_data: Dict[str, Any]):
        sub_task_name = sub_task_data.get('name', 'this part')
        sub_task_description = sub_task_data.get('description', 'Let\'s work on this part.')
        self._send_ai_message(f"\n--- Starting Part {self.current_sub_task_index + 1}: {sub_task_name} ---")
        self._send_ai_message(sub_task_description)
        experienced_subtask_stmt = create_xapi_statement(
            actor=XAPI_ACTOR, verb_id=XAPI_VERB_EXPERIENCED["id"], verb_display_map=XAPI_VERB_EXPERIENCED["display"],
            object_id=sub_task_data.get("object_id"),
            object_name_map=sub_task_data.get("object_name_map", {"en-US": sub_task_name}),
            object_description_map=sub_task_data.get("object_description_map", {"en-US": sub_task_description}),
            object_type=sub_task_data.get("object_type", "http://adlnet.gov/expapi/activities/interaction"),
            interaction_type=sub_task_data.get("interaction_type"),
            parent_activity_id=self.current_activity_object_id)
        await self._send_xapi_statement(experienced_subtask_stmt)
        self.sub_task_state = {'attempts': 0, 'help_provided_count': 0}

    async def start_activity(self, user_id: str, activity_key: str):
        self.user_id = user_id
        self.current_activity_key = activity_key
        self.student_model = get_student_model(user_id) # Module-level function
        self.current_activity_data = get_current_activity(user_id, activity_key) # Module-level function

        self.current_sub_task_index = 0
        self.is_activity_complete = False
        self.pending_ai_messages.clear()
        self.pending_xapi_statements.clear()
        self.sub_task_state = {}

        if not self.current_activity_data:
            self._send_ai_message(f"Sorry, I couldn't find an activity with key: {activity_key}")
            self.is_activity_complete = True
            return

        self.current_activity_object_id = self.current_activity_data.get("object_id")
        activity_name = self.current_activity_data.get("name", "our new topic")

        goal_statement = f"Today, we're going to learn about {activity_name.lower()}!"
        self._send_ai_message(goal_statement)
        if self.current_activity_data.get("objective_id"):
             await self._send_xapi_statement(create_xapi_statement( # Module-level function
                XAPI_ACTOR, XAPI_VERB_EXPERIENCED["id"], XAPI_VERB_EXPERIENCED["display"],
                self.current_activity_data["objective_id"],
                self.current_activity_data.get("objective_name_map", {"en-US": "Activity Objective"}),
                self.current_activity_data.get("objective_description_map", {"en-US": "Objective"}),
                self.current_activity_data.get("objective_type", "http://adlnet.gov/expapi/activities/objective"),
                parent_activity_id=self.current_activity_object_id))
        if self.current_activity_data.get("details"):
            self._send_ai_message(f"Specifically, we'll be {self.current_activity_data.get('details').lower()}")

        sub_tasks = self.current_activity_data.get("sub_tasks", [])
        if not sub_tasks:
            self._send_ai_message("Looks like this activity has no sub-tasks defined yet!")
            self.is_activity_complete = True
        else:
            self._send_ai_message(f"\nTo achieve our goal of {activity_name.lower()}, we're going to work through these parts together:")
            for i, task_info in enumerate(sub_tasks):
                self._send_ai_message(f"  {i+1}. {task_info.get('name', f'part {i+1}')}")

            if self.current_activity_object_id:
                await self._send_xapi_statement(create_xapi_statement(
                    XAPI_ACTOR, XAPI_VERB_EXPERIENCED["id"], XAPI_VERB_EXPERIENCED["display"],
                    self.current_activity_object_id,
                    self.current_activity_data.get("object_name_map", {"en-US": activity_name}),
                    self.current_activity_data.get("object_description_map", {"en-US": self.current_activity_data.get("details", "")}),
                    self.current_activity_data.get("object_type", "http://adlnet.gov/expapi/activities/activity"),
                    context_extensions={"sub_task_overview": [st.get("name") for st in sub_tasks]}))

            self._send_ai_message("\nLet's get started!")
            await self._introduce_sub_task(sub_tasks[0])

    async def _process_single_interaction(self, sub_task: Dict[str, Any], student_response: str) -> bool:
        self.sub_task_state['attempts'] = self.sub_task_state.get('attempts', 0) + 1
        evaluation_result = self._evaluate_student_response(student_response, sub_task)
        current_status = evaluation_result.get("status")
        feedback_message = evaluation_result.get("feedback")
        next_action_prompt = evaluation_result.get("next_action_prompt")
        self._send_ai_message(feedback_message)

        await self._send_xapi_statement(create_xapi_statement(
            actor=XAPI_ACTOR, verb_id=XAPI_VERB_ATTEMPTED["id"], verb_display_map=XAPI_VERB_ATTEMPTED["display"],
            object_id=sub_task.get("object_id"), object_name_map=sub_task.get("object_name_map"),
            object_description_map=sub_task.get("object_description_map"), object_type=sub_task.get("object_type"),
            interaction_type=sub_task.get("interaction_type"), result_success=(current_status == STATUS_CORRECT),
            student_response=student_response,
            context_extensions={"identified_intention": current_status, f"attempt_{self.sub_task_state['attempts']}_details": feedback_message},
            parent_activity_id=self.current_activity_object_id))

        if current_status == STATUS_CORRECT:
            await self._send_xapi_statement(create_xapi_statement(
                actor=XAPI_ACTOR, verb_id=XAPI_VERB_COMPLETED["id"], verb_display_map=XAPI_VERB_COMPLETED["display"],
                object_id=sub_task.get("object_id"), object_name_map=sub_task.get("object_name_map"),
                object_description_map=sub_task.get("object_description_map"), object_type=sub_task.get("object_type"),
                interaction_type=sub_task.get("interaction_type"), result_success=True, result_completion=True,
                result_extensions={"attempts_taken": self.sub_task_state['attempts'], "help_levels_used": self.sub_task_state.get('help_provided_count', 0)},
                parent_activity_id=self.current_activity_object_id))
            self._send_ai_message(f"Great job on completing: {sub_task.get('name')}!")
            return True

        if current_status not in [STATUS_NEEDS_HELP, STATUS_INCORRECT_GENERIC]:
            if next_action_prompt: self._send_ai_message(next_action_prompt)
        elif current_status == STATUS_NEEDS_HELP or current_status == STATUS_INCORRECT_GENERIC:
            await self._provide_graduated_help(sub_task)

        if self.sub_task_state['attempts'] < sub_task.get("max_attempts", 3):
            self._send_ai_message("Please try answering the question again, or type 'help'.")
        else:
            self._send_ai_message(f"It looks like we're still stuck on {sub_task.get('name')}. That's okay!")
            return True
        return False

    async def process_student_input(self, student_response: str):
        if self.is_activity_complete or not self.current_activity_data or not self.current_activity_data.get('sub_tasks'):
            self._send_ai_message("There's no active activity or sub-task to respond to.")
            self.is_activity_complete = True
            return

        sub_tasks = self.current_activity_data['sub_tasks']
        if self.current_sub_task_index >= len(sub_tasks):
            self._send_ai_message("It seems we've finished all sub-tasks!")
            if not self.is_activity_complete: # Ensure completion xAPI only sent once
                self.is_activity_complete = True
                if self.current_activity_object_id:
                    await self._send_xapi_statement(create_xapi_statement(
                        XAPI_ACTOR, XAPI_VERB_COMPLETED["id"], XAPI_VERB_COMPLETED["display"], self.current_activity_object_id,
                        self.current_activity_data.get("object_name_map"), self.current_activity_data.get("object_description_map"),
                        self.current_activity_data.get("object_type"), result_success=True, result_completion=True))
            return

        current_sub_task = sub_tasks[self.current_sub_task_index]
        sub_task_completed_or_exhausted = await self._process_single_interaction(current_sub_task, student_response)

        if sub_task_completed_or_exhausted:
            self.current_sub_task_index += 1
            if self.current_sub_task_index < len(sub_tasks):
                next_sub_task = sub_tasks[self.current_sub_task_index]
                await self._introduce_sub_task(next_sub_task)
            else:
                self._send_ai_message(f"\nWe've completed all parts of {self.current_activity_data.get('name')}! Well done!")
                if not self.is_activity_complete: # Ensure completion xAPI only sent once
                    self.is_activity_complete = True
                    if self.current_activity_object_id:
                        await self._send_xapi_statement(create_xapi_statement(
                            XAPI_ACTOR, XAPI_VERB_COMPLETED["id"], XAPI_VERB_COMPLETED["display"], self.current_activity_object_id,
                            self.current_activity_data.get("object_name_map"), self.current_activity_data.get("object_description_map"),
                            self.current_activity_data.get("object_type"), result_success=True, result_completion=True))
