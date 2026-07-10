from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, Dict
from datetime import datetime

class AuditCreate(BaseModel):
    url: HttpUrl = Field(..., description="The URL to audit")

class AuditResponse(BaseModel):
    id: int
    url: str
    status: str
    created_at: datetime

    performance: Optional[float] = None
    accessibility: Optional[float] = None
    best_practices: Optional[float] = None
    seo: Optional[float] = None
    first_contentful_paint: Optional[float] = None
    largest_contentful_paint: Optional[float] = None
    cumulative_layout_shift: Optional[float] = None

    security_checks: Optional[Dict[str, bool]] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
