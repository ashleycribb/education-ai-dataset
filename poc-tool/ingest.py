import json
import random
import time

def generate_embedding(text):
    """
    Simulates generating a vector embedding from text.
    In a real application, this would call an embedding model (e.g., from OpenAI).
    """
    time.sleep(0.1)  # Simulate network latency
    return [random.uniform(-1, 1) for _ in range(1536)]

def main():
    """
    Main function to simulate the LRS ingestion process.
    """
    print("--- Starting LRS Ingestion Simulation ---")

    try:
        with open("../docs/sample-data.json", "r") as f:
            statements = json.load(f)
    except FileNotFoundError:
        print("Error: `sample-data.json` not found. Make sure you are running this script from the `poc-tool` directory.")
        return

    for stmt in statements:
        statement_id = stmt.get("id", "N/A")
        print(f"\n[Document DB] Storing statement: {statement_id}")

        # Check for qualitative data in the context extensions
        if "context" in stmt and "extensions" in stmt["context"]:
            extensions = stmt["context"]["extensions"]
            qualitative_data = None

            if "https://w3id.org/xapi/ai/extensions/assistance-content" in extensions:
                qualitative_data = extensions["https://w3id.org/xapi/ai/extensions/assistance-content"]
            elif "https://w3id.org/xapi/ai/extensions/teacher-correction" in extensions:
                qualitative_data = extensions["https://w3id.org/xapi/ai/extensions/teacher-correction"]

            if qualitative_data:
                print(f"  -> Found qualitative data: '{qualitative_data[:50]}...'")
                print("  -> Generating embedding...")
                embedding = generate_embedding(qualitative_data)
                print(f"[Vector DB]   Storing embedding for statement {statement_id} (vector dim: {len(embedding)})")

    print("\n--- LRS Ingestion Simulation Complete ---")

if __name__ == "__main__":
    main()
