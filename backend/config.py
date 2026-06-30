"""
config.py

Centralized application configuration.
Reads environment variables from a .env file using python-dotenv so that
sensitive / environment-specific values (database URI, names, ports) are
never hard-coded. This makes the app easy to re-configure for Docker and
Kubernetes deployments later (the same variable names can simply be
injected as container env vars or ConfigMap/Secret values).
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file located at the project root.
# In containerized environments (Docker/K8s) these will instead be
# injected directly as environment variables, and load_dotenv() will
# simply be a no-op if no .env file is found.
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # MongoDB connection settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "todo_app")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "tasks")

    # API / CORS settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Comma-separated list of allowed CORS origins. Defaults cover common
    # local development setups (Live Server, plain file open, etc.).
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost,http://localhost:3000,http://localhost:5500,"
        "http://127.0.0.1,http://127.0.0.1:3000,http://127.0.0.1:5500,"
        "http://127.0.0.1:5501,http://localhost:5501",
    ).split(",")


# Singleton settings instance used across the app
settings = Settings()
