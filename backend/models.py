"""
models.py

Pydantic models used for request validation and response serialization.
Separating these from routes.py keeps validation logic reusable and
makes the API's data contracts explicit and easy to document via
FastAPI's automatic OpenAPI generation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    """Schema for creating a new task (POST /tasks)."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        default=None, max_length=2000, description="Optional task description"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and coffee",
            }
        }
    )


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task (PUT /tasks/{id}).
    All fields are optional so the client can send a partial update.
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Buy groceries and cook dinner",
                "description": "Milk, eggs, bread, coffee, pasta",
                "completed": False,
            }
        }
    )


class TaskResponse(BaseModel):
    """Schema describing a task as returned by the API."""

    id: str = Field(alias="_id")
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True)


class MessageResponse(BaseModel):
    """Generic message response, e.g. for delete confirmations."""

    message: str
