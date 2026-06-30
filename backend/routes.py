"""
routes.py

Defines all HTTP API routes for the To-Do application. Route handlers
are intentionally kept thin: they validate input (via Pydantic models),
delegate actual data access to the `db` object from database.py, and
translate errors into appropriate HTTP responses.
"""

from typing import List, Optional

from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query, status

from database import db
from models import TaskCreate, TaskUpdate, TaskResponse, MessageResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _handle_invalid_id(task_id: str) -> None:
    """Raise a clean 400 error for malformed ObjectId strings."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"'{task_id}' is not a valid task id.",
    )


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter by status: 'active' or 'completed'",
        pattern="^(active|completed)$",
    ),
    search: Optional[str] = Query(
        default=None, description="Search tasks by title (case-insensitive)"
    ),
    sort: str = Query(
        default="newest",
        description="Sort order: 'newest' or 'oldest'",
        pattern="^(newest|oldest)$",
    ),
):
    """Retrieve all tasks, optionally filtered, searched, and sorted."""
    tasks = db.get_tasks(status=status_filter, search=search, sort=sort)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    """Retrieve a single task by its id."""
    try:
        task = db.get_task(task_id)
    except InvalidId:
        _handle_invalid_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' was not found.",
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Create a new task."""
    created = db.create_task(title=task.title, description=task.description)
    return created


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task: TaskUpdate):
    """Update an existing task. Only provided fields are modified."""
    update_data = task.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    try:
        updated = db.update_task(task_id, update_data)
    except InvalidId:
        _handle_invalid_id(task_id)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' was not found.",
        )
    return updated


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: str):
    """Delete a task by its id."""
    try:
        deleted = db.delete_task(task_id)
    except InvalidId:
        _handle_invalid_id(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' was not found.",
        )
    return {"message": f"Task '{task_id}' was deleted successfully."}


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str):
    """Mark a task as completed."""
    try:
        updated = db.set_completed(task_id, True)
    except InvalidId:
        _handle_invalid_id(task_id)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' was not found.",
        )
    return updated


@router.patch("/{task_id}/uncomplete", response_model=TaskResponse)
def uncomplete_task(task_id: str):
    """Mark a task as active (not completed)."""
    try:
        updated = db.set_completed(task_id, False)
    except InvalidId:
        _handle_invalid_id(task_id)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' was not found.",
        )
    return updated
