from typing import Optional, Dict, Any, Union
import time # For timeouts
import sys # For printing to stderr

from modelcontextprotocol.client.stdio_client import MCPStdIOClient
from modelcontextprotocol.client.http_client import MCPHTTPClient
from modelcontextprotocol.protocol import ResourcePath, ToolInvocation, ToolResult, StreamMessageType

class SimplifiedMCPClient:
    """
    A simplified client for interacting with MCP servers (StdIO or HTTP).
    """
    def __init__(
        self,
        client_type: str = "stdio",
        host: Optional[str] = "localhost",
        port: Optional[int] = 8080,
        logger: Optional[Any] = None
    ):
        self.client_type = client_type.lower()
        self.logger = logger # In a real SDK, this would be a proper logger interface
        self.mcp_client: Union[MCPStdIOClient, MCPHTTPClient, None] = None

        if self.client_type == "stdio":
            self.mcp_client = MCPStdIOClient()
        elif self.client_type == "http":
            if host is None or port is None:
                raise ValueError("Host and port must be provided for HTTP client type.")
            self.mcp_client = MCPHTTPClient(host=host, port=port)
        else:
            raise ValueError(f"Unsupported client_type: {client_type}. Choose 'stdio' or 'http'.")

        if self.logger:
            self.logger.info(f"SimplifiedMCPClient initialized (type: {self.client_type}).")

    def start(self):
        """Starts the client connection (primarily for StdIO)."""
        if self.client_type == "stdio" and isinstance(self.mcp_client, MCPStdIOClient):
            try:
                self.mcp_client.start()
                if self.logger:
                    self.logger.info("MCPStdIOClient started.")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to start MCPStdIOClient: {e}", exc_info=True)
                # Re-raise or handle as appropriate for the SDK's design
                raise
        elif self.client_type == "http":
            if self.logger:
                self.logger.info("MCPHTTPClient does not require an explicit start() method from this wrapper.")
        else: # Should not happen if constructor validated client_type
            if self.logger:
                self.logger.warning(f"Start called on an uninitialized or unsupported client type: {self.client_type}")


    def stop(self):
        """Stops the client connection (primarily for StdIO)."""
        if self.client_type == "stdio" and isinstance(self.mcp_client, MCPStdIOClient):
            try:
                self.mcp_client.stop()
                if self.logger:
                    self.logger.info("MCPStdIOClient stopped.")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to stop MCPStdIOClient: {e}", exc_info=True)
        elif self.client_type == "http":
             if self.logger:
                self.logger.info("MCPHTTPClient does not require an explicit stop() method from this wrapper.")
        else:
            if self.logger:
                self.logger.warning(f"Stop called on an uninitialized or unsupported client type: {self.client_type}")


    def get_resource_data(
        self, path: str, query_params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches resource data from the MCP server.
        """
        if self.mcp_client is None:
            if self.logger: self.logger.error("MCP client not initialized.")
            return None

        resource_path = ResourcePath(path=path, query_params=query_params or {})

        try:
            if self.logger:
                self.logger.info(f"Requesting resource: {path} with params {query_params}")

            if isinstance(self.mcp_client, MCPStdIOClient):
                # StdIO client doesn't have a timeout on get_resource in the same way HTTP might
                response = self.mcp_client.get_resource(resource_path)
            elif isinstance(self.mcp_client, MCPHTTPClient):
                # The underlying HTTP client in modelcontextprotocol might handle its own timeouts
                # or expect it via a different mechanism. This timeout is conceptual here.
                # For now, we assume the HTTPClient's internal requests call might have a timeout.
                # Let's simulate a timeout check if we were using a library like 'requests' directly.
                # response = self.mcp_client.get_resource(resource_path, timeout=timeout) # If supported
                response = self.mcp_client.get_resource(resource_path) # Assuming timeout is handled by http client config
            else: # Should not happen
                if self.logger: self.logger.error(f"Unsupported client type for get_resource: {type(self.mcp_client)}")
                return None


            if response and response.status_code == 200:
                if self.logger:
                    self.logger.info(f"Resource received successfully (status 200): {response.payload}")
                return response.payload
            else:
                status = response.status_code if response else "N/A"
                error_payload = response.payload if response and response.payload else {"error": "Unknown error or no payload"}
                if self.logger:
                    self.logger.error(f"Failed to get resource. Status: {status}, Payload: {error_payload}")
                return None
        except Exception as e: # Catching broader exceptions for robustness
            if self.logger:
                self.logger.error(f"Exception during get_resource for {path}: {e}", exc_info=True)
            return None

    def invoke_tool_outputs(
        self, tool_name: str, inputs: Dict[str, Any], timeout: Optional[float] = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Invokes a tool on the MCP server and returns its outputs.
        """
        if self.mcp_client is None:
            if self.logger: self.logger.error("MCP client not initialized.")
            return None

        tool_invocation = ToolInvocation(tool_name=tool_name, inputs=inputs)

        try:
            if self.logger:
                self.logger.info(f"Invoking tool: {tool_name} with inputs: {inputs}")

            tool_result: Optional[ToolResult] = None

            if isinstance(self.mcp_client, MCPStdIOClient):
                self.mcp_client.send_invocation(tool_invocation)
                # StdIO client's receive_response might block. Timeout is conceptual here.
                # A more complex implementation might use asyncio with timeout.
                response_message = self.mcp_client.receive_response()
                if response_message:
                    if response_message.stream_type == StreamMessageType.TOOL_RESULT:
                        tool_result = ToolResult.from_json(response_message.payload)
                    elif response_message.stream_type == StreamMessageType.ERROR:
                        if self.logger: self.logger.error(f"Server error on tool invocation: {response_message.payload}")
                        return None # Error message from server
                    else:
                        if self.logger: self.logger.warning(f"Unexpected message type from server: {response_message.stream_type}")
                        return None
                else: # No response
                    if self.logger: self.logger.error("No response received from server for tool invocation.")
                    return None


            elif isinstance(self.mcp_client, MCPHTTPClient):
                # tool_result = self.mcp_client.invoke_tool(tool_invocation, timeout=timeout) # If supported
                tool_result = self.mcp_client.invoke_tool(tool_invocation)
            else: # Should not happen
                if self.logger: self.logger.error(f"Unsupported client type for invoke_tool: {type(self.mcp_client)}")
                return None


            if tool_result and tool_result.outputs:
                # Check for structured errors within the tool_result.outputs, as per our response helpers
                if "error" in tool_result.outputs and isinstance(tool_result.outputs["error"], dict):
                    error_details = tool_result.outputs["error"]
                    if self.logger:
                        self.logger.error(f"Tool '{tool_name}' invocation resulted in an error: {error_details.get('message', 'Unknown tool error')}")
                    return None # Error reported by the tool itself

                if self.logger:
                    self.logger.info(f"Tool '{tool_name}' invoked successfully. Outputs: {tool_result.outputs}")
                return tool_result.outputs
            else:
                err_msg = "Tool invocation failed or returned no outputs."
                if tool_result and tool_result.outputs and "error" in tool_result.outputs: # More specific error
                    err_msg = f"Tool error: {tool_result.outputs['error']}"
                if self.logger:
                    self.logger.error(err_msg)
                return None

        except Exception as e: # Catching broader exceptions
            if self.logger:
                self.logger.error(f"Exception during invoke_tool for {tool_name}: {e}", exc_info=True)
            return None
