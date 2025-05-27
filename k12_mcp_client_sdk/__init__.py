"""
K-12 Model Context Protocol (MCP) Client SDK
---------------------------------------------
This SDK provides a simplified client for interacting with MCP servers 
(both StdIO and HTTP) and utilities for creating xAPI-like statements 
for logging interactions.
"""

from .client import SimplifiedMCPClient
from .xapi_utils import create_interaction_xapi_statement, log_xapi_statement
# from .utils import some_utility_function # If utils.py gets content later

__all__ = [
    "SimplifiedMCPClient",
    "create_interaction_xapi_statement",
    "log_xapi_statement"
]

__version__ = "0.1.0"
