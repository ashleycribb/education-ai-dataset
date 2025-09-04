# Advanced Teacher Oversight Tools & Analytics: Requirement Gathering for AITA Ecosystem

## 1. Introduction

### Purpose
This document outlines the process and types of requirements to be gathered from K-12 educators for the design and development of advanced teacher oversight tools and analytics dashboards for the AI Tutor (AITA) ecosystem.

### Goal
The ultimate goal is to ensure that these tools are genuinely useful for educators, providing actionable insights into student learning, AITA performance, and overall classroom dynamics. These tools should empower teachers to make data-informed decisions, personalize support, and effectively integrate AITAs into their pedagogical practices.

### Methodology Note
The requirements detailed herein are conceptual starting points. They would be formally gathered and refined through established user research methodologies, including:
*   **Interviews**: One-on-one discussions with teachers, curriculum specialists, and school administrators.
*   **Focus Groups**: Group discussions to elicit diverse perspectives and collaborative brainstorming.
*   **Surveys**: To gather quantitative data and opinions from a broader set_of_educators.
*   **Analysis of User Trial Data**: Insights from future, more extensive user trials with the AITA system (building upon findings from protocols like `UserTrialProtocol_Pilot.md`).
*   **Usability Testing**: Observing educators interacting with prototype dashboards.

## 2. Key Areas for Requirement Gathering (Question Prompts for Educators)

To understand the needs of educators, we would pose questions across several key areas:

### Understanding Student Learning & Progress
*   What specific information about a student's interaction with an AITA (e.g., types of questions asked, AITA's scaffolding, common errors, time spent) would help you best understand their learning process and current understanding for a given topic or Learning Objective (LO)?
*   How would you want to see a student's progress tracked over time for specific LOs, based on their interactions with AITAs? What would make this tracking meaningful and easy to interpret?
*   What data points or patterns in AITA interactions would be clear indicators to you that a student is consistently struggling with particular concepts or skills?
*   Are there specific points in a dialogue (e.g., where a student expresses confusion, or where the AITA provides a key explanation) that you'd want to easily access or be alerted to?

### Class-Level Insights
*   What aggregated information about your class's overall AITA usage would be most beneficial (e.g., which AITAs/topics are most used, average time spent, common LOs being worked on)?
*   How could class-level data from AITAs (e.g., frequently asked questions by students, common misconceptions identified by AITA interactions, areas where many students required extensive AITA scaffolding) inform your lesson planning or group interventions?
*   Would it be useful to compare engagement or performance patterns across different student groups within your class (anonymized or with appropriate permissions)?

### AITA Effectiveness & Behavior
*   What information or evidence would help you trust that the AITA is pedagogically sound and effective for your students?
*   How would you want to assess the types of guidance, questioning strategies, or scaffolding the AITA is providing? Is seeing the "pedagogical notes" (as designed in our AITA JSON) useful?
*   What level of detail do you need regarding the AITA's internal reasoning or the full prompts it uses when generating responses (beyond what's available in the current prototype dashboard's "Full Prompt to LLM" expander)?
*   How important is it to see if and how the AITA adapts its approach based on student responses or context?

### Safeguards & Ethical Use Monitoring
*   What information do you need regarding triggered content moderation safeguards (for both student input and AITA output)? What level of detail is useful versus overwhelming?
*   How would you want to be alerted to or review potentially problematic interactions, either from a safety perspective or a pedagogical one (e.g., AITA consistently failing to guide a student effectively)?
*   What tools or views would help you ensure students are using the AITA appropriately and for its intended educational purpose?

### Actionability & Intervention
*   If the dashboard shows a student is struggling with a specific LO via AITA interactions, what actions would you typically want to take?
*   How could the AITA system or dashboard directly help you assign follow-up tasks, provide targeted resources, or differentiate instruction based on AITA interaction insights?
*   Would a feature to "flag" a session for later review or to share with a specialist be useful?

### Customization & Control
*   What aspects of AITA behavior, content focus, or pedagogical strategy would you ideally want some level of control or customization over for your class or individual students (e.g., adjusting difficulty, pre-selecting LOs for a session)?
*   Would you want to provide specific instructions or contextual information to the AITA for certain students or activities?

### Integration & Reporting
*   How important is it for AITA oversight data to integrate with or export to other systems you currently use (e.g., LMS gradebook, school-wide student information systems, or existing reporting tools)?
*   What data export formats (e.g., CSV, PDF summaries) would be most useful for your own record-keeping, parent-teacher conferences, or school reporting requirements?
*   What types of pre-defined reports would be most valuable (e.g., weekly student progress summary, class-wide LO mastery based on AITA interactions)?

## 3. Types of Requirements to Elicit

The information gathered through the above questions will be translated into different types of requirements:

*   **Functional Requirements**: What the system *does*.
    *   *Example*: "The dashboard *shall* allow teachers to filter session logs by student ID and date range."
    *   *Example*: "The system *shall* generate an alert if a student has more than X flagged inputs in a single session."
*   **Data Requirements**: Specific data points that need tobe_logged, stored, processed, and displayed.
    *   *Example*: "The dashboard *must* display the full dialogue transcript, including timestamps for each turn."
    *   *Example*: "The system *must* log the specific 'flagged_categories' from the `ModerationService`."
*   **Non-Functional Requirements**: How well the system performs certain functions.
    *   **Usability**: Ease of use, intuitiveness of the interface, clarity of information.
        *   *Example*: "The dashboard *should* be navigable by teachers with average technical proficiency without extensive training."
    *   **Performance**: Speed, responsiveness, scalability.
        *   *Example*: "Session transcripts *should* load within 3 seconds."
    *   **Accessibility**: Design for users with disabilities (e.g., WCAG compliance).
        *   *Example*: "The dashboard *must* be keyboard navigable and screen-reader compatible."
    *   **Security**: Protection of data, user authentication for dashboard access.
        *   *Example*: "Access to the teacher dashboard *must* be restricted to authenticated school staff."
*   **Reporting/Visualization Requirements**: How data is presented to be meaningful.
    *   *Example*: "Class-level progress on LOs *should* be visualized as a bar chart showing mastery levels (e.g., not started, developing, proficient)."
    *   *Example*: "The system *should* allow exporting student session summaries as PDF."

## 4. Example Prioritized Requirements (Illustrative)

This is a conceptual prioritization based on anticipated educator needs. Actual prioritization will result from the gathering process.

*   **Must-Have (Core Functionality & Oversight)**:
    *   View detailed student interaction history with AITAs, including full dialogue, timestamps, and all logged safeguard/moderation actions (input and output).
    *   Dashboard view summarizing class-wide engagement (e.g., which AITAs/passages are used, frequency, number of turns per session).
    *   Clear visual indicators (e.g., flags, color-coding) on the dashboard for sessions with triggered safeguards or errors.
    *   Ability to filter interaction logs/sessions by student, date range, and potentially by AITA persona or Learning Objective.
    *   Secure, role-based access to the dashboard.
*   **Should-Have (Enhanced Insights & Actionability)**:
    *   Analytics on common student misconceptions or error patterns identified during AITA sessions for specific LOs.
    *   Tracking of student progress or interaction patterns towards specific LOs based on AITA interaction data (e.g., number of attempts, types of AITA scaffolding needed).
    *   Alerts or a "watchlist" for students consistently struggling, frequently triggering safeguards, or showing low engagement.
    *   Ability to view the full prompt sent to the LLM for any AITA turn (as in current prototype).
    *   Basic data export functionality (e.g., session transcript to text/PDF, overview table to CSV).
*   **Could-Have (Advanced Features & Research Potential)**:
    *   Analysis of pedagogical strategies used by AITAs and their potential correlation with student engagement or understanding (research-heavy).
    *   Teacher annotation/feedback tools directly within dialogue transcripts in the dashboard.
    *   Custom report builder for teachers to create their own views and summaries.
    *   Direct link/integration from the dashboard to assign targeted follow-up resources in an LMS based on AITA interaction insights.

## 5. Next Steps

The requirements gathered through the methods outlined in Section 1 will directly inform:
*   The design of an extensible and scalable architecture for the Teacher Oversight Dashboard and underlying analytics components.
*   The development roadmap for specific advanced features, visualizations, and "add-on" tools for educators.
*   Prioritization of which data points are most critical to capture and expose through the dashboard.
*   Ongoing refinement of the xAPI-like statement structure to ensure it captures the necessary data for these advanced tools.

This iterative, educator-centered approach to requirements gathering is essential for building oversight tools that truly support teaching and learning in the AITA ecosystem.
