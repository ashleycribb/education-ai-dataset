from typing import Dict, Any, Optional
from modelcontextprotocol.protocol import ToolResult
from modelcontextprotocol.server import ResourceResponse

# Re-export for convenience if needed by users of the SDK
__all__ = [
    "ResourceResponse",
    "ToolResult",
    "create_success_response",
    "create_error_response",
    "create_success_tool_result",
    "create_error_tool_result"
]

def create_success_response(payload: Any, status_code: int = 200) -> ResourceResponse:
    """
    Creates a successful ResourceResponse.
    """
    return ResourceResponse(status_code=status_code, payload=payload)

def create_error_response(
    error_message: str,
    status_code: int,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> ResourceResponse:
    """
    Creates an error ResourceResponse with a structured error payload.
    """
    error_payload = {
        "error": {
            "code": error_code or f"ERR_HTTP_{status_code}",
            "message": error_message,
        }
    }
    if details:
        error_payload["error"]["details"] = details

    return ResourceResponse(status_code=status_code, payload=error_payload)

def create_success_tool_result(outputs: Dict[str, Any], tool_name: str = "unknown_tool") -> ToolResult:
    """
    Creates a successful ToolResult.
    """
    return ToolResult(tool_name=tool_name, outputs=outputs)

def create_error_tool_result(
    error_message: str,
    tool_name: str = "unknown_tool",
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    Creates an error ToolResult.
    The error information is structured within the 'outputs' payload.
    """
    error_payload = {
        "error": {
            "code": error_code or "TOOL_EXECUTION_ERROR",
            "message": error_message,
        }
    }
    if details:
        error_payload["error"]["details"] = details

    return ToolResult(tool_name=tool_name, outputs={"error": error_payload})
