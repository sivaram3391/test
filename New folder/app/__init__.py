"""PSS Fabric MCP Tools - MCP integration with Jira and Xray.

FastAPI app with MCP servers for Jira (issues) and Xray (test cases).

Environment Variables:
    JIRA_EMAIL, JIRA_API_TOKEN, JIRA_BASE_URL
    XRAY_CLIENT_ID, XRAY_CLIENT_SECRET, XRAY_BASE_URL
    CORS_ORIGINS (default: http://localhost:3000)
    DEBUG, ENV (default: development)

Access: http://localhost:8000/fabric (MCP), http://localhost:8000/api/health
"""