# AITA Pedagogical Reasoner: Scope & Explanation Formats (V1)

## 1. Introduction

### Purpose
This document defines the scope and format for how AI Tutors (AITAs) can explain their pedagogical reasoning. It covers explanations intended for students during interactions and how this reasoning is presented to teachers for oversight and understanding.

### Benefits
*   **Increased Transparency**: Helps users understand the AITA's behavior and intent.
*   **Student Metacognition**: Encourages students to reflect on the learning process and understand *why* certain questions or strategies are used by the AITA.
*   **Teacher Trust & Insight**: Provides educators with a clearer view of the AITA's pedagogical decision-making, fostering trust and enabling better analysis of teaching strategies.
*   **Debugging & Refinement**: Exposing the AITA's reasoning aids developers and curriculum specialists in debugging dialogue flows and refining pedagogical strategies.

## 2. Target Audiences & Goals for Explanation

*   **Students (e.g., 4th Grade for Reading AITA, 7th Grade for Ecology AITA):**
    *   **Goal**: To help students understand *why* the AITA is asking a particular question or providing a certain type of guidance. This aims to make the learning process clearer, more engaging, and less like a "black box."
    *   **Characteristics**: Explanations must be simple, age-appropriate, concise, encouraging, and directly related to the student's learning task. They should avoid complex pedagogical jargon.

*   **Teachers (via Teacher Oversight Dashboard & Logs):**
    *   **Goal**: To provide educators with detailed insights into the AITA's pedagogical strategies, its alignment with learning objectives, and the rationale behind its decision-making process for specific dialogue turns.
    *   **Characteristics**: Explanations can be more detailed, use standard pedagogical terminology, and be linked to associated metadata like ontology tags or learning objectives.

## 3. Scope of What the AITA Explains (V1)

*   **Primary Focus**: The immediate pedagogical reason for the AITA's *most recent utterance* (e.g., the question it just asked, the hint it just provided, or the explanation it just gave).
*   **Student Elicited Examples**:
    *   Student: "Why did you ask me that?"
    *   Student: "How does that help me find the main idea?"
    *   Student: "I don't get why you're asking about the character's feelings."
    *   Student: "Why are you telling me this definition now?"
*   **Out of Scope for V1 Reasoner**:
    *   Deep explanations of the underlying SLM's internal workings, neural network architecture, or complex AI theory.
    *   Predictions about future pedagogical moves beyond the immediate next step.
    *   Complex causal chains of its entire dialogue strategy.

## 4. Triggers for Explanations

*   **Student-Initiated (Reactive - V1 Implementation Focus):**
    1.  **UI Element**: A dedicated UI element (e.g., a "?" button or a "Why this question?" link) next to or associated with each AITA message in the student frontend. Clicking this would trigger a request to the AITA for an explanation of its last turn.
    2.  **Natural Language Phrases (Conceptual for V1, more robust in V2+):** The AITA system could attempt to recognize simple, direct student phrases like:
        *   "Why did you ask that?"
        *   "How does that help?"
        *   "I don't understand why..."
        *   "What do you mean by that question?"
        *   *(For V1, this might be a very limited set of exact phrase matches. More advanced NLU would be V2+).*

*   **Teacher-Viewed (Always Available in Data):**
    *   The AITA's pedagogical reasoning, primarily derived from the `pedagogical_notes` (List[str]) and `ontology_concept_tags` (List[str]) associated with each AITA turn, is always logged in the xAPI-like statements (`service_xapi_statements.jsonl`).
    *   This data is then available for review in the Teacher Oversight Dashboard within the session transcript view, typically in an expander section for each AITA turn.

## 5. Format of Explanations

### 5.1. Student-Facing Explanations (V1 Approach: Template-Based from Pedagogical Notes/Tags)

The `AITA Interaction Service` will generate these explanations.

*   **Mechanism**:
    1.  The student frontend sends a request for explanation, referencing the AITA's previous turn (or the turn in question).
    2.  The `AITA Interaction Service` retrieves the `pedagogical_notes` and/or `ontology_concept_tags` that were logged for that specific AITA turn. (This implies the service needs access to the dialogue history or the xAPI log for the current session).
    3.  A predefined mapping/dictionary within the service is used to select an age-appropriate, templated explanation string based on keywords or specific tags found in the `pedagogical_notes` or `ontology_concept_tags`.
    4.  If multiple notes/tags match, a primary one can be chosen, or a generic explanation can be provided.

*   **Example Mappings & Templates (Illustrative for 4th Grade Reading):**

    | Keyword/Tag in `pedagogical_notes` or `ontology_concept_tags` | Student-Facing Explanation Template                                                                                                |
    | :----------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
    | "Prompt for textual evidence", "STRAT.Prompt.TextualEvidence" | "I asked that to help you practice finding clues right in the story, like a detective looking for hints to solve a mystery!"         |
    | "Socratic question", "elicit prior knowledge", "STRAT.Socratic.PriorKnowledge" | "I'm curious about what you already know! That helps me figure out the best way to help you learn this new idea."        |
    | "Break down problem", "scaffolding", "STRAT.Scaffolding.Breakdown" | "Sometimes big ideas are easier to understand if we look at smaller pieces one by one. That's what we're doing now!"          |
    | "Acknowledge student emotion", "empathetic response", "STRAT.Feedback.Empathetic" | "It's important to me that you're feeling okay while we learn! Sometimes just talking about how we feel helps us move forward." |
    | "Connect problem and resolution", "main idea synthesis", "STRAT.MainIdea.Synthesis" | "To find the main idea of a story, it's often helpful to see what the big problem was and how it got solved. That's why I asked about the ending!" |
    | "Contextual clues for vocabulary", "STRAT.Vocab.ContextClue" | "When we find a new word, looking at the words around it can give us super clues about what it means. That's why I asked about the sentence it was in!" |
    | "Positive reinforcement", "confirm understanding", "STRAT.Feedback.Positive" | "I said that because you did a great job figuring it out, and I wanted to let you know you're on the right track!"      |
    | "Clarify student response", "STRAT.Clarification.Request"    | "I asked for more details to make sure I fully understand your great ideas before we move on!"                                   |

*   **Tone & Style**: Explanations should be encouraging, simple, use analogies relatable to the age group (e.g., "detective"), and clearly connect the AITA's action to the student's learning process.

### 5.2. Teacher-Facing Explanations (Via Teacher Dashboard & Logs)

This leverages the detailed data already being logged.

*   **Primary Method (Existing Design)**:
    *   The `pedagogical_notes` (as a `List[str]`) and `ontology_concept_tags` (as a `List[str]`) associated with each AITA turn are included in the xAPI-like statements.
    *   The Teacher Oversight Dashboard (specifically the Session Transcript View) will display these lists directly within an expander for each AITA turn, providing teachers with the AITA's explicit rationale as authored or logged.

*   **New Conceptual Field for Logs: `aita_turn_narrative_rationale` (V1.5+ Enhancement)**:
    *   **Purpose**: To provide a concise, human-readable summary of the AITA's intent for a specific turn, complementing the more granular `pedagogical_notes` and `ontology_concept_tags`.
    *   **Format**: A single string (1-2 sentences).
    *   **Generation**:
        *   **Option A (Service-Generated)**: The `AITA Interaction Service` could algorithmically construct this rationale by summarizing key `pedagogical_notes` or by using a template based on high-priority `ontology_concept_tags`.
        *   **Option B (SLM-Generated - Future)**: A fine-tuned SLM could potentially generate this rationale itself as part of its output, if prompted to explain its reasoning. This is more complex and likely V2+.
    *   **Storage**: This field would be added to the AITA turn object within the `dialogue_turns` in the AITA JSON (during authoring or generation) and subsequently included in the xAPI log's extensions (e.g., under `object.definition.extensions` or `result.extensions`).
    *   **Display**: The Teacher Dashboard would display this `aita_turn_narrative_rationale` prominently for each AITA turn, perhaps above or alongside the more detailed `pedagogical_notes` list.
    *   *Example*: "Aimed to scaffold main idea identification by prompting the student to connect the character's primary problem with the story's resolution, using an open-ended guiding question."

## 6. Implementation Approach for Student-Facing Explanations (V1)

*   **V1 Focus**: The initial implementation will use the **template-based approach (Section 5.1)**.
*   **Location of Logic**: The mapping from `pedagogical_notes`/`ontology_concept_tags` to student-facing explanation templates will reside within the **`AITA Interaction Service`**.
*   **Process**:
    1.  Student Frontend sends a request (e.g., to a new `/explain_last_turn` endpoint or a flag on `/interact`) indicating the student wants an explanation for the AITA's previous utterance.
    2.  The `AITA Interaction Service` needs to access the `pedagogical_notes`/`ontology_concept_tags` of that specific previous AITA turn. This might involve:
        *   The client sending back an identifier for the AITA turn in question.
        *   The service temporarily caching the last few turns' metadata (including notes/tags) for the active session.
    3.  The service looks up matching keywords/tags in its predefined map and returns the corresponding templated explanation.
    4.  If no specific match, a generic explanation like "I'm asking this to help us explore the topic more deeply!" can be returned.
*   **Dynamic SLM-Generated Explanations**: Generating these explanations dynamically using the SLM itself (e.g., "Explain your last question to the student in simple terms") is a more advanced feature, considered for V2+ of the Reasoner, as it requires careful prompting and potential fine-tuning to ensure explanations are accurate, safe, and genuinely helpful without being condescending or overly complex.

This strategy aims to provide a foundational capability for AITAs to explain their reasoning, enhancing transparency and supporting student metacognition, while providing detailed pedagogical insights for educators.
