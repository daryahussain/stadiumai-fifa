import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.incident import ReportIncidentRequest, IncidentResponse

router = APIRouter()

INCIDENT_TYPES = ["medical", "security", "fire", "lost_child", "suspicious_activity", "maintenance"]


@router.get("/incidents")
async def get_incidents():
    return {"incidents": []}


@router.post("/incidents")
async def report_incident(body: ReportIncidentRequest):
    if body.incident_type not in INCIDENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {', '.join(INCIDENT_TYPES)}")
    if body.severity < 1 or body.severity > 5:
        raise HTTPException(status_code=400, detail="Severity must be between 1 and 5")

    severity_responses = {
        1: "Low priority incident logged. Routine monitoring in place.",
        2: "Moderate priority. Staff has been notified to check the area.",
        3: "Medium priority. Security personnel are being dispatched.",
        4: "High priority. Emergency response team is en route.",
        5: "Critical! All available units are being deployed immediately.",
    }

    return IncidentResponse(
        id=str(uuid.uuid4()),
        incident_type=body.incident_type,
        severity=body.severity,
        description=body.description,
        location=body.location,
        status="reported",
        created_at=datetime.now(timezone.utc),
        ai_response=severity_responses.get(body.severity, "Incident reported."),
    )
