from __future__ import annotations

from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import DemoRequest

app = FastAPI(title="Project Nexus API", version="1.0.0")

# Allow frontend origin via env or default wildcard for sandbox convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/test")
async def test_db():
    # Try listing collections to ensure DB connectivity
    try:
        names = await db.list_collection_names()
        return {"ok": True, "collections": names}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/demo-request")
async def demo_request(payload: DemoRequest):
    try:
        doc = await create_document("demorequest", payload.model_dump())
        # Convert ObjectId to string for JSON
        if isinstance(doc.get("_id"), ObjectId):
            doc["id"] = str(doc.pop("_id"))
        return {"success": True, "data": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
