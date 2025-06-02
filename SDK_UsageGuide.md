# K-12 AITA MCP SDKs: Usage Guide

## 1. Introduction

This guide introduces two Python SDKs (Software Development Kits) designed to streamline the development of AI Tutor (AITA) components within the K-12 Model Context Protocol (MCP) project:

*   **`k12_mcp_server_sdk`**: Simplifies the creation of MCP-compliant servers. These servers can provide educational context (like student data or learning activities from an LMS) or expose tools (like specialized content generators) to AITAs.
*   **`k12_mcp_client_sdk`**: Simplifies the development of MCP clients, such as the AITAs themselves. It provides wrappers for common communication patterns and utilities for structured interaction logging.

Both SDKs are built upon the foundational `modelcontextprotocol` library, abstracting some of its complexities to provide a more K-12 education-focused development experience.

## 2. Part 1: `k12_mcp_server_sdk`

### 2.1. Purpose
The `k12_mcp_server_sdk` aims to make it easier for developers to create robust K-12 focused MCP servers. It achieves this by providing base classes with common functionality (like error handling and request dispatching) and helper utilities for constructing standardized responses. This allows developers to focus more on the specific logic of their educational resources or tools.

### 2.2. Key Components

*   **`SimplifiedMCPServer`**:
    *   This class wraps the `MCPStdIOServer` from the base `modelcontextprotocol` library (and is designed to conceptually support `MCPHTTPServer` in the future).
    *   It offers simplified methods for registering handlers:
        *   `add_resource_handler(path_pattern, handler_instance)`: For registering classes that serve data resources.
        *   `add_tool_handler(handler_instance)`: For registering classes that expose tools.
    *   It manages the server lifecycle (e.g., `run()` method).

*   **`BaseK12ResourceHandler`**:
    *   An abstract base class for creating resource handlers. Developers should subclass this and implement the `handle_get(path_params, query_params, **kwargs)` method to define the logic for their specific resource.
    *   It includes built-in error handling, automatically returning appropriate MCP error responses for common issues like `NotImplementedError` (status 501) or unhandled exceptions (status 500).

*   **`BaseK12ToolHandler`**:
    *   An abstract base class for creating tool handlers. Developers should subclass this and implement the `handle_invoke(inputs, **kwargs)` method to define the core logic of their tool.
    *   The tool's definition (its name, description, input parameters, and output parameters, conforming to `modelcontextprotocol.protocol.ToolDefinition`) is typically passed to the `super().__init__(tool_definition_dict=...)` constructor of this base class.
    *   It includes built-in error handling for tool invocations, ensuring that errors are wrapped in a standard `ToolResult` format.

*   **Response Helpers** (from `k12_mcp_server_sdk.responses`):
    *   `create_success_response(payload, status_code=200)`: Creates a `ResourceResponse` for successful operations.
    *   `create_error_response(error_message, status_code, error_code=None, details=None)`: Creates a `ResourceResponse` for errors with a structured JSON error payload.
    *   `create_success_tool_result(outputs, tool_name)`: Creates a `ToolResult` for successful tool invocations.
    *   `create_error_tool_result(error_message, tool_name, error_code=None, details=None)`: Creates a `ToolResult` for tool invocation errors, structuring the error within the `outputs`.
    *   These helpers ensure consistent JSON response structures, compliant with MCP expectations.

### 2.3. Basic Usage Example

This condensed example shows how to define a simple resource handler and run it using `SimplifiedMCPServer`.

```python
# Condensed Example for SDK_UsageGuide.md
from k12_mcp_server_sdk import SimplifiedMCPServer, BaseK12ResourceHandler, ResourceResponse, create_success_response
import logging # Standard logger example

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyEchoHandler(BaseK12ResourceHandler):
    def handle_get(self, path_params, query_params, **kwargs) -> ResourceResponse:
        # self.logger is available from BaseK12ResourceHandler if a logger is passed to __init__
        if self.logger:
            self.logger.info(f"MyEchoHandler received GET with query_params: {query_params}")
        
        # Create a payload that echoes back the query parameters
        response_payload = {
            "message": "Echoing your query parameters.",
            "received_params": query_params
        }
        return create_success_response(payload=response_payload)

if __name__ == "__main__":
    # Initialize the server with a logger
    sdk_server = SimplifiedMCPServer(logger=logger)
    
    # Instantiate your handler, passing the logger
    echo_handler = MyEchoHandler(logger=logger)
    
    # Register the handler for a specific path
    sdk_server.add_resource_handler("/echo", echo_handler)
    
    logger.info("Starting SDK example server. Listening on /echo via stdio.")
    logger.info("To test, send an MCP JSON request to stdin, e.g.:")
    logger.info('{"mcp_version": "0.1.0", "request_id": "req1", "resource_path": "/echo", "query_params": {"message": "Hello SDK"}}')
    
    sdk_server.run()
```

### 2.4. Installation Note
Currently, this SDK is part of the project's codebase. To use it, ensure the `k12_mcp_server_sdk` directory is in your Python path or install it as an editable package if using a project structure that supports it (e.g., with `pyproject.toml` and `pip install -e .`).

## 3. Part 2: `k12_mcp_client_sdk`

### 3.1. Purpose
The `k12_mcp_client_sdk` aims to simplify the development of MCP clients, such as AITAs or other tools that consume MCP resources/tools. It provides wrappers for common communication patterns (StdIO and HTTP) and utilities for creating xAPI-like statements for robust interaction logging.

### 3.2. Key Components

*   **`SimplifiedMCPClient`**:
    *   Wraps the `MCPStdIOClient` and `MCPHTTPClient` from the base `modelcontextprotocol` library.
    *   Provides `start()` and `stop()` methods, which are particularly important for managing `MCPStdIOClient`'s subprocess and communication pipes.

*   **Wrapper Methods**:
    *   `get_resource_data(path: str, query_params: Optional[Dict] = None, timeout: Optional[float] = 10.0) -> Optional[Dict]`: Simplifies making a GET request to an MCP resource. It constructs the `ResourcePath`, sends the request, and returns the JSON payload directly if successful, or `None` if an error occurs or the response is malformed. It also handles basic logging of the request and response.
    *   `invoke_tool_outputs(tool_name: str, inputs: Dict, timeout: Optional[float] = 10.0) -> Optional[Dict]`: Simplifies invoking an MCP tool. It constructs the `ToolInvocation`, sends it (handling `send_invocation` and `receive_response` for stdio), and returns the `outputs` dictionary from the `ToolResult` if successful, or `None` if an error occurs.

*   **`xapi_utils`** (from `k12_mcp_client_sdk.xapi_utils`):
    *   `create_interaction_xapi_statement(...)`: A helper function to construct a Python dictionary that closely mirrors the structure of an xAPI statement. This is useful for logging detailed educational interactions. It takes various parameters like actor, verb, object details, session ID, etc.
    *   `log_xapi_statement(statement: Dict, filepath: str, logger: Optional[Any])`: A utility to append the generated statement dictionary as a JSON string to a specified file, following the JSON Lines (jsonl) format.

### 3.3. Basic Usage Example

This condensed example demonstrates setting up the `SimplifiedMCPClient`, making a `get_resource_data` call, and logging the interaction using `xapi_utils`.

```python
# Condensed Example for SDK_UsageGuide.md
from k12_mcp_client_sdk import SimplifiedMCPClient, create_interaction_xapi_statement, log_xapi_statement
import logging # Standard logger example
import json # For formatting the response in the log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize client for stdio communication
    sdk_client = SimplifiedMCPClient(client_type="stdio", logger=logger)
    
    log_file = "sdk_client_example.jsonl"
    session_id_example = "session_sdk_test_001"

    try:
        sdk_client.start() # Important for stdio client
        
        logger.info("Querying /echo resource from a piped MCP server...")
        # This assumes an MCP server (like the server SDK example) is running 
        # and its stdout is piped to this client's stdin.
        resource_payload = sdk_client.get_resource_data(
            path="/echo", 
            query_params={"message": "Hello from K-12 Client SDK"}
        )
        
        if resource_payload:
            logger.info(f"Server response: {resource_payload}")
            
            # Log the interaction using xAPI utils
            statement = create_interaction_xapi_statement(
                actor_name="SDKExampleUser", 
                actor_account_name="sdkuser@example.com", # Unique identifier for the user
                verb_id="http://example.com/verbs/queried_resource", 
                verb_display="queried an MCP resource",
                object_activity_id="http://example.com/activities/echo_resource_test",
                object_activity_name="Echo Resource Test (Client SDK)",
                object_activity_description="Client SDK example querying an /echo resource from an MCP server.",
                session_id=session_id_example,
                result_response=json.dumps(resource_payload), # Store the JSON response as a string
                # Add more details as needed
                context_extensions={"client_sdk_version": "0.1.0"}
            )
            log_xapi_statement(statement, log_file, logger)
            logger.info(f"Interaction logged to {log_file}")
        else:
            logger.warning("No response received from server for /echo, or an error occurred.")

    except Exception as e:
        logger.error(f"An error occurred in the client example: {e}", exc_info=True)
    finally:
        sdk_client.stop() # Important for stdio client
        logger.info("Client SDK example finished.")
```

### 3.4. Installation Note
Currently, this SDK is part of the project's codebase. To use it, ensure the `k12_mcp_client_sdk` directory is in your Python path or install it as an editable package if using a project structure that supports it (e.g., with `pyproject.toml` and `pip install -e .`).

## 4. General Advice

*   **Interoperability**: The `k12_mcp_server_sdk` and `k12_mcp_client_sdk` are designed to facilitate communication between components that adhere to the Model Context Protocol. An AITA built using the client SDK can interact with an LMS or tool provider built using the server SDK (or any other MCP-compliant implementation).
*   **Foundation**: Both SDKs build upon and simplify the use of the core `modelcontextprotocol` library. For advanced MCP features or customization, referring to the base library's documentation may be necessary.
*   **Logging**: The xAPI-like logging provided by the client SDK is crucial for creating auditable and analyzable records of AITA interactions, which can be invaluable for educational research, debugging, and iterative improvement of AI tutors.
*   **Prototyping**: These SDKs are intended to accelerate the prototyping and development of K-12 educational tools by providing reusable components and patterns for MCP communication.
