# K-12 Model Context Protocol (MCP) Server SDK

A Python SDK to simplify building K-12 focused Model Context Protocol (MCP) servers. 
This SDK provides base classes and utilities that wrap the core `modelcontextprotocol` library, 
making it easier to create educational tools and resource providers that can communicate 
with MCP-compliant AI tutors and learning platforms.

## Features (Planned)

*   Simplified server setup for both Stdio and HTTP MCP transport.
*   Base handler classes (`BaseK12ResourceHandler`, `BaseK12ToolHandler`) with common error handling and logging hooks.
*   Helper functions for creating standardized MCP responses (`ResourceResponse`, `ToolResult`).
*   Utilities for common K-12 education data structures (e.g., learning objectives, student context - future).
*   Hooks for xAPI statement generation (future).
*   Example implementations to get started quickly.

## Installation

```bash
# Installation instructions will be provided once the package is ready for distribution.
# For now, to use this SDK, include it directly in your project or use path-based dependencies.
# Example (if using Poetry):
# poetry add path/to/k12_mcp_server_sdk
```

## Basic Usage

The following example demonstrates how to set up a simple MCP server using this SDK.
This server will respond to GET requests on the `/hello` resource path and the `/student/{student_id}/info` path.

```python
# examples/simple_server_example.py
from typing import Dict, Any, Optional

from k12_mcp_server_sdk import (
    SimplifiedMCPServer, 
    BaseK12ResourceHandler, 
    ResourceResponse,
    create_success_response,
    create_error_response
)

# A simple logger class for demonstration purposes
class ConsoleLogger:
    def info(self, message: str):
        print(f"INFO: {message}")
    def error(self, message: str, exc_info: bool = False):
        print(f"ERROR: {message}")
    def warning(self, message: str):
        print(f"WARNING: {message}")

# 1. Define a custom resource handler
class HelloResourceHandler(BaseK12ResourceHandler):
    def __init__(self, logger: Optional[Any] = None):
        super().__init__(logger)
        self.message_template = "Hello, {name}! Welcome to the K-12 MCP SDK example."

    def handle_get(
        self, path_params: Dict[str, str], query_params: Dict[str, str], **kwargs
    ) -> ResourceResponse:
        if self.logger:
            self.logger.info(f"HelloResourceHandler: Handling GET. Path: {path_params}, Query: {query_params}")
        
        name = query_params.get("name", "Guest")
        
        if name.lower() == "error":
            if self.logger:
                self.logger.warning("HelloResourceHandler: Simulating an error for name='error'.")
            return create_error_response("Simulated error: Name 'error' is not allowed.", 400, "INVALID_NAME")
            
        payload = {"greeting": self.message_template.format(name=name)}
        return create_success_response(payload=payload)

class StudentDataHandler(BaseK12ResourceHandler):
    def __init__(self, logger: Optional[Any] = None):
        super().__init__(logger)
        self.mock_student_db = {
            "student123": {"name": "Alice", "grade": 4, "topic": "Fractions"},
            "student456": {"name": "Bob", "grade": 5, "topic": "Ecosystems"}
        }
    
    def handle_get(
        self, path_params: Dict[str, str], query_params: Dict[str, str], **kwargs
    ) -> ResourceResponse:
        student_id = path_params.get("student_id")
        if not student_id:
            return create_error_response("student_id path parameter is required.", 400, "MISSING_PATH_PARAM")
        
        student_data = self.mock_student_db.get(student_id)
        if student_data:
            return create_success_response(student_data)
        else:
            return create_error_response(f"Student with ID '{student_id}' not found.", 404, "STUDENT_NOT_FOUND")

if __name__ == "__main__":
    logger = ConsoleLogger()
    server = SimplifiedMCPServer(server_type="stdio", logger=logger)

    hello_handler = HelloResourceHandler(logger=logger)
    student_handler = StudentDataHandler(logger=logger)

    server.add_resource_handler(path_pattern="/hello", handler_instance=hello_handler)
    server.add_resource_handler(path_pattern="/student/{student_id}/info", handler_instance=student_handler)
    
    logger.info("Starting K-12 MCP example server (stdio mode)...")
    print("\\nSend JSON MCP requests via stdin. Examples:")
    print('  {"mcp_version": "0.1.0", "request_id": "req1", "resource_path": "/hello", "query_params": {"name": "World"}}')
    print('  {"mcp_version": "0.1.0", "request_id": "req2", "resource_path": "/student/student123/info"}\\n')
    
    server.run()
```

## SDK Components

### `SimplifiedMCPServer`
Wraps the underlying `MCPStdIOServer` or `MCPHTTPServer` and provides methods to easily add resource and tool handlers.

### `BaseK12ResourceHandler`
An abstract base class for creating resource handlers. Subclasses should implement `handle_get` to process GET requests for a specific resource type. It includes basic error handling.

### `BaseK12ToolHandler`
An abstract base class for creating tool handlers. Subclasses should implement `handle_invoke` to define the tool's logic. It includes basic error handling and response formatting.

### Response Helpers
Located in `k12_mcp_server_sdk.responses`:
*   `create_success_response`: Creates a `ResourceResponse` for successful operations.
*   `create_error_response`: Creates a `ResourceResponse` for errors with a structured error payload.
*   `create_success_tool_result`: Creates a `ToolResult` for successful tool invocations.
*   `create_error_tool_result`: Creates a `ToolResult` for tool invocation errors.

## Contributing (Placeholder)

Details on how to contribute to this SDK will be provided later.

## License (Placeholder)

This SDK will be released under the [Apache 2.0 License or MIT License - TBD].
```
