import socket
import json
import logging
import os

def main():
    """
    Main function to run the MCP server.
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'server.log')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file_path,
        filemode='w' # Overwrite log on each start
    )

    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    logging.info(f"--- MCP Server listening on {host}:{port} ---")
    print(f"--- MCP Server listening on {host}:{port} ---") # Keep this for interactive mode

    while True:
        conn, addr = server_socket.accept()
        logging.info(f"Connection from {addr}")
        try:
            # Receive the data from the client
            data = conn.recv(4096)
            if data:
                # Decode the JSON data
                statement = json.loads(data.decode('utf-8'))
                actor_name = statement.get("actor", {}).get("name", "Unknown Actor")
                verb_display = statement.get("verb", {}).get("display", {}).get("en-US", "Unknown Verb")

                logging.info(f"Received statement: '{actor_name} {verb_display}'")

                # Send a success response back to the client
                response = {"success": True, "message": "Statement received and processed."}
                conn.sendall(json.dumps(response).encode('utf-8'))
        except json.JSONDecodeError:
            logging.error("Received invalid JSON.")
            response = {"success": False, "message": "Invalid JSON received."}
            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            response = {"success": False, "message": f"An error occurred: {e}"}
            conn.sendall(json.dumps(response).encode('utf-8'))
        finally:
            logging.info("Closing connection.")
            conn.close()

if __name__ == "__main__":
    main()
