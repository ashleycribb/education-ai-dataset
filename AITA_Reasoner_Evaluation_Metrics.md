# AITA Reasoner: Evaluation Metrics (Conceptual)

## 1. Introduction

The AITA Reasoner feature aims to provide transparency into the pedagogical choices and actions taken by AI Tutors (AITAs) within the AITA ecosystem. By exposing the underlying intent and strategy for each AITA turn, educators can better understand how the AITA is working to support student learning, troubleshoot interactions, and contribute to the refinement of pedagogical models.

This document outlines conceptual metrics for evaluating the AITA Reasoner, primarily focusing on the current implementation where these explanations are pre-defined in the training data and displayed in tools like the Teacher Oversight Dashboard.

## 2. Goals of Evaluation

The primary goals for evaluating the AITA Reasoner are to determine:
*   The **quality** of the explanations themselves (clarity, accuracy, usefulness).
*   The **impact** of these explanations on educators' understanding and actions.
*   The **consistency** of explanations with the AITA's behavior.

## 3. Evaluation Metrics for Pre-defined Explanations

These metrics apply to the current system where `aita_turn_narrative_rationale` and `pedagogical_notes` are authored content.

### 3.1. Quality of Explanations (Assessed by Educators/Experts)

*   **Clarity**:
    *   **Metric**: Likert scale ratings (e.g., 1-5) from educators on the clarity and understandability of `aita_turn_narrative_rationale`.
    *   **Method**: Educators review a set of AITA dialogue turns and their associated rationales in the Teacher Dashboard and rate clarity. Open-ended feedback on confusing rationales should also be collected.
*   **Usefulness**:
    *   **Metric**: Likert scale ratings on how useful educators find the `aita_turn_narrative_rationale` and `pedagogical_notes` for understanding the AITA's strategy.
    *   **Method**: Similar to clarity, educators rate usefulness after reviewing interactions. Specific questions could include: "How helpful was the rationale in understanding why the AITA made this specific utterance?"
*   **Accuracy/Relevance**:
    *   **Metric**: Percentage of rationales and pedagogical notes deemed accurate and relevant to the AITA's utterance and the dialogue context by expert reviewers (e.g., pedagogical experts, experienced teachers).
    *   **Method**: Expert panel review of dialogue transcripts alongside the AITA Reasoner fields. Reviewers would flag inaccurate, misleading, or irrelevant explanations.
*   **Actionability**:
    *   **Metric**: Qualitative feedback on whether the explanations provide insights that could lead to actionable steps for teachers (e.g., adjusting their own teaching, providing feedback on AITA design).
    *   **Method**: Interviews or open-ended survey questions posed to educators after they have used the dashboard with the Reasoner feature.

### 3.2. Consistency of Explanations

*   **Internal Consistency**:
    *   **Metric**: Expert judgment on whether the `pedagogical_notes` (detailed list) align well with the summary provided in `aita_turn_narrative_rationale` for the same turn.
    *   **Method**: Review by pedagogical experts or content authors.
*   **Contextual Consistency**:
    *   **Metric**: Expert judgment on whether the explanations are consistent with the overall dialogue flow, the active learning objective, and the student's visible actions/responses.
    *   **Method**: Review by pedagogical experts.
*   **Potential for Automated Checks (Future Research)**:
    *   Exploration of NLP techniques (e.g., keyword overlap, semantic similarity) to perform preliminary checks for consistency between utterances, notes, and rationales. This is a research area and not a current capability.

### 3.3. Impact on Educator Understanding and Practice (Indirect Measures)

*   **Improved Understanding of AITA Behavior**:
    *   **Metric**: Pre/post assessment of teachers' understanding of AITA strategies after being exposed to the Reasoner explanations (e.g., through scenario-based questions).
    *   **Method**: Administer a questionnaire before and after teachers use the dashboard with Reasoner features for a set period or a set number of reviewed sessions.
*   **Enhanced Ability to Identify Pedagogical Patterns**:
    *   **Metric**: Qualitative analysis of teacher feedback on whether the Reasoner helps them identify and understand the pedagogical patterns employed by the AITA.
    *   **Method**: Think-aloud protocols where teachers review sessions using the dashboard, or post-review interviews.
*   **Informed Feedback on AITA**:
    *   **Metric**: Analysis of the quality and specificity of feedback provided by teachers on AITA performance when they have access to Reasoner explanations versus when they do not.
    *   **Method**: Collect teacher feedback on AITA interactions under both conditions (with/without Reasoner data) and have it rated by a panel.

## 4. Evaluation Metrics for Dynamically Generated Explanations (Future)

If future iterations of AITA involve the SLM dynamically generating the `aita_turn_narrative_rationale` or other explanations, additional metrics would be needed:

*   **Fluency and Coherence**:
    *   **Metric**: Human ratings of the grammatical correctness, readability, and logical flow of generated explanations.
    *   **Method**: Similar to evaluating SLM-generated text in other contexts.
*   **Accuracy to AITA's Internal State/Principles**:
    *   **Metric**: This is highly challenging. It might involve comparing generated explanations to:
        *   Pre-defined "gold standard" explanations for specific test scenarios.
        *   The AITA's known underlying rules or the pedagogical principles it was fine-tuned on (if discernible).
    *   **Method**: Expert review, possibly with access to AITA's internal logic or training objectives if feasible.
*   **Student-Facing Explanation Effectiveness**:
    *   If explanations are shown to students (e.g., "Why did you ask that?"), metrics would include:
        *   Student comprehension of the explanation.
        *   Impact on student engagement or metacognition.
    *   **Method**: Student surveys, A/B testing with/without explanations, think-aloud protocols with students.

## 5. Conclusion

Evaluating the AITA Reasoner feature requires a mixed-methods approach, heavily relying on qualitative feedback from educators and expert review for the current implementation. As the feature evolves, particularly if explanations become dynamically generated, the suite of evaluation metrics will also need to expand. The core goal remains to ensure that these explanations are clear, accurate, useful, and ultimately contribute to more effective AI-assisted learning.
```
