# User Trial Protocol: Reading Explorer AITA (4th Grade Pilot)

## 1. Introduction & Purpose

### Purpose of the User Trial
This document outlines the protocol for conducting initial, small-scale user trials of the "Reading Explorer AITA." The primary purposes of this pilot trial are to:
*   Gather initial qualitative feedback on the AITA's usability and user experience for 4th-grade students.
*   Observe student engagement levels when interacting with the AITA.
*   Collect preliminary impressions on the effectiveness and appropriateness of the AITA's pedagogical approach (i.e., its "teach how to learn" philosophy).
*   Identify any immediate areas for improvement in the AITA's dialogue, interface, or overall interaction flow.
*   Assess the functionality of technical components like context fetching, moderation, and logging in a near-real-use scenario.

### Reading Explorer AITA Description
The "Reading Explorer AITA" is an AI-powered tutor designed to support 4th-grade students in developing reading comprehension skills. It focuses on areas such as identifying the main idea, making inferences, and understanding vocabulary in context. The AITA interacts with students through a chat-based interface, aiming to guide their learning by asking questions and prompting critical thinking rather than providing direct answers.

## 2. Ethical Considerations

*   **IRB Approval (or Equivalent)**: Prior to conducting any trials involving minors, approval from an Institutional Review Board (IRB) or an equivalent ethics review committee must be obtained. This protocol serves as a planning document and does not replace formal ethics review.
*   **Parental/Guardian Informed Consent**: Written, informed consent must be obtained from parents or legal guardians of all participating students. Consent forms will detail the purpose of the trial, the nature of participation, data handling procedures, potential risks/benefits, and the voluntary nature of participation.
*   **Student Assent**: Age-appropriate assent must be obtained from each participating student, explaining the trial in simple terms and ensuring they understand they can stop at any time.
*   **Data Privacy and Confidentiality**:
    *   All data collected (interaction logs, survey responses, interview notes) will be handled with strict confidentiality.
    *   Student identifiers in logs (e.g., `user_id` from `xapi_statements.jsonl`) will be anonymized or pseudonymized in any reports or analyses. For this pilot, we will use pre-assigned, anonymized IDs.
    *   Data will be stored securely, and access will be restricted to the research team.
    *   No personally identifiable information (PII) beyond what is necessary for the study (and covered by consent) will be collected.
*   **Voluntary Participation**: Participation is entirely voluntary. Students and their parents/guardians must be informed that they can choose not to participate or to withdraw from the trial at any point without any negative consequences.
*   **Minimizing Risk**: The trial design aims to minimize any potential risks. The `ModerationService` will be active to filter inappropriate content. Facilitators will be present to address any technical or emotional discomfort.

## 3. Participants

*   **Target Profile**: Students currently in 4th grade (or an equivalent age/reading level, e.g., 9-10 years old).
*   **Number**: For this initial pilot, a small group of **3-5 students** is proposed. This allows for detailed observation and qualitative feedback.
*   **Recruitment Strategy (Conceptual)**:
    *   Approach local elementary schools or school districts (with formal permission from administration and ethics approval).
    *   Connect with homeschooling co-ops or parent groups.
    *   Ensure a diverse group of participants if possible (e.g., varied reading levels within the 4th-grade range, different backgrounds), but this may be limited for a small pilot.
*   **Teacher/Parent Involvement**:
    *   Involve **1-2 teachers** (if in a school setting) or **homeschool parents** who have 4th-grade students.
    *   Their role could be to:
        *   Observe some student sessions (with consent).
        *   Review anonymized session transcripts or dashboard summaries.
        *   Provide feedback on the AITA's pedagogical approach and its potential fit within their educational context.

## 4. Trial Environment & System Setup

*   **AITA System**:
    *   **Student Frontend**: A web-based student frontend application (e.g., an adapted version of `student_frontend_streamlit.py` that communicates with the backend service via HTTP requests instead of directly running the SLM).
    *   **AITA Interaction Service**: The `aita_interaction_service.py` running as a backend service. This service will host the base SLM (e.g., Phi-3-mini) and conceptually, the fine-tuned LoRA adapter for the "Reading Explorer AITA."
    *   **LMS Context Server**: `lms_mcp_server_mock.py` running to provide simulated student and activity context via MCP to the AITA Interaction Service.
    *   **Moderation Service**: The `ModerationService` (using `unitary/toxic-bert` or similar) will be active within the `AITA Interaction Service` to filter user inputs and AITA outputs.
    *   **Logging**: The `AITA Interaction Service` will log interactions to `xapi_statements.jsonl` (or a test LRS if set up).
*   **User Devices**: Chromebooks, laptops (Windows/Mac), or tablets (iOS/Android) with a modern web browser capable of accessing the student frontend.
*   **Location**: A quiet room where students can concentrate, such as a school computer lab, a designated classroom area, or a quiet space at home for remote participants. Ensure reliable internet access.
*   **Facilitator Setup**: A separate computer for the facilitator to take notes and monitor any server-side logs or the dashboard if applicable during the session.

## 5. Trial Procedure (Step-by-Step)

### Pre-Trial:
1.  **Ethics & Consent**: Secure all necessary ethics approvals and obtain signed informed consent from parents/guardians and assent from students. Assign anonymized participant IDs.
2.  **System Check**: Ensure the AITA Interaction Service, Mock LMS Server, and Student Frontend are all running correctly and communicating. Test with a sample student ID.
3.  **Facilitator Training**: Ensure the facilitator understands the AITA's purpose, the trial tasks, and how to provide minimal, non-leading assistance.
4.  **Briefing (5-10 minutes)**:
    *   Welcome the student (and parent/teacher if present).
    *   Explain that they will be trying out a new computer tutor called "Reading Explorer AITA" that helps with reading.
    *   Emphasize that the AITA is like a helper that asks questions to guide them, and it's okay if they don't know answers right away – the AITA is there to help them think.
    *   Briefly show them how to type in the chat interface.
    *   Reiterate that their participation is helping to make the AITA better and they can stop at any time.

### During Trial (Student Interaction):
1.  **Task Assignment**:
    *   Assign **Task 1 (Main Idea)**: "Today, we're going to read a short story called 'Lily the Lost Kitten'. After you read it on the screen (or provide a printout), I'd like you to use the AITA to help you figure out what the main idea of the story is. You can ask it questions like 'What is this story mostly about?' or 'How do I find the main idea?'"
        *   *(Facilitator ensures the passage "Lily the Lost Kitten" is configured in the mock LMS for the student's context, or displayed directly in the frontend if context fetching is simplified for the trial).*
    *   Assign **Task 2 (Vocabulary in Context/Inference - if time permits)**: "Now, let's try another story/task. We'll read 'Why Leaves Change Color'. After reading, please ask the AITA to help you understand what the word 'pigment' means in the story. You can also ask it why the other colors were hidden."
        *   *(Facilitator ensures context is set for this task if applicable).*
2.  **Student Interaction**:
    *   The student interacts with the AITA through the web frontend.
    *   Encourage students to type their questions and responses as they normally would.
3.  **Session Duration**: Aim for approximately 15-25 minutes of interaction per student, or per task. Allow for flexibility based on student engagement.
4.  **Facilitator Role**:
    *   Observe the student's interaction: Note ease of use, points of confusion, signs of engagement or frustration, and types of questions asked.
    *   Provide minimal technical assistance (e.g., if the student has trouble typing or submitting).
    *   **Crucially, do not guide the student on how to answer the AITA's questions or what to ask about the reading content.** The goal is to see how the student and AITA interact naturally.
    *   Log any critical technical issues encountered (e.g., service errors, frontend bugs).

### Post-Trial (Data Collection):
1.  **Student Survey (5-10 minutes)**:
    *   Administer a short, age-appropriate survey. Example questions (using Likert scales or simple choices):
        *   "Was the AITA easy to use?" (Yes/Mostly/A Little/No)
        *   "Did the AITA help you understand the story/word?" (A Lot/A Little/Not Much/Not at All)
        *   "Was chatting with the AITA fun?" (Yes/Kind Of/No)
        *   "What did you like best about the AITA?" (Open-ended)
        *   "What was confusing or hard about using the AITA?" (Open-ended)
2.  **Student Interview (Optional, 5-10 minutes)**:
    *   If feasible and the student is willing, ask a few open-ended questions:
        *   "Can you tell me about what you did with the AITA today?"
        *   "What was it like when the AITA asked you questions?"
        *   "Did you learn anything new or think about something in a new way?"
        *   "If you could change one thing about the AITA, what would it be?"
3.  **Teacher/Parent Feedback (Survey/Interview)**:
    *   If a teacher/parent observed or will review data:
        *   "Did the AITA's questions seem appropriate for a 4th grader?"
        *   "How well do you think the AITA supported the learning objective (e.g., finding the main idea)?"
        *   "Did you notice any positive or negative aspects of the student's interaction with the AITA?"
        *   "Do you have suggestions for improving the AITA?"

## 6. Data to be Collected

*   **Quantitative**:
    *   **xAPI Interaction Logs** (from `xapi_statements.jsonl` or test LRS):
        *   Number of interaction turns per session.
        *   Session duration.
        *   Frequency of specific AITA response types (if categorizable from logs).
        *   Counts of input/output moderation safeguard triggers and flagged categories.
        *   (If tasks are designed for it) Task completion rates or correctness of student responses to specific AITA prompts (requires manual review of logs against expected answers).
    *   **Student Survey Responses**: Aggregated ratings and categorized open-ended feedback.
*   **Qualitative**:
    *   **Facilitator Observation Notes**: Detailed notes on usability challenges, student engagement cues (verbal and non-verbal), points of confusion, errors encountered, and any spontaneous comments from students.
    *   **Student Interview Responses**: Transcripts or detailed notes of student answers.
    *   **Teacher/Parent Interview/Survey Responses**: Transcripts or written feedback.

## 7. Evaluation Focus (What to Look For)

*   **Usability**:
    *   Can students easily read text and type responses in the frontend?
    *   Do they understand how to progress through the interaction?
    *   Are there any confusing interface elements?
*   **Engagement**:
    *   Do students appear focused and interested?
    *   Do they respond thoughtfully to the AITA's prompts?
    *   Do they initiate questions or primarily just respond?
    *   What is the general sentiment (e.g., enjoyment, frustration, curiosity)?
*   **Pedagogical Effectiveness (Initial Impressions)**:
    *   Does the AITA's guidance (questions, prompts) appear to help students think about the task?
    *   Is the AITA successfully adhering to the "teach how to learn" principle (i.e., not giving direct answers too quickly)?
    *   Do students seem to understand the AITA's language and questions?
    *   Are there patterns in student responses that suggest common misunderstandings of the AITA's prompts or the content?
*   **Safeguards**:
    *   Were any input or output safeguards triggered during the sessions? What were the details (logged in xAPI data)?
    *   Were there any instances where problematic content was observed but *not* flagged by the safeguards?
*   **Technical Issues**:
    *   Any bugs, interface glitches, system crashes, or noticeable performance delays (e.g., AITA response time)?

## 8. Reporting

The findings from this pilot user trial (quantitative data summaries, qualitative themes from observations and interviews) will be compiled into an internal report. This report will:
*   Summarize key findings related to usability, engagement, and initial pedagogical impressions.
*   Identify critical issues and areas for immediate improvement.
*   Provide recommendations for the next iteration of AITA development, frontend design, and future, larger-scale user trials.

This protocol provides a framework for conducting valuable initial user trials to inform the ongoing development of the AITA ecosystem.
