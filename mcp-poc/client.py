import json
import requests
import os

def main():
    """
    Main function to run the MCP client.
    """
    print("--- MCP Client (HTTP) ---")

    # The server is expected to be running on localhost, port 8000 (default for uvicorn)
    server_url = "http://127.0.0.1:8000/statement"

    # --- Load the Example Statement ---
    # Construct the path to the example file relative to the client script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    example_file_path = os.path.join(script_dir, '..', 'examples', '04_assistant_gave_feedback.json')

    try:
        with open(example_file_path, 'r', encoding='utf-8') as f:
            statement = json.load(f)
        print("Preparing to send statement:")
        print(json.dumps(statement, indent=2))
    except FileNotFoundError:
        print(f"Error: `{os.path.basename(example_file_path)}` not found.")
        print("Make sure the `examples` directory is present and you are running this script correctly.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from `{os.path.basename(example_file_path)}`.")
        return

    # --- Send the Statement via HTTP POST ---
    try:
        print(f"\n[Client] Sending POST request to {server_url}")
        response = requests.post(server_url, json=statement, timeout=10)

        # Check if the request was successful
        response.raise_for_status()

        print("[Client] Server response:")
        print(response.json())

    except requests.exceptions.RequestException as e:
        print(f"\n[Client] An error occurred while sending the request: {e}")
        print("[Client] Please ensure the server is running.")

if __name__ == "__main__":
    main()
