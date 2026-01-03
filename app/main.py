from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from dotenv import load_dotenv
from app.fabric_mcp import jira_mcp_server, xray_mcp_server
from app.core.config import settings
from contextlib import asynccontextmanager
from app.api import health_router

import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the main Fabric MCP server
# This server acts as a hub that imports other specialized MCP servers (Jira, Xray)
# mask_error_details: In production (not DEBUG), sensitive error information is masked
fabric_mcp_server = FastMCP(name="Fabric MCP Server", mask_error_details=not settings.DEBUG)

# MCP server lifespan context manager to import dependent servers
@asynccontextmanager
async def include_mcp_servers(_: FastAPI):
	"""Register Jira and Xray MCP servers with 'pss_fabric' prefix."""
	await fabric_mcp_server.import_server(jira_mcp_server, prefix="pss_fabric")
	await fabric_mcp_server.import_server(xray_mcp_server, prefix="pss_fabric")
	yield

# Create MCP HTTP app for exposing MCP server via HTTP
fabric_mcp_app = fabric_mcp_server.http_app()

# Combined lifespan manager for FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Orchestrate startup/shutdown of MCP servers and FastAPI application."""
	async with include_mcp_servers(app):
		async with fabric_mcp_app.lifespan(app):
			yield

# Create FastAPI application with lifespan management
app = FastAPI(title="MCP Fabric Server", version="1.0.0", lifespan=lifespan)

# Mount MCP HTTP server at /fabric endpoint
# This exposes the MCP server's HTTP interface for client connections
app.mount("/fabric", fabric_mcp_app)
app.mount("/healthy", JSONResponse(content={"status": "healthy"}))

# Configure CORS (Cross-Origin Resource Sharing)
# Allows specified origins to make requests to this API
origins = settings.CORS_ORIGINS.split(",")
logger.info(f"CORS configured with origins: {origins}")

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Global exception handler for unhandled application errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
	"""Handle uncaught exceptions at the application level.
    
    Catches any unhandled exception thrown during request processing and returns
    a standardized error response. Response content varies based on environment:
    - Production: Generic error message (details hidden)
    - Development: Full error message and stack trace
    
    Args:
        request: The HTTP request that caused the exception
        exc: The unhandled exception
    
    Returns:
        JSONResponse with HTTP 500 status and appropriate error detail
    
    Note:
        - Logs the full exception with traceback for debugging
        - Environment mode is determined by settings.ENV
        - Production mode protects sensitive information
    """
	logger.error(f"Unhandled error: {exc}", exc_info=True)
	
	# Don't expose internal errors in production
	if settings.ENV == "production":
		return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
	else:
		return JSONResponse(
			status_code=500, 
			content={"detail": "Internal Server Error", "error": str(exc)}
		)

# Include API routes (health checks, etc.)
app.include_router(health_router, prefix="/api")

if __name__ == "__main__":
	"""Main entry point for running the application with uvicorn."""
	import uvicorn
	logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
	uvicorn.run(
		"app.main:app", 
		host=settings.HOST, 
		port=settings.PORT,
		reload=settings.DEBUG
	)
