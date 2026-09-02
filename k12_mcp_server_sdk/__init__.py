"""
K-12 Model Context Protocol (MCP) Server SDK
---------------------------------------------
This SDK provides base classes and utilities to simplify the creation of
MCP-compliant servers tailored for K-12 educational applications.
It builds upon the core `modelcontextprotocol` library.
"""

# Core server and handler classes
from .server import SimplifiedMCPServer
from .handlers import BaseK12ResourceHandler, BaseK12ToolHandler

# Response creation utilities
from .responses import (
    create_success_response,
    create_error_response,
    create_success_tool_result,
    create_error_tool_result,
    ResourceResponse, # Re-exporting for convenience
    ToolResult        # Re-exporting for convenience
)

# Potentially other utilities or constants if added to utils.py later
# from .utils import some_utility_function

__all__ = [
    "SimplifiedMCPServer",
    "BaseK12ResourceHandler",
    "BaseK12ToolHandler",
    "create_success_response",
    "create_error_response",
    "create_success_tool_result",
    "create_error_tool_result",
    "ResourceResponse",
    "ToolResult"
]

__version__ = "0.1.0"
