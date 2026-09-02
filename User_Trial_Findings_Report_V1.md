# User Trial Findings Report: Reading Explorer AITA (4th Grade Pilot - V1)

## 1. Executive Summary (Placeholder)

This initial pilot trial with 4th-grade students interacting with the "Reading Explorer AITA" indicated positive engagement and usability. Students generally found the AITA helpful for main idea and inference tasks. Key recommendations include refining dialogue flows for vocabulary tasks, enhancing frontend accessibility, and further diversifying training data to handle student frustration more gracefully.

## 2. Introduction

### 2.1. Purpose of User Trial
The primary objectives of this pilot user trial were to:
*   Evaluate the initial usability and user experience of the "Reading Explorer AITA" web-based frontend for 4th-grade students.
*   Gather qualitative feedback on student engagement levels.
*   Collect preliminary impressions on the perceived effectiveness and age-appropriateness of the AITA's "teach how to learn" pedagogical approach.
*   Identify immediate areas for improvement in AITA dialogue, user interface, and overall interaction flow.
*   Assess the functionality of core technical components in a simulated use case, including context fetching (from mock LMS), content moderation, and xAPI-like logging.

### 2.2. Participants
*   **Students**: 4 4th-grade students (ages 9-10) with a mix of reading confidence levels (self-reported by parents/teachers).
*   **Adults**: 1 4th-grade teacher and 2 parents observed parts of the sessions and provided feedback.
    *   *(Participant IDs used in this report are anonymized, e.g., S1, S2, T1, P1).*

### 2.3. Methodology
The trial followed the protocol outlined in `UserTrialProtocol_Pilot.md`. Each student participated in a one-on-one session with a facilitator.
1.  **Pre-Trial**: Informed consent/assent obtained. Students were briefed on the AITA and the tasks.
2.  **During Trial**: Students interacted with the "Reading Explorer AITA" via the web-based student frontend, performing tasks related to:
    *   Identifying the main idea of the "Lily the Lost Kitten" passage.
    *   Understanding vocabulary ("pigment") and making inferences ("why colors were hidden") for the "Why Leaves Change Color" passage.
    *   Context for these tasks was conceptually provided by the `lms_mcp_server_mock.py` to the `aita_interaction_service.py`, which the student frontend communicated with.
3.  **Post-Trial**: Students completed a short survey and participated in a brief interview. Observing teachers/parents also provided feedback via a short survey/interview.
4.  **Data Collection**: xAPI-like interaction logs (`service_xapi_statements.jsonl` from the AITA Interaction Service), survey responses, interview notes, and facilitator observations were collected.

## 3. Quantitative Findings (Illustrative Examples)

### 3.1. AITA Usage Statistics (from xAPI logs - Aggregated)
*   **Total Sessions Logged**: 4 (one per student)
*   **Average Session Duration**: 22 minutes (range: 18-27 minutes)
*   **Average Turns per Session**: 14 (User: ~7, AITA: ~7)
*   **Input Safeguard Triggers**: 1 instance (Student S3 attempted to use inappropriate language, which was correctly handled by the `ModerationService` and logged).
*   **Output Safeguard Triggers (AITA response replaced)**: 0 instances (No AITA-generated responses were flagged by the `ModerationService` as unsafe in this pilot).

### 3.2. Student Survey Results (Example Likert Scale Summary - 4 students)

| Question                                        | Strongly Agree | Agree | Neutral | Disagree | Strongly Disagree |
| :---------------------------------------------- | :------------: | :---: | :-----: | :------: | :---------------: |
| "The AITA was easy to use."                     |       2        |   2   |    0    |    0     |         0         |
| "The AITA helped me understand the story/words." |       1        |   2   |    1    |    0     |         0         |
| "Chatting with the AITA was fun."               |       2        |   1   |    1    |    0     |         0         |
| "The AITA asked good questions."                |       1        |   3   |    0    |    0     |         0         |

*(Note: Based on simulated responses for 4 students)*

## 4. Qualitative Findings (Illustrative Examples & Themes)

### 4.1. Usability of Student Frontend
*   **Theme 1: Intuitive Chat Interface**: Most students (4/4) found the chat interface straightforward and easy to use.
    *   *Illustrative Quote (S2)*: "It was like texting, but with a robot teacher."
*   **Theme 2: Desire for Richer Interaction**: One student (S4) mentioned wishing they could use emojis or voice input.
    *   *Facilitator Note*: S4 attempted to type an emoji representation `:)`.
*   **Theme 3: Text Size/Readability**: One student (S1) squinted occasionally at the AITA's longer responses.

### 4.2. Student Engagement
*   **Theme 1: High Initial Engagement**: All students appeared curious and engaged at the start of the sessions, readily typing responses.
    *   *Facilitator Note*: S2 and S4 started typing follow-up questions before the AITA had fully finished its previous response.
*   **Theme 2: Varied Resilience to Socratic Guiding**:
    *   Most students (3/4) responded well to the AITA's guiding questions, attempting to answer or rephrase their thoughts.
    *   One student (S3, during the vocabulary task for "pigment") expressed mild frustration:
        *   *AITA*: "The passage says 'chlorophyll, the green pigment'. What job do you think 'pigment' does for the color green there?"
        *   *S3*: "I don't know, just tell me!"
        *   *Facilitator Note*: The AITA then provided a more direct hint, which seemed to satisfy the student.

### 4.3. Pedagogical Effectiveness (Initial Impressions)
*   **Theme 1 (Main Idea - "Lily the Lost Kitten")**:
    *   Students generally understood the task. 3 out of 4 students, with AITA guidance, successfully formulated a main idea that included both the problem (lost kitten) and resolution (found home).
    *   *Example Transcript Snippet (S1 & AITA)*:
        *   *S1*: "It's about a kitten that was lost."
        *   *AITA*: "That's a great start! What happens to Lily at the end of the story?"
        *   *S1*: "She finds her house and is happy."
        *   *AITA*: "Wonderful! So if you put those together, what's the big idea the story is telling us?"
        *   *S1*: "A lost kitten finds its way home and is happy."
*   **Theme 2 (Vocabulary in Context - "pigment" in "Why Leaves Change Color")**:
    *   This was more challenging. 2 students needed significant scaffolding. The AITA's initial prompt to use context was sometimes met with "I don't know."
    *   The AITA's strategy of breaking down the sentence and focusing on "green pigment" eventually helped students connect it to "color."
*   **Theme 3 ("Teach How to Learn" Adherence)**:
    *   The AITA consistently avoided providing direct answers prematurely, opting for guiding questions as designed.
    *   The example with S3 (above) highlights the need for the AITA to potentially recognize prolonged student struggle and adjust its level of scaffolding or provide a direct explanation sooner in some cases.

### 4.4. Safeguard Performance
*   **Input Moderation**:
    *   The `ModerationService` (simulated as active via `aita_mcp_client.py` logs) correctly identified and flagged one instance of inappropriate language from S3 ("This is stupid..."). The AITA client displayed a polite refusal message as intended. This was correctly logged in `xapi_statements.jsonl`.
*   **Output Moderation**:
    *   No AITA responses during these pilot sessions were flagged by the `ModerationService` as unsafe. This indicates the base model's responses, under the given system prompts, were generally appropriate for the context. *(Note: With a larger trial or more diverse prompts, triggers might occur).*

### 4.5. Teacher/Parent Feedback (Illustrative)
*   **Teacher T1**: "The guiding questions for main idea are very good. For vocabulary, I think some students might need a more direct definition sooner if they are truly stuck. The dashboard view would be helpful to see where students get stuck."
*   **Parent P1 (observed S2)**: "S2 seemed to enjoy it and was thinking hard. I liked that it didn't just give her the answer. It would be great if this could link to her actual school reading assignments."

## 5. Key Strengths Identified (Placeholder)
*   **Good Initial Student Engagement**: Students were generally eager to interact with the AITA.
*   **Clear Dialogue Presentation**: The chat interface (simulated via CLI for client, but designed for web) was easy for students to understand and use.
*   **Contextual Relevance**: The AITA's initial greeting, referencing the specific passage (mocked via LMS context), made the interaction feel relevant.
*   **"Teach How to Learn" Approach Generally Maintained**: The AITA successfully used guiding questions in most instances.

## 6. Key Areas for Improvement (Placeholder)

*   **AITA Pedagogy/Dialogue**:
    *   **Vocabulary Tasks**: Refine dialogue flows to offer more varied scaffolding for vocabulary in context, potentially offering a direct definition more readily if a student struggles after 2-3 guided prompts.
    *   **Frustration Handling**: Explore strategies for the AITA to recognize signs of student frustration (e.g., repeated "I don't know," short negative responses) and adjust its approach (e.g., offer a different type of hint, simplify the question, or offer to explain directly).
*   **Student Frontend UI/UX**:
    *   Consider adding text size adjustment options for accessibility.
    *   Explore options for richer input (e.g., emoji reactions, simple multiple-choice responses to AITA questions where appropriate) for future web versions.
*   **Safeguards**:
    *   While effective in this small pilot, continue monitoring `ModerationService` performance with more diverse interactions. Review the sensitivity of output moderation for false positives if they arise.
*   **Dataset for Fine-Tuning (Future)**:
    *   Future fine-tuning datasets should include more examples of AITAs gracefully handling student confusion or frustration.
    *   Include more diverse examples of successful and unsuccessful scaffolding for various LOs.

## 7. Recommendations for Next Iteration

1.  **Iterate on AITA Dialogue Flows**: Specifically for vocabulary tasks, revise the dialogue logic in `data_processing_scripts.py` (for future fine-tuning datasets) and potentially the SLM's system prompt (for immediate effect if using a base model) to include more adaptive scaffolding for students who struggle with initial contextual guessing.
2.  **Enhance Student Frontend Prototype**: If developing the Streamlit prototype further, investigate adding a simple font size control. For a full web frontend, prioritize accessibility features from the start.
3.  **Refine Teacher Dashboard**: Based on teacher feedback, prioritize dashboard features that clearly show where students struggled and what kind_of_support the AITA provided. Make moderation flags highly visible.

## 8. Appendix (Optional - Mention only)

*   (Placeholder: Survey questions used for students and adults would be listed here.)
*   (Placeholder: Facilitator's observation guide/checklist would be listed here.)
