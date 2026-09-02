import socket
import json
import random

def main():
    """
    Main function to run the MCP client.
    """
    host = "127.0.0.1"
    port = 12345

    # Load a sample xAPI statement
    try:
        with open("../examples/04_assistant_gave_feedback.json", "r") as f:
            statement = json.load(f)
    except FileNotFoundError:
        print("Error: `04_assistant_gave_feedback.json` not found. Make sure you are running this script from the `mcp-poc` directory.")
        return

    print("--- MCP Client ---")
    print("Preparing to send statement:")
    print(json.dumps(statement, indent=2))

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"\n[Client] Connected to server at {host}:{port}")

        # Send the statement to the server
        client_socket.sendall(json.dumps(statement).encode('utf-8'))
        print("[Client] Statement sent.")

        # Receive the response from the server
        response_data = client_socket.recv(1024)
        response = json.loads(response_data.decode('utf-8'))

        print(f"[Client] Server response: {response}")

    except ConnectionRefusedError:
        print("\n[Client] Error: Connection refused. Is the server running?")
    except Exception as e:
        print(f"\n[Client] An error occurred: {e}")
    finally:
        client_socket.close()
        print("[Client] Connection closed.")


if __name__ == "__main__":
    main()
