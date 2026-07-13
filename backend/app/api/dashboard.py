from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, func

from app.core.database import get_db
from app.models.match import Match
from app.models.incident import Incident
from app.models.user import User
from app.models.stadium import Stadium
from app.schemas.dashboard import (
    DashboardResponse,
    StatCard,
    MatchItem,
    AlertItem,
    CrowdDataPoint,
)

router = APIRouter()

_STATS = [
    StatCard(label="Total Users", value="0", change="+12%", trend="up"),
    StatCard(label="Active Incidents", value="0", change="-3", trend="down"),
    StatCard(label="Stadium Capacity", value="0", change="72%", trend="neutral"),
    StatCard(label="AI Reports", value="24", change="+8", trend="up"),
]

_CROWD_TREND = [
    CrowdDataPoint(hour="08:00", density=20),
    CrowdDataPoint(hour="10:00", density=45),
    CrowdDataPoint(hour="12:00", density=80),
    CrowdDataPoint(hour="14:00", density=95),
    CrowdDataPoint(hour="16:00", density=70),
    CrowdDataPoint(hour="18:00", density=85),
    CrowdDataPoint(hour="20:00", density=60),
]


@router.get("/")
async def get_dashboard(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_incidents = db.query(func.count(Incident.id)).filter(Incident.status == "open").scalar() or 0
    total_capacity = db.query(func.sum(Stadium.capacity)).scalar() or 0

    today = datetime.now(timezone.utc).date()
    today_matches = (
        db.query(Match)
        .filter(cast(Match.match_date, Date) >= today)
        .order_by(Match.match_date.asc())
        .limit(5)
        .all()
    )

    recent_incidents = (
        db.query(Incident)
        .filter(Incident.status == "open")
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )

    return DashboardResponse(
        stats=[
            StatCard(label="Total Users", value=str(total_users), change="+12%", trend="up"),
            StatCard(label="Active Incidents", value=str(active_incidents), change="-3", trend="down"),
            StatCard(label="Stadium Capacity", value=f"{total_capacity:,}", change="72%", trend="neutral"),
            StatCard(label="AI Reports", value="24", change="+8", trend="up"),
        ],
        matches=[
            MatchItem(
                id=str(m.id),
                home_team=m.home_team,
                away_team=m.away_team,
                match_date=m.match_date,
                status=m.status,
                sold_tickets=m.sold_tickets,
                total_tickets=m.total_tickets,
            )
            for m in today_matches
        ] if today_matches else [],
        alerts=[
            AlertItem(
                id=str(i.id),
                type=i.incident_type,
                severity=i.severity,
                description=i.description or "",
                location=i.location or "",
                created_at=i.created_at,
            )
            for i in recent_incidents
        ],
        crowd_trend=_CROWD_TREND,
        ai_insight="Quarter-finals underway! France vs Morocco tonight. Crowd density at 72% across venues.",
    )
