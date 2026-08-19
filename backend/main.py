"""
main.py

FastAPI application entrypoint. Responsible for:
  - Creating the FastAPI app instance
  - Configuring CORS
  - Wiring up the database connection lifecycle (startup/shutdown)
  - Registering routers
  - Exposing a simple health check endpoint (useful for Docker/K8s
    liveness and readiness probes later on)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import db
from routes import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup: connect to MongoDB
    db.connect()
    yield
    # Shutdown: close the MongoDB connection
    db.close()


app = FastAPI(
    title="To-Do List API",
    description="A simple, modular REST API for managing to-do tasks, "
    "built with FastAPI, PyMongo, and MongoDB.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS so the frontend (served separately on localhost) can call
# this API from the browser without being blocked by CORS policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the /tasks routes
app.include_router(tasks_router)


@app.get("/health", tags=["health"])
def health_check():
    """
    Simple health check endpoint.
    Useful for Docker HEALTHCHECK instructions and Kubernetes
    liveness/readiness probes.
    """
    mongo_ok = db.ping()
    return {
        "status": "ok" if mongo_ok else "degraded",
        "mongodb_connected": mongo_ok,
    }


@app.get("/", tags=["health"])
def root():
    """Root endpoint with basic API info."""
    return {
        "message": "To-Do List API is running.",
        "docs": "/docs",
        "health": "/health",
    }
# Versiyonlama full test-11