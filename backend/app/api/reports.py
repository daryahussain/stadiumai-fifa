from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.incident import Incident
from app.models.user import User
from app.schemas.incident import ReportIncidentRequest, IncidentResponse

router = APIRouter()

INCIDENT_TYPES = ["medical", "security", "fire", "lost_child", "suspicious_activity", "maintenance"]

SEVERITY_RESPONSES = {
    1: "Low priority incident logged. Routine monitoring in place.",
    2: "Moderate priority. Staff has been notified to check the area.",
    3: "Medium priority. Security personnel are being dispatched.",
    4: "High priority. Emergency response team is en route.",
    5: "Critical! All available units are being deployed immediately.",
}


@router.get("/incidents")
async def get_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(50).all()
    return {
        "incidents": [
            IncidentResponse(
                id=str(inc.id),
                incident_type=inc.incident_type,
                severity=inc.severity,
                description=inc.description or "",
                location=inc.location or "",
                status=inc.status,
                created_at=inc.created_at,
                ai_response="",
            )
            for inc in incidents
        ]
    }


@router.post("/incidents")
async def report_incident(
    body: ReportIncidentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.incident_type not in INCIDENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {', '.join(INCIDENT_TYPES)}")
    if body.severity < 1 or body.severity > 5:
        raise HTTPException(status_code=400, detail="Severity must be between 1 and 5")

    incident = Incident(
        reporter_id=current_user.id,
        incident_type=body.incident_type,
        severity=body.severity,
        description=body.description,
        location=body.location,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return IncidentResponse(
        id=str(incident.id),
        incident_type=incident.incident_type,
        severity=incident.severity,
        description=incident.description or "",
        location=incident.location or "",
        status=incident.status,
        created_at=incident.created_at,
        ai_response=SEVERITY_RESPONSES.get(body.severity, "Incident reported."),
    )
