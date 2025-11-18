# Education AI Dataset Standard: Specification

This document provides the technical specification for the Education AI Dataset Standard. It defines the core data structures and their relationships, providing a common format for representing educational data.

## Core Principles

*   **JSON-based:** The standard uses a JSON format for data exchange, ensuring broad compatibility and ease of use.
*   **Well-defined Schema:** All data structures are clearly defined, specifying required fields, data types, and relationships.
*   **Extensible:** The standard is designed to be extensible, allowing for the addition of new data structures and fields to meet specific needs.

## Serialization Formats

### JSON (Default)

JSON is the default format for interoperability. It is widely supported and easy to parse. All systems compliant with this standard should be able to process data in JSON format.

### TOON (Recommended for LLMs)

For applications involving Large Language Models (LLMs), we highly recommend [TOON (Token-Oriented Object Notation)](https://github.com/toon-format/toon). TOON is a serialization format that is optimized for LLM prompts, offering significant advantages:

*   **Token Efficiency:** TOON's compact syntax can reduce the number of tokens by ~40% compared to JSON, leading to lower API costs and faster processing.
*   **Higher Accuracy:** The format includes "guardrails" like explicit array lengths and field headers, which help LLMs parse data more reliably.

When providing large amounts of data from our standard to an LLM (e.g., a student's full interaction history for a tutoring agent), using TOON is the preferred method.

## Core Data Structures

### 1. Student

Represents an individual student.

```json
{
  "studentId": "string (unique)",
  "attributes": {
    "demographics": {
      "birthDate": "date",
      "gender": "string"
    },
    "enrollmentStatus": "string (e.g., 'active', 'inactive')"
  },
  "privacySettings": {
    "dataSharingConsent": "boolean",
    "anonymizationLevel": "string (e.g., 'full', 'partial')"
  }
}
```

### 2. Educator

Represents a teacher, instructor, or other educator.

```json
{
  "educatorId": "string (unique)",
  "attributes": {
    "name": "string",
    "roles": ["string"]
  }
}
```

### 3. Course

Represents a course of study.

```json
{
  "courseId": "string (unique)",
  "title": "string",
  "description": "string",
  "learningObjectives": ["string (learningObjectiveId)"]
}
```

### 4. Learning Objective

Represents a specific learning goal or outcome.

```json
{
  "learningObjectiveId": "string (unique)",
  "description": "string",
  "masteryLevel": "number"
}
```

### 5. Assessment

Represents a test, quiz, or other form of assessment.

```json
{
  "assessmentId": "string (unique)",
  "title": "string",
  "assessmentType": "string (e.g., 'quiz', 'exam', 'homework')",
  "items": [
    {
      "itemId": "string (unique)",
      "itemType": "string (e.g., 'multiple-choice', 'essay')",
      "learningObjectives": ["string (learningObjectiveId)"]
    }
  ]
}
```

### 6. Interaction Event

Represents a specific interaction between a student and a learning resource.

```json
{
  "eventId": "string (unique)",
  "studentId": "string",
  "timestamp": "datetime",
  "eventType": "string (e.g., 'view_resource', 'submit_assessment')",
  "data": {
    "resourceId": "string",
    "assessmentId": "string",
    "studentResponse": "any"
  }
}
```

## Privacy and Security

The security and privacy of student data are of paramount importance. This standard is designed with a "privacy by design" approach, and all implementations should adhere to the following principles:

### 1. Data Minimization

Collect and store only the data that is absolutely necessary for the intended educational purpose. Avoid collecting personally identifiable information (PII) whenever possible.

### 2. Data Anonymization and Pseudonymization

Where PII is not required for the functionality of an application, data should be anonymized. In cases where data needs to be linked to a specific student, pseudonymization techniques should be used to replace PII with a non-identifying token.

The `Student` object includes a `privacySettings` field to help manage this:
*   `anonymizationLevel`: Can be set to `'full'` (no PII), `'partial'` (some PII removed), or `'none'` (raw data). Implementations should default to the highest level of anonymization possible.

### 3. Role-Based Access Control (RBAC)

Access to data should be strictly controlled based on the user's role. For example:
*   An **Educator** should only have access to the data of the students in their own courses.
*   A **Student** should only have access to their own data.
*   An **Administrator** may have broader access, but this should be carefully audited.

### 4. Secure Data Transmission and Storage

All data should be encrypted in transit (e.g., using TLS) and at rest (e.g., using AES-256).

### 5. Consent and Transparency

Students (and/or their legal guardians) should be informed about what data is being collected and how it is being used. The `Student` object's `dataSharingConsent` field should be used to track whether a student has provided consent for their data to be used in specific ways (e.g., for research).
