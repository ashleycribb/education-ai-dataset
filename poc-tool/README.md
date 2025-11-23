# Proof-of-Concept LRS Ingestion Tool

This tool is a simple simulation that demonstrates the vision for our "AI-Enhanced" Learning Record Store (LRS), as described in our [Conceptual Database Model](../DATABASE_MODEL.md).

It is designed for a **non-technical audience** to help visualize how the data flows in our proposed hybrid database system.

## What It Does

The script (`ingest.py`) reads the xAPI statements from our `sample-data.json` file and pretends to store them in our two different types of databases:

1.  **The "Document DB" (like MongoDB):** This is where the full, original xAPI statement is stored. The tool will print a message like `[Document DB] Storing statement...` for every learning record it processes. This database is great for looking up specific, structured information (e.g., "show me everything Sally Student did").

2.  **The "Vector DB" (like Pinecone):** If a learning record contains rich, qualitative feedback (like the content of an AI's hint or a teacher's correction), the tool will pretend to create a "vector embedding" from that text. A vector embedding is a special, numerical representation of the text that AI can understand. The tool will print a message like `[Vector DB] Storing embedding...` when it does this. This database is what allows us to do powerful, "semantic" searches (e.g., "find me all the times a teacher gave feedback *similar to*...").

By showing these two different messages, the tool demonstrates how our hybrid system stores both the original records and the AI-ready embeddings.

## How to Run It

1.  Make sure you have Python 3 installed on your system.
2.  Open your terminal or command prompt.
3.  Navigate into this `poc-tool` directory.
4.  Run the following command:

```bash
python ingest.py
```

You will see a series of messages printed to your screen that simulate the ingestion process.
