from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class DemoRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr


class DemoRequestOut(DemoRequest):
    id: Optional[str] = None
    status: str = "received"
