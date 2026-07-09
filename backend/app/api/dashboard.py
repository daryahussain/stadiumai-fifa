from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date

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


@router.get("/")
async def get_dashboard(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_incidents = db.query(Incident).filter(Incident.status == "open").count()
    total_stadiums = db.query(Stadium).count()

    if total_stadiums == 0:
        from app.data import fifa2026
        total_capacity = sum(s["capacity"] for s in fifa2026.STADIUMS)
        today_matches = []
        for m in fifa2026.MATCHES:
            if m["status"] in ("scheduled", "in_progress"):
                if m["id"] in ("m8", "m9", "m10", "m11", "m12", "m13", "m14", "m15"):
                    today_matches.append(MatchItem(
                        id=m["id"],
                        home_team=m["home"],
                        away_team=m["away"],
                        match_date=datetime.fromisoformat(f"{m['date']}T{m['time'].split(' ')[0]}:00"),
                        status=m["status"],
                        sold_tickets=0,
                        total_tickets=0,
                    ))
        return DashboardResponse(
            stats=[
                StatCard(label="Total Users", value=str(total_users), change="+12%", trend="up"),
                StatCard(label="Active Incidents", value=str(active_incidents), change="-3", trend="down"),
                StatCard(label="Stadium Capacity", value=f"{total_capacity:,}", change="72%", trend="neutral"),
                StatCard(label="AI Reports", value="24", change="+8", trend="up"),
            ],
            matches=today_matches[:5] if today_matches else [
                MatchItem(id="m9", home_team="France", away_team="Morocco", match_date=datetime(2026, 7, 9, 20, 0, tzinfo=timezone.utc), status="scheduled", sold_tickets=64146, total_tickets=64146),
                MatchItem(id="m8", home_team="Spain", away_team="Belgium", match_date=datetime(2026, 7, 10, 19, 0, tzinfo=timezone.utc), status="scheduled", sold_tickets=70492, total_tickets=70492),
                MatchItem(id="m10", home_team="Norway", away_team="England", match_date=datetime(2026, 7, 11, 21, 0, tzinfo=timezone.utc), status="scheduled", sold_tickets=64478, total_tickets=64478),
                MatchItem(id="m11", home_team="Argentina", away_team="Switzerland", match_date=datetime(2026, 7, 12, 21, 0, tzinfo=timezone.utc), status="scheduled", sold_tickets=69045, total_tickets=69045),
            ],
            alerts=[
                AlertItem(id="a1", type="crowd", severity=2, description="Gate A at MetLife operating at 75% capacity — recommend opening auxiliary gates", location="MetLife Stadium", created_at=datetime(2026, 7, 9, 14, 0, tzinfo=timezone.utc)),
            ],
            crowd_trend=[
                CrowdDataPoint(hour="08:00", density=20),
                CrowdDataPoint(hour="10:00", density=45),
                CrowdDataPoint(hour="12:00", density=80),
                CrowdDataPoint(hour="14:00", density=95),
                CrowdDataPoint(hour="16:00", density=70),
                CrowdDataPoint(hour="18:00", density=85),
                CrowdDataPoint(hour="20:00", density=60),
            ],
            ai_insight="Quarter-finals are underway! France vs Morocco tonight at Gillette Stadium (8PM ET). Spain vs Belgium tomorrow at SoFi. Crowd density peaking at Gate A — redirecting fans via auxiliary entries.",
        )

    total_capacity = sum(s.capacity for s in db.query(Stadium).all())

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
        ],
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
        crowd_trend=[
            CrowdDataPoint(hour="08:00", density=20),
            CrowdDataPoint(hour="10:00", density=45),
            CrowdDataPoint(hour="12:00", density=80),
            CrowdDataPoint(hour="14:00", density=95),
            CrowdDataPoint(hour="16:00", density=70),
            CrowdDataPoint(hour="18:00", density=85),
            CrowdDataPoint(hour="20:00", density=60),
        ],
        ai_insight="Quarter-finals underway! France vs Morocco tonight. Crowd density at 72% across venues.",
    )
