# K-12 Model Context Protocol (MCP) Client SDK

A Python SDK to simplify interactions with K-12 focused Model Context Protocol (MCP) servers.
This SDK provides a `SimplifiedMCPClient` for communicating via StdIO or HTTP, 
and utilities for creating xAPI-like statements to log educational interactions.

## Features

*   `SimplifiedMCPClient`: A client for both `stdio` and `http` MCP communication.
    *   Methods to start/stop client connections.
    *   Wrapper for `get_resource` calls.
    *   Wrapper for `invoke_tool` calls (handling stdio's send/receive logic).
*   `xapi_utils`:
    *   `create_interaction_xapi_statement`: Helper function to construct xAPI-like JSON statements.
    *   `log_xapi_statement`: Utility to append these statements to a JSON Lines file.
*   Example usage demonstrating client setup and basic calls.

## Installation

```bash
# Installation instructions will be provided once the package is formally packaged.
# For now, to use this SDK, include it directly in your project or use path-based dependencies.
# Example (if using Poetry):
# poetry add path/to/k12_mcp_client_sdk
```

## Basic Usage

The following example demonstrates how to set up and use the `SimplifiedMCPClient` 
to interact with an MCP server (assumed to be running in stdio mode for this example)
and log interactions using the xAPI utilities.

```python
# examples/simple_client_example.py
from typing import Optional, Any
import datetime 
import json # For pretty printing in example

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
    def warning(self, message: str):
        print(f"CLIENT_EXAMPLE_WARNING: {message}")

if __name__ == "__main__":
    logger = ConsoleLogger()
    client = SimplifiedMCPClient(client_type="stdio", logger=logger)
    
    session_id = "session_client_example_001"
    user_name_for_log = "ClientSDKUser"
    user_account_for_log = "clientsdkuser@example.com"
    example_log_file = "example_client_interactions.jsonl"

    try:
        logger.info("Starting SimplifiedMCPClient (stdio)...")
        client.start()

        # Example: Get a resource
        resource_data = client.get_resource_data(
            path="/hello", 
            query_params={"name": "SDK Client User"}
        )

        if resource_data:
            logger.info(f"Received resource data: {resource_data}")
            print(f"Server Response to /hello: {resource_data.get('greeting', 'N/A')}\\n")

            statement = create_interaction_xapi_statement(
                actor_name=user_name_for_log,
                actor_account_name=user_account_for_log,
                verb_id="http://adlnet.gov/expapi/verbs/requested",
                verb_display="requested resource",
                object_activity_id="http://example.com/mcp_sdk/resource/hello_world",
                object_activity_name="Hello World Resource (SDK Example)",
                object_activity_description="A simple resource that returns a greeting.",
                session_id=session_id,
                result_response=json.dumps(resource_data) 
            )
            log_xapi_statement(statement, example_log_file, logger)
        else:
            logger.warning("Failed to retrieve /hello resource.")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
    finally:
        logger.info("Stopping SimplifiedMCPClient...")
        client.stop()
        logger.info("Client example finished.")
    
    print(f"Check '{example_log_file}' for xAPI-like statements.")
```

## SDK Components

### `SimplifiedMCPClient`
(Located in `k12_mcp_client_sdk.client`)
*   Provides a high-level interface for MCP communication.
*   Supports `stdio` and `http` client types.
*   Methods:
    *   `start()`: Initiates connection for stdio client.
    *   `stop()`: Terminates connection for stdio client.
    *   `get_resource_data(...)`: Fetches data from a resource path on the server.
    *   `invoke_tool_outputs(...)`: Invokes a tool on the server and retrieves outputs.

### `xapi_utils`
(Located in `k12_mcp_client_sdk.xapi_utils`)
*   `create_interaction_xapi_statement(...)`: A function to build a Python dictionary that closely mirrors the structure of an xAPI statement for logging educational interactions.
*   `log_xapi_statement(...)`: A function to append a statement dictionary (as created by the function above) to a specified file in JSON Lines (jsonl) format.

## Contributing (Placeholder)

Details on how to contribute to this SDK will be provided later.

## License (Placeholder)

This SDK will be released under the [Apache 2.0 License or MIT License - TBD].
```
