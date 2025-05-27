from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from modelcontextprotocol.protocol import ToolInvocation, ToolResult
from modelcontextprotocol.server import ResourceHandler, ToolHandler, ResourceResponse

from .responses import (
    create_success_response, 
    create_error_response,
    create_success_tool_result,
    create_error_tool_result
)

class BaseK12ResourceHandler(ResourceHandler, ABC):
    """
    Abstract base class for K-12 resource handlers.
    Provides basic error handling and structure.
    """
    def __init__(self, logger: Optional[Any] = None):
        self.logger = logger # In a real SDK, this would be a proper logger interface

    def get_resource(
        self, path_params: Dict[str, str], query_params: Dict[str, str], **kwargs
    ) -> ResourceResponse:
        try:
            if self.logger:
                self.logger.info(f"BaseK12ResourceHandler: Received GET request for path_params={path_params}, query_params={query_params}")
            return self.handle_get(path_params, query_params, **kwargs)
        except NotImplementedError:
            if self.logger:
                self.logger.error("BaseK12ResourceHandler: Method not implemented by subclass.")
            return create_error_response(
                error_message="The requested resource or method is not implemented on this server.",
                status_code=501,
                error_code="NOT_IMPLEMENTED"
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"BaseK12ResourceHandler: Unhandled exception in handle_get: {e}", exc_info=True)
            # In a production system, be careful about exposing raw error messages.
            return create_error_response(
                error_message=f"An unexpected server error occurred: {str(e)}",
                status_code=500,
                error_code="INTERNAL_SERVER_ERROR"
            )

    @abstractmethod
    def handle_get(
        self, path_params: Dict[str, str], query_params: Dict[str, str], **kwargs
    ) -> ResourceResponse:
        """
        Subclasses must implement this method to handle GET requests.
        Should return a ResourceResponse object.
        """
        raise NotImplementedError("Subclasses must implement handle_get.")


class BaseK12ToolHandler(ToolHandler, ABC):
    """
    Abstract base class for K-12 tool handlers.
    Provides basic error handling and structure for tool invocation.
    """
    def __init__(self, tool_definition_dict: Dict[str, Any], logger: Optional[Any] = None):
        # The actual Tool object (from modelcontextprotocol.protocol.Tool) is constructed
        # by the MCPStdIOServer or similar when it registers the handler.
        # This __init__ is more about setting up the handler itself.
        # The `name` and `description` typically come from the tool_definition_dict.
        super().__init__(
            name=tool_definition_dict.get("name", "unnamed_k12_tool"),
            description=tool_definition_dict.get("description", "No description provided."),
            inputs=tool_definition_dict.get("inputs", []),
            outputs=tool_definition_dict.get("outputs", [])
        )
        self.logger = logger

    def invoke(self, invocation: ToolInvocation, **kwargs) -> ToolResult:
        """
        Handles a tool invocation.
        This method is called by the MCP server.
        """
        try:
            if self.logger:
                self.logger.info(f"BaseK12ToolHandler ({self.name}): Received invocation with inputs: {invocation.inputs}")
            
            # The 'inputs' field of ToolInvocation is already a Dict[str, Any]
            tool_outputs = self.handle_invoke(invocation.inputs, **kwargs)
            return create_success_tool_result(outputs=tool_outputs, tool_name=self.name)
        
        except NotImplementedError:
            if self.logger:
                self.logger.error(f"BaseK12ToolHandler ({self.name}): Method not implemented by subclass.")
            return create_error_tool_result(
                tool_name=self.name,
                error_message="The requested tool logic is not implemented.",
                error_code="TOOL_NOT_IMPLEMENTED"
            )
        except ValueError as ve: # Example of handling specific user-facing errors
            if self.logger:
                self.logger.warning(f"BaseK12ToolHandler ({self.name}): Value error during tool invocation: {ve}")
            return create_error_tool_result(
                tool_name=self.name,
                error_message=str(ve),
                error_code="INVALID_TOOL_INPUT" 
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"BaseK12ToolHandler ({self.name}): Unhandled exception in handle_invoke: {e}", exc_info=True)
            return create_error_tool_result(
                tool_name=self.name,
                error_message=f"An unexpected error occurred in tool {self.name}: {str(e)}",
                error_code="TOOL_EXECUTION_FAILED"
            )

    @abstractmethod
    def handle_invoke(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Subclasses must implement this method to define the tool's core logic.
        Should return a dictionary of outputs.
        """
        raise NotImplementedError("Subclasses must implement handle_invoke.")
