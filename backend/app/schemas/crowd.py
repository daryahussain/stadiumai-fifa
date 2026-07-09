from pydantic import BaseModel


class ZoneDensity(BaseModel):
    zone: str
    density: float
    status: str
    wait_time: int


class QueueInfo(BaseModel):
    location: str
    type: str
    wait_minutes: int
    trend: str


class CrowdOverview(BaseModel):
    total_occupancy: int
    total_capacity: int
    avg_density: float
    congestion_level: str


class CrowdResponse(BaseModel):
    overview: CrowdOverview
    zones: list[ZoneDensity]
    queues: list[QueueInfo]
    ai_summary: str
