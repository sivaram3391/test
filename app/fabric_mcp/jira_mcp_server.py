from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from app.core.config import settings
from app.services.jira_client import JiraClient
import logging

logger = logging.getLogger(__name__)

# Initialize Jira client with credentials from configuration
jira_client = JiraClient(
    base_url=settings.JIRA_BASE_URL,
    username=settings.JIRA_EMAIL,
    api_token=settings.JIRA_API_TOKEN,
)

# Initialize FastMCP server for Jira integration
# - name: Display name for the MCP server in client applications
# - mask_error_details: When True (production), hides sensitive error details from responses
jira_mcp_server = FastMCP(
    name="Fabric JIRA MCP Server",
    mask_error_details=not settings.DEBUG
)

@jira_mcp_server.tool(name="get_jira_issue")
async def get_jira_issue(issue_key: str) -> dict:
    """Fetch Jira issue by key with all fields including custom fields via MCP tool.

    Args:
        issue_key: Jira issue key (e.g., 'PROJ-123')

    Returns:
        Issue dict with key, summary, status, priority, assignee, all_fields, etc.

    Raises:
        ToolError: Wraps ValueError (invalid key), PermissionError (auth), or RuntimeError (network)
    """
    try:
        issue = await jira_client.get_issue(issue_key)
        return issue
    except (ValueError, PermissionError, RuntimeError) as e:
        logger.error(f"Error in get_jira_issue tool: {e}", exc_info=True)
        # Raise a ToolError to return error response
        raise ToolError(str(e))
    except Exception as e:
        # Truly unexpected errors
        logger.critical(f"Unexpected error in get_jira_issue tool: {e}", exc_info=True)
        raise # Safe to raise. Exceptions/Error other than ToolError will be masked by FastMCP
