from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Environment variables are auto-provided by the platform
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[DATABASE_NAME]
    return _db

# Backwards-compatible alias expected by the app description
_db_alias = get_db

db = get_db()


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a document with automatic timestamps and return the created document."""
    now = datetime.now(timezone.utc)
    payload = {**data, "created_at": data.get("created_at", now), "updated_at": now}
    result = await db[collection_name].insert_one(payload)
    payload["_id"] = result.inserted_id
    return payload


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: int = 50,
    sort: Optional[List[tuple]] = None,
) -> List[Dict[str, Any]]:
    """Query documents with an optional filter, limit, and sort."""
    filter_dict = filter_dict or {}
    cursor = db[collection_name].find(filter_dict)
    if sort:
        cursor = cursor.sort(sort)
    if limit:
        cursor = cursor.limit(limit)
    return [doc async for doc in cursor]
