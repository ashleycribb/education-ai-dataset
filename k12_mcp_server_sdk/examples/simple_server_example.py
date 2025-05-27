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
        if exc_info:
            # In a real app, you might print traceback here
            pass
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
            self.logger.info(f"HelloResourceHandler: Handling GET request. Path params: {path_params}, Query params: {query_params}")
        
        # Example: Use a query parameter 'name' to customize the response
        name = query_params.get("name", "Guest")
        
        # Example: Use a path parameter 'version' (if path was /hello/{version})
        # api_version = path_params.get("version", "v1") 

        if name.lower() == "error": # Simulate an error
            if self.logger:
                self.logger.warning("HelloResourceHandler: Simulating an error for name='error'.")
            return create_error_response(
                error_message="Simulated error: Name 'error' is not allowed.",
                status_code=400,
                error_code="INVALID_NAME"
            )
            
        payload = {
            "greeting": self.message_template.format(name=name),
            "timestamp": self.get_current_timestamp() # Example of using a method from a base or self
        }
        return create_success_response(payload=payload)

    def get_current_timestamp(self) -> str:
        # In a real SDK, this might come from a utility class
        import datetime
        return datetime.datetime.utcnow().isoformat() + "Z"

class StudentDataHandler(BaseK12ResourceHandler):
    def __init__(self, logger: Optional[Any] = None):
        super().__init__(logger)
        self.mock_student_db = {
            "student123": {"name": "Alice Wonderland", "grade": 4, "current_topic": "Fractions"},
            "student456": {"name": "Bob The Builder", "grade": 5, "current_topic": "Ecosystems"}
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
    print("--- K-12 MCP SDK: Simple Server Example ---")
    
    # Initialize a logger (optional)
    logger = ConsoleLogger()
    logger.info("Logger initialized for example server.")

    # 1. Create an instance of the simplified server (default is stdio)
    # To run as HTTP: server = SimplifiedMCPServer(server_type="http", logger=logger)
    # Note: MCPHTTPServer from modelcontextprotocol might require additional dependencies
    # like 'aiohttp'. For simplicity, this example primarily targets stdio.
    server = SimplifiedMCPServer(server_type="stdio", logger=logger)
    logger.info("SimplifiedMCPServer (stdio) instance created.")

    # 2. Create instances of your custom handlers
    hello_handler = HelloResourceHandler(logger=logger)
    student_data_handler = StudentDataHandler(logger=logger)
    logger.info("Custom resource handlers instantiated.")

    # 3. Register the handlers with the server
    server.add_resource_handler(path_pattern="/hello", handler_instance=hello_handler)
    # Example with path parameters:
    server.add_resource_handler(path_pattern="/student/{student_id}/info", handler_instance=student_data_handler)
    
    # Example: How a tool handler would be added (though BaseK12ToolHandler needs full definition for useful example)
    # from modelcontextprotocol.protocol import ParameterDefinition, ParameterType
    # class MySimpleToolHandler(BaseK12ToolHandler):
    #     def __init__(self, logger=None):
    #         tool_def = {
    #             "name": "simple_echo_tool", "description": "Echoes back the input.",
    #             "inputs": [ParameterDefinition(name="message", type=ParameterType.STRING, description="Message to echo.")],
    #             "outputs": [ParameterDefinition(name="echo", type=ParameterType.STRING, description="The echoed message.")]
    #         }
    #         super().__init__(tool_definition_dict=tool_def, logger=logger)
    #     def handle_invoke(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    #         return {"echo": f"You said: {inputs.get('message', '')}"}
    # simple_tool = MySimpleToolHandler(logger)
    # server.add_tool_handler(simple_tool)
    # logger.info("Simple tool handler added (example).")


    logger.info("Starting server...")
    print("\nTo interact with this example server (stdio mode):")
    print("Send JSON MCP requests via stdin. For example:")
    print("For HelloResourceHandler (path /hello):")
    print('  {"mcp_version": "0.1.0", "request_id": "req1", "resource_path": "/hello"}')
    print('  {"mcp_version": "0.1.0", "request_id": "req2", "resource_path": "/hello", "query_params": {"name": "YourName"}}')
    print("For StudentDataHandler (path /student/{student_id}/info):")
    print('  {"mcp_version": "0.1.0", "request_id": "req3", "resource_path": "/student/student123/info"}')
    print('  {"mcp_version": "0.1.0", "request_id": "req4", "resource_path": "/student/unknown/info"}')
    # print("For simple_echo_tool:")
    # print('  {"mcp_version": "0.1.0", "request_id": "req_tool1", "tool_invocation": {"tool_name": "simple_echo_tool", "inputs": {"message": "Hello MCP!"}}}')
    print("\nServer is now listening...\n")

    # 4. Run the server
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user (KeyboardInterrupt).")
    except Exception as e:
        logger.error(f"Server exited with an error: {e}", exc_info=True)
    finally:
        logger.info("Example server run finished.")
