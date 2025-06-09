from typing import Dict, Any, Optional, List, Union

from modelcontextprotocol.server import MCPStdIOServer, MCPHTTPServer, ToolHandler as MCPToolHandler
from modelcontextprotocol.protocol import Tool # Assuming Tool is the base for ToolHandler's tool registration

from .handlers import BaseK12ResourceHandler, BaseK12ToolHandler

class SimplifiedMCPServer:
    """
    A simplified server wrapper for MCPStdIOServer or MCPHTTPServer.
    """
    def __init__(
        self,
        server_type: str = "stdio",
        host: str = "localhost",
        port: int = 8080,
        logger: Optional[Any] = None
    ):
        self.logger = logger
        self.server_type = server_type.lower()
        self._tools: List[MCPToolHandler] = [] # Store tool handlers before server instantiation for stdio

        if self.server_type == "stdio":
            # For MCPStdIOServer, tools are typically passed at initialization.
            # Resource handlers are registered directly with the server instance.
            self._server = MCPStdIOServer(tools=self._tools, handlers={}) # Handlers will be added via add_resource_handler
        elif self.server_type == "http":
            # MCPHTTPServer might handle registration differently or also at init.
            # This is a simplified example; real HTTP server setup might be more complex.
            self._server = MCPHTTPServer(host=host, port=port, tools=self._tools, handlers={})
        else:
            raise ValueError(f"Unsupported server_type: {server_type}. Choose 'stdio' or 'http'.")

        if self.logger:
            self.logger.info(f"SimplifiedMCPServer initialized with type: {self.server_type}")

    def add_resource_handler(
        self,
        path_pattern: str,
        handler_instance: BaseK12ResourceHandler
    ):
        """
        Registers a resource handler with the underlying MCP server.
        """
        if not hasattr(self._server, 'handlers') or not isinstance(self._server.handlers, dict):
             # This might happen if the underlying server doesn't initialize handlers as a dict
            self._server.handlers = {} # Ensure handlers dict exists

        self._server.handlers[path_pattern] = handler_instance
        if self.logger:
            self.logger.info(f"Registered resource handler for path: {path_pattern}")

    def add_tool_handler(self, handler_instance: BaseK12ToolHandler):
        """
        Registers a tool handler.
        For MCPStdIOServer, tools are often provided at init. This method collects them.
        If the server is already running or initialized in a way that tools can't be added,
        this might need adjustment based on the specific MCP server implementation.
        """
        # The BaseK12ToolHandler itself is already an instance of MCPToolHandler
        # (since BaseK12ToolHandler inherits from modelcontextprotocol.server.ToolHandler)
        if isinstance(handler_instance, MCPToolHandler):
            self._tools.append(handler_instance)
            if self.logger:
                self.logger.info(f"Added tool handler: {handler_instance.name}")

            # If server is already instantiated and supports dynamic tool addition (less common for stdio)
            # if hasattr(self._server, 'add_tool'): # Hypothetical method
            #     self._server.add_tool(handler_instance)
            # elif self.server_type == "stdio" and isinstance(self._server, MCPStdIOServer):
                # For MCPStdIOServer, tools are passed in constructor.
                # Re-initialize if necessary, though this is a simplification.
                # A better approach for dynamic addition would be a more complex server wrapper.
                # For this SDK, we assume tools are added before run() is called.
                # self._server = MCPStdIOServer(tools=self._tools, handlers=self._server.handlers)
                # print("Warning: Re-initialized MCPStdIOServer to add new tool. This is a simplified behavior.")
                # Pass
        else:
            if self.logger:
                self.logger.error(f"Failed to add tool: {handler_instance} is not a valid ToolHandler.")
            raise TypeError("handler_instance must be a subclass of BaseK12ToolHandler or ToolHandler.")


    def run(self):
        """
        Starts the MCP server.
        """
        if self.logger:
            self.logger.info(f"Starting MCP server (type: {self.server_type})...")

        # For MCPStdIOServer, ensure tools collected via add_tool_handler are part of the server instance
        # if self.server_type == "stdio" and isinstance(self._server, MCPStdIOServer):
            # If the server was initialized with an empty tool list, update it.
            # This check is a bit redundant if we assume tools are added before run.
            # A more robust SDK might have a build() step before run().
            # self._server.tools = self._tools # This might not be how MCPStdIOServer works if tools are immutable post-init

        self._server.run()
        if self.logger:
            self.logger.info("MCP server stopped.")
