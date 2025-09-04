import asyncio
from typing import Optional, Dict, Any, Union
import sys

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from mcp.types import CallToolResult

class SimplifiedMCPClient:
    """
    An async-first simplified client for interacting with MCP servers (StdIO or HTTP).
    """
    def __init__(
        self,
        client_type: str = "stdio",
        host: Optional[str] = "localhost",
        port: Optional[int] = 8080,
        logger: Optional[Any] = None,
        stdio_command: Optional[str] = None,
        stdio_args: Optional[list[str]] = None,
    ):
        self.client_type = client_type.lower()
        self.logger = logger
        self.session: Optional[ClientSession] = None
        self._cm = None

        if self.client_type == "stdio":
            if not stdio_command:
                raise ValueError("`stdio_command` is required for stdio client type.")
            self.server_params = StdioServerParameters(command=stdio_command, args=stdio_args or [])
        elif self.client_type == "http":
            if host is None or port is None:
                raise ValueError("Host and port must be provided for HTTP client type.")
            self.url = f"http://{host}:{port}/mcp"
        else:
            raise ValueError(f"Unsupported client_type: {client_type}. Choose 'stdio' or 'http'.")

        if self.logger:
            self.logger.info(f"SimplifiedMCPClient initialized (type: {self.client_type}).")

    async def start(self):
        """Starts the client connection and establishes a session."""
        if self.session:
            if self.logger: self.logger.warning("Client already started.")
            return

        if self.client_type == "stdio":
            self._cm = stdio_client(self.server_params)
        else: # http
            self._cm = streamablehttp_client(self.url)

        try:
            read_stream, write_stream, _ = await self._cm.__aenter__()
            self.session = ClientSession(read_stream, write_stream)
            await self.session.initialize()
            if self.logger:
                self.logger.info("MCP client started and session initialized.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to start MCP client: {e}", exc_info=True)
            if self._cm:
                await self._cm.__aexit__(None, None, None)
            self._cm = None
            self.session = None
            raise

    async def stop(self):
        """Stops the client connection."""
        if not self.session or not self._cm:
            if self.logger: self.logger.warning("Client not started or already stopped.")
            return

        try:
            await self._cm.__aexit__(None, None, None)
            if self.logger:
                self.logger.info("MCP client stopped.")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to stop MCP client: {e}", exc_info=True)
        finally:
            self.session = None
            self._cm = None

    async def get_resource_data(
        self, path: str, query_params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Fetches resource data from the MCP server.
        """
        if not self.session:
            if self.logger: self.logger.error("MCP client not started.")
            return None

        try:
            if self.logger:
                self.logger.info(f"Requesting resource: {path} with params {query_params}")

            resource_content = await self.session.read_resource(path)

            # Assuming the first content block is the one we want and it's text
            if resource_content.contents:
                content_block = resource_content.contents[0]
                if hasattr(content_block, 'text'):
                     return {"payload": content_block.text} # Emulating old structure
                elif hasattr(content_block, 'blob'):
                     return {"payload": content_block.blob}
            return None

        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception during get_resource for {path}: {e}", exc_info=True)
            return None

    async def invoke_tool_outputs(
        self, tool_name: str, inputs: Dict[str, Any], timeout: Optional[float] = 10.0
    ) -> Optional[Dict[str, Any]]:
        """
        Invokes a tool on the MCP server and returns its outputs.
        """
        if not self.session:
            if self.logger: self.logger.error("MCP client not started.")
            return None

        try:
            if self.logger:
                self.logger.info(f"Invoking tool: {tool_name} with inputs: {inputs}")

            result = await self.session.call_tool(tool_name, arguments=inputs)

            if result.isError:
                if self.logger: self.logger.error(f"Tool invocation failed: {result.content}")
                return None

            # The new API returns structured content directly
            return result.structuredContent

        except Exception as e:
            if self.logger:
                self.logger.error(f"Exception during invoke_tool for {tool_name}: {e}", exc_info=True)
            return None
