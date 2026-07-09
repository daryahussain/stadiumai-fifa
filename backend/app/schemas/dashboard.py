from datetime import datetime
from pydantic import BaseModel


class StatCard(BaseModel):
    label: str
    value: str
    change: str
    trend: str


class MatchItem(BaseModel):
    id: str
    home_team: str
    away_team: str
    match_date: datetime
    status: str
    sold_tickets: int
    total_tickets: int


class AlertItem(BaseModel):
    id: str
    type: str
    severity: int
    description: str
    location: str
    created_at: datetime


class CrowdDataPoint(BaseModel):
    hour: str
    density: float


class DashboardResponse(BaseModel):
    stats: list[StatCard]
    matches: list[MatchItem]
    alerts: list[AlertItem]
    crowd_trend: list[CrowdDataPoint]
    ai_insight: str
