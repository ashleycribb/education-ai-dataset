# LTI AITA Integration Design (LTI 1.3 / Advantage)

## 1. Introduction

### Purpose
This document outlines the design for integrating AI Tutors (AITAs) with Learning Management Systems (LMSs) using the Learning Tools Interoperability (LTI) standard, specifically focusing on LTI 1.3 and LTI Advantage. This integration will allow students to seamlessly launch AITA sessions from within their familiar LMS environment.

### Benefits of LTI Integration
*   **Seamless User Experience**: Students access AITAs as just another tool or activity within their LMS course, without needing separate logins.
*   **Automatic Context Passing**: Critical information such as user identity (student ID), course details, and the specific learning resource (e.g., a reading passage or quiz) can be automatically and securely passed from the LMS to the AITA.
*   **Leveraging LMS Authentication**: The AITA system relies on the LMS to authenticate the user, reducing the need for a separate authentication mechanism within the AITA itself for LTI launches.
*   **Gradebook Integration (LTI Advantage)**: Future potential for AITA activities to report scores or completion status back to the LMS gradebook (via LTI Advantage's Assignment and Grade Services).

## 2. Components Involved

The LTI integration involves several key components:

*   **LMS (Learning Management System)**:
    *   **Role**: LTI Platform.
    *   **Description**: The primary educational platform used by students and teachers (e.g., Canvas, Moodle, Blackboard, D2L Brightspace, Google Classroom if it supports LTI for tools). It initiates the LTI launch.
*   **AITA LTI Tool Provider Service (New Component)**:
    *   **Role**: LTI Tool.
    *   **Description**: A new backend web service that handles LTI 1.3 launch requests from the LMS. It's responsible for OIDC authentication, validating ID Tokens, extracting contextual information, and then redirecting the user to the Student Frontend. This service would likely be built using a web framework like FastAPI and an LTI library.
*   **Student Frontend Web Application**:
    *   **Role**: User Interface for AITA interaction.
    *   **Description**: An evolution of the `student_frontend_streamlit.py` prototype, refactored into a robust web application (e.g., using React, Vue, or server-side rendering with a Python web framework). It receives context from the AITA LTI Tool Provider and communicates with the AITA Interaction Service.
*   **AITA Interaction Service**:
    *   **Role**: Backend for AITA logic and SLM interaction.
    *   **Description**: The existing `aita_interaction_service.py` (or its evolution) which hosts the SLM (base model + adapters), handles dialogue management, and applies moderation. It receives interaction requests from the Student Frontend.
*   **(Optional) LMS-Adapter-MCP-Server**:
    *   **Role**: Context Enrichment via MCP.
    *   **Description**: If the LTI launch doesn't provide all necessary context, the AITA LTI Tool Provider Service (or the AITA Interaction Service) could query this MCP server. The LMS-Adapter-MCP-Server would then use other standards (e.g., OneRoster, Ed-Fi, direct LMS APIs) to fetch richer context not included in the LTI launch. For many core LTI use cases, this might not be immediately necessary if LTI custom parameters are used effectively.

## 3. User Flow (LTI 1.3 Launch Sequence)

The LTI 1.3 launch process follows the OpenID Connect (OIDC) standard:

1.  **Student Clicks AITA Tool Link**: A student, logged into their LMS, clicks on a link or button that represents the AITA tool (e.g., "Start Reading Tutor Session for 'Lily the Lost Kitten'"). This link is configured in the LMS by an administrator or teacher.
2.  **LMS Initiates OIDC Login Flow**: The LMS, acting as the OIDC Relying Party, initiates an authentication request. It redirects the student's browser to an OIDC login initiation endpoint on the **AITA LTI Tool Provider Service**. This request includes parameters like `login_hint`, `lti_message_hint`, and `redirect_uri`.
3.  **AITA LTI Tool Provider Handles Authentication Request**: The AITA LTI Tool Provider Service receives the login initiation request. It typically stores some state (e.g., using a `state` parameter cookie) and redirects the student's browser back to the LMS's OIDC authorization endpoint.
4.  **LMS Authenticates User & Issues ID Token**: The LMS authenticates the student (if not already fully authenticated in the session). Upon successful authentication, the LMS constructs an ID Token (a JSON Web Token - JWT) containing claims about the user, context, and the launch. The LMS then makes an HTTP POST request (via the student's browser, often using a self-submitting form) to the **AITA LTI Tool Provider Service's** configured LTI launch URL (redirect URI), sending the `id_token` and `state` parameter.
5.  **AITA LTI Tool Provider Validates ID Token & Extracts Context**:
    *   The AITA LTI Tool Provider Service receives the POST request containing the `id_token`.
    *   It validates the `state` parameter to prevent CSRF attacks.
    *   It validates the `id_token`'s signature using the LMS's public keys (obtained from the LMS's JWKS URI, which was part of the LTI tool registration).
    *   It validates standard OIDC claims in the ID Token (e.g., `iss` (issuer), `aud` (audience - client ID of the tool), `exp` (expiration), `nonce`).
    *   It extracts standard LTI claims (user identity, course context, resource link context) and any custom parameters passed by the LMS (see Section 4 for mapping).
    *   It translates these LTI parameters into the AITA's internal context format (e.g., the structure expected by `context_provided_to_aita`).
    *   It establishes a session for the Student Frontend (e.g., by generating a session token or setting a secure cookie).
    *   It redirects the student's browser to the **Student Frontend Web Application**, passing the session/context information (e.g., via URL parameters, or by having the frontend fetch it using the session token).
6.  **Student Frontend Loads & Initiates Interaction**:
    *   The Student Frontend Web Application loads in the student's browser.
    *   It uses the received session/context information to initialize the AITA session.
    *   It then communicates with the **AITA Interaction Service** (backend) for dialogue management, SLM interaction, and logging, passing the established user and session context with each request.

## 4. Data Mapping (LTI Claims to AITA Context)

The following table maps key LTI 1.3 claims (typically found in the ID Token) to the fields used in the AITA ecosystem's `context_provided_to_aita` object (as conceptualized in `DataStrategy.md` and used by `aita_mcp_client.py` and `lms_mcp_server_mock.py`).

| LTI 1.3 Claim (ID Token)                                     | AITA Context Field (`context_provided_to_aita`)                                     | Notes                                                                                                                                                                                             |
| :----------------------------------------------------------- | :---------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `sub` (Subject - User ID)                                    | `user_id` (or `student_id_anonymized` after pseudonymization)                       | This is the LMS's unique identifier for the user. A pseudonymization strategy might be applied before storing or using it internally if required by privacy policies.                            |
| `name`                                                       | (Display only, if needed and permitted)                                             | Full name of the user.                                                                                                                                                                            |
| `given_name`                                                 | (Display only, if needed and permitted)                                             | Given name of the user.                                                                                                                                                                           |
| `family_name`                                                | (Display only, if needed and permitted)                                             | Family name of the user.                                                                                                                                                                          |
| `email`                                                      | (Internal use only, if needed for communication and permitted)                      | User's email address.                                                                                                                                                                             |
| `https://purl.imsglobal.org/spec/lti/claim/roles`            | (Used to determine user role, e.g., "Learner", "Instructor")                        | Helps AITA adapt behavior if it supports different roles (e.g., teacher preview mode).                                                                                                             |
| `https://purl.imsglobal.org/spec/lti/claim/context`          |                                                                                     | Contains information about the course/context from which the LTI launch originated.                                                                                                               |
| `  .id`                                                      | `current_lms_course_id` (or similar field)                                          | LMS's unique ID for the course.                                                                                                                                                                   |
| `  .label`                                                   | `current_lms_course_label` (e.g., course code like "ENG101")                        | Label for the course.                                                                                                                                                                             |
| `  .title`                                                   | `current_lms_course_title` (e.g., "Introduction to English Literature")             | Title of the course.                                                                                                                                                                              |
| `https://purl.imsglobal.org/spec/lti/claim/resource_link`    |                                                                                     | Information about the specific link/resource in the LMS that was clicked to launch the tool.                                                                                                      |
| `  .id`                                                      | `content_item_id` (e.g., "passage_kitten_001")                                      | LMS's unique ID for the resource link. This is crucial for identifying the specific passage or activity.                                                                                        |
| `  .title`                                                   | `content_item_title`                                                                | Title of the resource link (e.g., "Reading: Lily the Lost Kitten").                                                                                                                                 |
| `  .description`                                             | `learning_context_description` (can be part of it)                                  | Description of the resource link.                                                                                                                                                                 |
| `https://purl.imsglobal.org/spec/lti/claim/custom`           | Mapped to various fields based on keys.                                             | Custom parameters configured in the LMS for the LTI tool placement. This is a powerful way to pass specific AITA context.                                                                         |
| `  custom_learning_objective_id` (Example custom param)      | `target_learning_objectives_for_activity[0].id`                                     | Example: `custom_learning_objective_id: "RC.4.LO1.MainIdea.Narrative"`                                                                                                                            |
| `  custom_learning_objective_text` (Example custom param)    | `target_learning_objectives_for_activity[0].text`                                   | Example: `custom_learning_objective_text: "Identify the main idea..."`                                                                                                                            |
| `  custom_teacher_notes` (Example custom param)              | `teacher_notes_for_student_on_lo`                                                   | Example: `custom_teacher_notes: "Focus on the character's feelings."`                                                                                                                               |
| `https://purl.imsglobal.org/spec/lti/claim/launch_presentation` | (Used to inform frontend display, e.g., `document_target`, `return_url`)            | Information about how the tool should be displayed and where to return the user.                                                                                                                  |
| `https://purl.imsglobal.org/spec/lti-ags/claim/endpoint`     | (Store for Assignment and Grade Services if AITA reports grades back to LMS)        | Contains API endpoints for LTI Advantage services like Gradebook.                                                                                                                                 |

## 5. API Interaction Sequences (Conceptual - High Level)

1.  **Browser (Student)** `->` Clicks AITA link in **LMS**.
2.  **Browser** `->` (HTTP Redirect GET) `->` **AITA LTI Tool Provider Service** (OIDC login initiation endpoint).
3.  **AITA LTI Tool Provider Service** `->` (HTTP Redirect GET) `->` **Browser**.
4.  **Browser** `->` (HTTP Redirect GET) `->` **LMS** (OIDC authorization endpoint).
5.  **LMS** `->` (HTTP POST with `id_token`) `->` **Browser** (self-submitting form to AITA LTI Tool Provider's launch URL).
6.  **Browser** `->` (HTTP POST with `id_token`) `->` **AITA LTI Tool Provider Service** (LTI launch URL / redirect URI).
    *   *(AITA LTI Tool Provider validates token, extracts context, creates session)*
7.  **AITA LTI Tool Provider Service** `->` (HTTP Redirect GET with session info/token) `->` **Browser**.
8.  **Browser** `->` (HTTP GET) `->` **Student Frontend Web Application**.
    *   *(Student Frontend loads, uses session info to initialize)*
9.  **Student Frontend** `->` (HTTP API requests, e.g., POST to `/interact`) `->` **AITA Interaction Service**.
    *   *(AITA Interaction Service may internally query LMS-Adapter-MCP-Server if needed for richer context not in LTI launch)*
10. **AITA Interaction Service** `->` (HTTP API response) `->` **Student Frontend**.
    *   *(Student Frontend displays AITA response)*
11. **AITA Interaction Service** `->` (xAPI statement) `->` **Learning Record Store (LRS)** (asynchronous).

## 6. Key Design Considerations for AITA LTI Tool Provider Service

*   **Security (Crucial)**:
    *   **OIDC Conformance**: Strictly adhere to LTI 1.3 and OIDC specifications for the authentication flow.
    *   **JWT Validation**: Thoroughly validate the `id_token` signature (using LMS's JWKS), issuer (`iss`), audience (`aud`), expiration (`exp`), and nonce (`nonce`) claims.
    *   **State Parameter**: Use the `state` parameter effectively to prevent Cross-Site Request Forgery (CSRF) attacks during the OIDC flow.
    *   **Secure Storage**: Securely store LMS platform registration details (client ID, deployment ID, JWKS URL, OIDC auth URL, issuer URL). Use environment variables or a secure configuration management system, not hardcoded values.
    *   **HTTPS**: All communication endpoints must use HTTPS.
    *   **Recommended Library**: Utilize a robust server-side LTI 1.3 library (e.g., `pylti1.3` for Python/FastAPI, or similar libraries for other frameworks/languages) to handle much of the OIDC complexity.

*   **Configuration & Platform Registration**:
    *   The service must allow administrators to register multiple LMS platforms. Each registration will include:
        *   LMS Issuer URL (`iss`).
        *   LMS Client ID (`aud` for the tool).
        *   LMS Deployment ID(s).
        *   LMS Public Keyset URL (JWKS URI).
        *   LMS OIDC Authorization Endpoint URL.
    *   This configuration could be stored in a database or secure configuration files.

*   **Context Mapping Logic**:
    *   Implement a flexible mapping mechanism to translate LTI claims (both standard and custom parameters like `custom_learning_objective_id`) into the AITA's internal `context_provided_to_aita` structure.
    *   This might involve a configuration layer where mappings can be defined or customized per LMS platform or per tool placement, as custom parameter names can vary.

*   **Error Handling**:
    *   Implement graceful error handling for all stages of the LTI launch:
        *   Invalid or missing LTI parameters.
        *   Failed ID Token validation (e.g., signature mismatch, expired token, invalid nonce).
        *   Errors during context mapping or session creation.
    *   Provide informative error messages to the user's browser or log them securely for administrators.

*   **Session Management**:
    *   After a successful LTI launch and context extraction, the AITA LTI Tool Provider Service needs to establish a session for the Student Frontend.
    *   This could involve generating a secure session token (e.g., a short-lived JWT) or setting a server-side session cookie.
    *   This session token/identifier is then passed to the Student Frontend, which uses it to authenticate its own requests to the AITA Interaction Service.

By addressing these design considerations, the AITA ecosystem can integrate effectively and securely with standard LMS platforms, providing a greatly improved user experience and richer contextualization for AI-powered tutoring.
