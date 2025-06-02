from typing import Optional, Any
import datetime # For example xAPI timestamp

from k12_mcp_client_sdk import (
    SimplifiedMCPClient,
    create_interaction_xapi_statement,
    log_xapi_statement
)

# A simple logger class for demonstration purposes
class ConsoleLogger:
    def info(self, message: str):
        print(f"CLIENT_EXAMPLE_INFO: {message}")
    def error(self, message: str, exc_info: bool = False):
        print(f"CLIENT_EXAMPLE_ERROR: {message}")
        if exc_info:
            pass # In a real app, print traceback
    def warning(self, message: str):
        print(f"CLIENT_EXAMPLE_WARNING: {message}")

if __name__ == "__main__":
    print("--- K-12 MCP Client SDK: Simple Client Example ---")
    
    logger = ConsoleLogger()
    logger.info("Logger initialized for client example.")

    # Configuration for the client
    # Assuming the server (e.g., simple_server_example.py from k12_mcp_server_sdk)
    # is running in stdio mode for this example.
    client = SimplifiedMCPClient(client_type="stdio", logger=logger)

    # Interaction details for xAPI logging
    session_id = "session_client_example_001"
    user_name_for_log = "ClientSDKUser"
    user_account_for_log = "clientsdkuser@example.com" # Example unique ID
    example_log_file = "example_client_interactions.jsonl"

    try:
        logger.info("Starting SimplifiedMCPClient (stdio)...")
        client.start() # Important for stdio client

        # 1. Example: Call get_resource_data
        logger.info("Attempting to get resource: /hello?name=SDK Client User")
        resource_data = client.get_resource_data(
            path="/hello", 
            query_params={"name": "SDK Client User"}
        )

        if resource_data:
            logger.info(f"Received resource data: {resource_data}")
            greeting = resource_data.get("greeting", "No greeting found.")
            print(f"\nServer Response to /hello: {greeting}\n")

            # Log this interaction using xAPI utils
            statement = create_interaction_xapi_statement(
                actor_name=user_name_for_log,
                actor_account_name=user_account_for_log,
                verb_id="http://adlnet.gov/expapi/verbs/requested",
                verb_display="requested resource",
                object_activity_id="http://example.com/mcp_sdk/resource/hello_world_sdk_example",
                object_activity_name="Hello World Resource (SDK Example)",
                object_activity_description="A simple resource that returns a greeting.",
                session_id=session_id,
                aita_persona="ExampleServerGreeter", # Example persona
                result_response=json.dumps(resource_data), # Store the full response as string
                context_extensions={"client_version": "k12_mcp_client_sdk_v0.1.0"}
            )
            log_xapi_statement(statement, example_log_file, logger)

        else:
            logger.warning("Failed to retrieve /hello resource or resource_data was None.")
            print("\nFailed to get a response from the server for /hello.\n")

        # 2. Example: Call get_resource_data for student info (simulating interaction with StudentDataHandler)
        student_to_query = "student123"
        logger.info(f"Attempting to get resource: /student/{student_to_query}/info")
        student_info = client.get_resource_data(path=f"/student/{student_to_query}/info")

        if student_info:
            logger.info(f"Received student data: {student_info}")
            print(f"Server Response to /student/{student_to_query}/info: {student_info}\n")
            statement_student = create_interaction_xapi_statement(
                actor_name=user_name_for_log, actor_account_name=user_account_for_log,
                verb_id="http://adlnet.gov/expapi/verbs/retrieved", verb_display="retrieved student info",
                object_activity_id=f"http://example.com/mcp_sdk/resource/student_info/{student_to_query}",
                object_activity_name=f"Student Information Resource for {student_to_query}",
                object_activity_description="Resource providing basic student data.",
                session_id=session_id, aita_persona="ExampleServerDataService",
                result_response=json.dumps(student_info)
            )
            log_xapi_statement(statement_student, example_log_file, logger)
        else:
            logger.warning(f"Failed to retrieve /student/{student_to_query}/info or data was None.")
            print(f"Failed to get a response for /student/{student_to_query}/info.\n")

        # 3. Example: How a tool invocation might look (conceptual, tool not in simple_server_example)
        # logger.info("Conceptually invoking a tool 'echo_tool'...")
        # tool_outputs = client.invoke_tool_outputs(
        #     tool_name="echo_tool", 
        #     inputs={"message": "Hello from client SDK!"}
        # )
        # if tool_outputs:
        #     logger.info(f"Received tool outputs: {tool_outputs}")
        #     print(f"Server Response to echo_tool: {tool_outputs.get('echo', 'No echo output.')}\n")
        # else:
        #     logger.warning("Failed to invoke 'echo_tool' or received no outputs.")
        #     print("Failed to get a response for 'echo_tool'.\n")

    except Exception as e:
        logger.error(f"An error occurred during the client example: {e}", exc_info=True)
    finally:
        logger.info("Stopping SimplifiedMCPClient...")
        client.stop() # Important for stdio client
        logger.info("Client example finished.")

    print(f"\nCheck '{example_log_file}' for xAPI-like statements logged during this example run.")
