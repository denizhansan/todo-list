"""
database.py

Encapsulates all MongoDB connectivity and low-level data access logic
using PyMongo. Keeping this separate from routes.py enforces a clean
separation between "how we talk to the database" and "how we expose
HTTP endpoints", which keeps the codebase modular and easier to test,
mock, or swap out later (e.g., for a different database).
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from config import settings


class Database:
    """
    Thin wrapper around a PyMongo client/collection that provides
    task-specific CRUD operations used by the API routes.
    """

    def __init__(self) -> None:
        self.client: Optional[MongoClient] = None
        self.collection: Optional[Collection] = None

    def connect(self) -> None:
        """Establish the connection to MongoDB. Called on app startup."""
        self.client = MongoClient(settings.MONGODB_URI)
        database = self.client[settings.DATABASE_NAME]
        self.collection = database[settings.COLLECTION_NAME]
        # Create a basic index on title to make search-by-title faster.
        self.collection.create_index("title")
        self.collection.create_index("created_at")

    def close(self) -> None:
        """Close the MongoDB connection. Called on app shutdown."""
        if self.client is not None:
            self.client.close()

    def ping(self) -> bool:
        """Health check used by the /health endpoint."""
        try:
            self.client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def to_object_id(task_id: str) -> ObjectId:
        """
        Safely convert a string into a MongoDB ObjectId.
        Raises InvalidId if the string is not a valid ObjectId, which is
        caught explicitly in routes.py to return a clean 400 response
        instead of a raw 500 server error.
        """
        return ObjectId(task_id)

    @staticmethod
    def serialize_task(task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a MongoDB document into a JSON-serializable dict."""
        task["_id"] = str(task["_id"])
        return task

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def create_task(self, title: str, description: Optional[str]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            "title": title,
            "description": description,
            "completed": False,
            "created_at": now,
            "updated_at": now,
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return self.serialize_task(document)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        object_id = self.to_object_id(task_id)
        task = self.collection.find_one({"_id": object_id})
        return self.serialize_task(task) if task else None

    def get_tasks(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "newest",
    ) -> List[Dict[str, Any]]:
        """
        Retrieve tasks with optional filtering, searching and sorting.

        status: "active" | "completed" | None (all tasks)
        search: case-insensitive substring match on title
        sort:   "newest" | "oldest" (based on created_at)
        """
        query: Dict[str, Any] = {}

        if status == "active":
            query["completed"] = False
        elif status == "completed":
            query["completed"] = True

        if search:
            query["title"] = {"$regex": search, "$options": "i"}

        sort_direction = DESCENDING if sort == "newest" else ASCENDING
        cursor = self.collection.find(query).sort("created_at", sort_direction)

        return [self.serialize_task(task) for task in cursor]

    def update_task(
        self,
        task_id: str,
        update_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        object_id = self.to_object_id(task_id)
        update_data["updated_at"] = datetime.now(timezone.utc)

        result = self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=True,
        )
        return self.serialize_task(result) if result else None

    def set_completed(self, task_id: str, completed: bool) -> Optional[Dict[str, Any]]:
        return self.update_task(task_id, {"completed": completed})

    def delete_task(self, task_id: str) -> bool:
        object_id = self.to_object_id(task_id)
        result = self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1


# Singleton database instance used across the app
db = Database()
