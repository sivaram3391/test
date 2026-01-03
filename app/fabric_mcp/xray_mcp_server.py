from app.services.xray_client import XrayClient
from app.core.config import settings
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
import logging

logger = logging.getLogger(__name__)

# Initialize Xray client with OAuth 2.0 credentials from configuration
xray_client = XrayClient(
    base_url=settings.XRAY_BASE_URL,
    client_id=settings.XRAY_CLIENT_ID,
    client_secret=settings.XRAY_CLIENT_SECRET
)

# Initialize FastMCP server for Xray integration
# - name: Display name for the MCP server in client applications
# - mask_error_details: When True (production), hides sensitive error details from responses
xray_mcp_server = FastMCP(
    name="Fabric Xray MCP Server",
    mask_error_details=not settings.DEBUG
)

@xray_mcp_server.tool(name="get_xray_test_case")
async def get_xray_test_case(test_case_key: str) -> dict:
    """Fetch Xray test case by key with all test details via MCP tool.

    Args:
        test_case_key: Xray test case key (e.g., 'XSP-123')

    Returns:
        Test case dict with key, summary, status, testType, steps, etc.

    Raises:
        ToolError: Wraps ValueError (invalid key), PermissionError (auth), or RuntimeError (network)
    """
    try:
        test_case = await xray_client.get_test_case(test_case_key)
        return test_case
    except (ValueError, PermissionError, RuntimeError) as e:
        logger.error(f"Error in get_xray_test_case tool: {e}", exc_info=True)
        raise ToolError(str(e))
    except Exception as e:
        logger.error(f"Error in get_xray_test_case tool: {e}", exc_info=True)
        raise # Safe to raise. Exceptions/Error other than ToolError will be masked by FastMCP
