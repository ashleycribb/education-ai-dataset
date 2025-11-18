# xAPI Profile for AI in Education: Specification

This document provides the technical specification for the xAPI Profile for AI in Education. This profile extends the [xAPI specification](https://github.com/adlnet/xAPI-Spec) to provide a common data model for interactions with AI-powered educational tools.

## 1. Core Concepts

This profile is built on the core data structures of the xAPI standard:

*   **Statement:** The fundamental data structure, representing an event in the `Actor-Verb-Object` format. All data is recorded as a stream of xAPI statements.
*   **Actor:** Represents the person or group performing the action. In this profile, the `Actor` will typically be a student or a teacher, but it can also be an AI agent.
*   **Verb:** Defines the action that was performed (e.g., "completed," "asked," "suggested").
*   **Object:** The thing that the action was performed on. This is typically an `Activity` in xAPI.
*   **Activity:** A representation of a learning resource, such as a course, assessment, or a specific interaction with an AI tutor.
*   **Learning Record Store (LRS):** The database where the xAPI statements are stored.

## 2. Representing Core Educational Data

Our previous data structures (`Student`, `Educator`, `Course`, etc.) can be mapped directly to xAPI concepts:

*   **Student and Educator:** Both are represented as an `Actor` in xAPI statements. The actor's role can be distinguished by their `objectType` (`Agent` for a person) and potentially through custom extensions.
*   **Course, Learning Objective, and Assessment:** These are all represented as `Activities` in xAPI. An `Activity` has a unique ID and a `definition` that can be used to describe its type (e.g., "course," "assessment").

## 3. Vocabulary for AI Interactions

This profile introduces a new vocabulary (a set of `Verbs` and `Activity Types`) to describe the unique interactions that occur in AI-powered learning environments.

### 3.1. Verbs

| Verb ID                                           | Display Name           | Description                                                                                             |
| ------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| `https://w3id.org/xapi/ai/verbs/suggested`          | suggested              | Indicates that an AI agent suggested a resource or action to a learner.                                 |
| `https://w3id.org/xapi/ai/verbs/assisted`           | assisted               | Indicates that a learner's action was assisted by an AI agent.                                            |
| `https://w3id.org/xapi/ai/verbs/generated`          | generated              | Indicates that an AI agent generated content, such as a quiz question or a personalized learning path.    |
| `https://w3id.org/xapi/ai/verbs/summarized`         | summarized             | Indicates that an AI agent provided a summary of a resource or a student's progress.                      |

### 3.2. Activity Types

| Activity Type ID                                  | Display Name           | Description                                                                                             |
| ------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| `https://w3id.org/xapi/ai/activity-types/ai-tutor`  | AI Tutor               | Represents an interaction with a conversational AI tutor.                                               |
| `https://w3id.org/xapi/ai/activity-types/agent`     | AI Agent               | Represents an AI agent acting as a participant in the learning process (e.g., as the `Actor` of a statement). |

## 4. Security and Privacy

This profile inherits the robust security and privacy model of the xAPI and LRS specifications. All data should be:

*   Transmitted securely over TLS.
*   Stored in a conformant LRS, which manages authentication and authorization.
*   Handled in accordance with data minimization and consent principles.

## 5. Serialization Formats

### JSON (Default)

JSON is the default format for all xAPI statements.

### TOON (Recommended for LLMs)

For applications that send large volumes of xAPI statements to LLMs (e.g., for analysis or to provide context to an AI tutor), we recommend serializing the JSON statements into [TOON (Token-Oriented Object Notation)](https://github.com/toon-format/toon) to reduce token count and improve parsing accuracy.
