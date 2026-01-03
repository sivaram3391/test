"""FastAPI route handlers.

Exports:
    health_router: APIRouter with /health, /health/ready, /health/live endpoints
"""

from app.api.routes.health import router as health_router