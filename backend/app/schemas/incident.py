from datetime import datetime
from pydantic import BaseModel


class ReportIncidentRequest(BaseModel):
    incident_type: str
    description: str
    location: str
    severity: int = 1


class IncidentResponse(BaseModel):
    id: str
    incident_type: str
    severity: int
    description: str
    location: str
    status: str
    created_at: datetime
    ai_response: str
