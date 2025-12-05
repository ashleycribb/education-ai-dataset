# xAPI Profile for AI in Education

## Live Dashboard

**[Click here to see a live, interactive dashboard that demonstrates the power of this xAPI Profile.](./docs/index.md)**

This dashboard visualizes a sample dataset of AI-learner interactions, providing both quantitative and qualitative analysis of the data captured by our profile.

## The Vision: Extending xAPI for the Age of AI

This project defines a foundational **xAPI Profile** designed to capture the unique interactions that occur in AI-powered learning environments. Our goal is to extend the power and interoperability of the Experience API (xAPI) to create a common language for AI agents, small learning models (SLMs), and AI-powered teacher's assistants.

By building on the proven foundation of xAPI, we can ensure that data from these next-generation educational tools is interoperable, secure, and part of the wider learning ecosystem.

## The Problem: A Missing Vocabulary for AI Interactions

The existing xAPI standard is excellent for capturing a wide range of learning experiences. However, as AI tutors and agents become more common, we need a specialized vocabulary to describe the new types of interactions they enable, such as:

*   An AI agent personalizing a learning path for a student.
*   A small learning model generating a new assessment question.
*   A teacher's assistant AI summarizing a student's progress.

Without a common data model for these events, data from AI educational tools will become siloed, making it difficult to analyze the effectiveness of these new technologies and integrate them with existing systems like Learning Record Stores (LRS).

## The Solution: A Foundational xAPI Profile

This project provides a formal xAPI Profile that defines the specific `Verbs`, `Activity Types`, and statement templates needed to track AI-driven learning experiences. By providing this shared vocabulary, we can enable a future where:

*   Data from an AI tutor can be seamlessly stored in any conformant LRS.
*   Learning analytics platforms can compare the effectiveness of different AI agents.
*   Small learning models can be trained on standardized, high-quality datasets of AI-student interactions.

This profile will serve as a foundational layer, which can be further extended by the community to meet the needs of specific AI applications.

## Use Case: Analyzing AI Teacher's Assistants

To demonstrate the power of this profile, we have defined a specific vocabulary for the "AI Teacher's Assistant" use case. This extension allows for the detailed capture of interactions where an AI provides direct help to a learner.

By using the specialized `Verbs` (e.g., `provided-hint`, `gave-feedback`) and `Context Extensions` defined in this profile, researchers and educators can perform both quantitative and qualitative analysis on the effectiveness of AI assistants. For example, one could analyze not just *how often* an AI provides hints, but also the *exact content* of those hints and the learner prompts that triggered them.

### Teacher in the Loop: Improving AI with Human Expertise

A crucial aspect of responsible AI in education is ensuring that human educators can guide and improve AI agents. This profile includes a "Teacher in the Loop" vocabulary to facilitate this feedback cycle. When an AI's interaction with a student is recorded, a teacher can then review that specific interaction and record their own feedback as a new xAPI statement.

This allows the AI agent to learn from expert feedback, creating a powerful mechanism for continuous improvement and ensuring that the AI's behavior aligns with sound pedagogical practices.

## Implementation Guidance: The AI-Enhanced LRS

To fully leverage the analytical power of this xAPI Profile, we have designed a conceptual database model for an "AI-Enhanced" Learning Record Store (LRS). This model proposes a hybrid architecture that combines a traditional document database (for structured xAPI data) with a vector database (for semantic analysis of qualitative feedback).

**[Click here to view the Conceptual Database Model](./DATABASE_MODEL.md)**

This document serves as a guide for developers and organizations looking to build a next-generation LRS that is truly "AI-ready."

## Proof-of-Concept Tool

To help make the conceptual database model easier to understand, we have created a simple, runnable tool that simulates the data ingestion process. This tool is designed for a non-technical audience and provides a clear, step-by-step demonstration of how data flows into our proposed AI-Enhanced LRS.

**[Click here to learn about and run the Proof-of-Concept Tool](./poc-tool/README.md)**

We have also created a functional, runnable demonstration of the high-performance MCP interface.

**[Click here to learn about and run the MCP Proof-of-Concept](./mcp-poc/README.md)**

### Communication Model

For advanced implementations, we also propose a conceptual communication model that includes a high-performance, model-centric interface for trusted communication between AI agents and the LRS, in addition to the standard xAPI REST interface.

**[Click here to view the Conceptual Communication Model](./COMMUNICATION_MODEL.md)**

## Guiding Principles

*   **xAPI Alignment:** We will adhere to the principles and data structures of the xAPI specification to ensure maximum interoperability.
*   **Focus on AI:** This profile is specifically focused on defining the data models for interactions that are unique to AI-powered educational tools.
*   **Privacy and Security First:** We will leverage the robust security and privacy features of the xAPI standard and the LRS specification.
*   **Open and Collaborative:** This is an open-source project, and we welcome contributions from educators, developers, and researchers.

## Get Involved

This project is in its early stages, and we are actively seeking collaborators. Whether you are an educator with deep domain expertise, a developer with experience in AI and xAPI, or a researcher with a passion for the future of education, we invite you to join us in extending xAPI for the age of AI.
