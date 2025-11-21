from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models  # noqa: F401  Ensure models are imported so metadata includes them
from .routers import products_router, alerts_router, jobs_router

openapi_tags = [
    {"name": "health", "description": "Service health and readiness"},
    {"name": "products", "description": "Product CRUD operations"},
    {"name": "prices", "description": "Price history operations"},
    {"name": "alerts", "description": "Alert operations"},
    {"name": "jobs", "description": "Maintenance jobs such as fetching latest prices"},
]

app = FastAPI(
    title="PriceSense Backend",
    description="Backend API for PriceSense providing product tracking, price history, and alerts.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# PUBLIC_INTERFACE
@app.get("/", tags=["health"], summary="Health Check", description="Simple health endpoint to verify the service is running.")
def health_check():
    """Return service health."""
    return {"message": "Healthy"}


# Include routers
app.include_router(products_router)
app.include_router(alerts_router)
app.include_router(jobs_router)
