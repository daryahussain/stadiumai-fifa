import asyncio
import logging
import random
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.crowd_data import CrowdData
from app.models.stadium import Stadium

logger = logging.getLogger(__name__)

ZONES = [
    "Gate A", "Gate B", "Gate C", "Gate D",
    "Section 100", "Section 200", "Section 300",
    "Food Court L1", "Food Court L2",
    "Parking Lot A", "Parking Lot B",
    "Concourse East", "Concourse West",
]


def _status_label(density_pct: float) -> str:
    if density_pct >= 80:
        return "congested"
    if density_pct >= 60:
        return "busy"
    if density_pct >= 40:
        return "moderate"
    return "clear"


class CrowdSimulator:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._running = False
        self._listeners: list[asyncio.Queue] = []

    def add_listener(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._listeners.append(q)
        return q

    def remove_listener(self, q: asyncio.Queue):
        if q in self._listeners:
            self._listeners.remove(q)

    async def _broadcast(self, data: dict):
        for q in self._listeners[:]:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                pass

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _run(self):
        while self._running:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"CrowdSimulator error: {e}")
            await asyncio.sleep(3)

    async def _tick(self):
        db: Session = SessionLocal()
        try:
            stadiums = db.query(Stadium).limit(3).all()
            if not stadiums:
                return

            now = datetime.now(timezone.utc)
            records = []
            for stadium in stadiums:
                for zone in ZONES:
                    base = random.uniform(0.2, 0.8)
                    density = round(max(0.05, min(1.0, base + random.uniform(-0.15, 0.15))), 2)
                    wait = max(1, int(density * 30 + random.randint(-5, 5)))
                    records.append(CrowdData(id=uuid4(), stadium_id=stadium.id, zone=zone, density=density, wait_time=wait, timestamp=now))

            db.add_all(records)
            db.commit()

            snapshot = self._build_snapshot(records, stadiums)
            await self._broadcast(snapshot)
        finally:
            db.close()

    def _build_snapshot(self, records: list[CrowdData], stadiums: list[Stadium]) -> dict:
        latest_per_zone = {}
        for r in records:
            if r.zone not in latest_per_zone:
                latest_per_zone[r.zone] = r

        total_capacity = sum(s.capacity for s in stadiums)
        zones = [
            {"zone": r.zone, "density": round(r.density * 100, 1), "status": _status_label(r.density * 100), "wait_time": r.wait_time or 0}
            for r in latest_per_zone.values()
        ]
        avg_density = round(sum(z["density"] for z in zones) / len(zones), 1) if zones else 0
        total_occupancy = int(total_capacity * avg_density / 100) if total_capacity else 0

        queues = [
            {"location": z["zone"], "type": "entry", "wait_minutes": z["wait_time"], "trend": random.choice(["rising", "falling", "stable"])}
            for z in zones[:5]
        ]

        return {
            "overview": {
                "total_occupancy": total_occupancy, "total_capacity": total_capacity,
                "avg_density": avg_density, "congestion_level": _status_label(avg_density),
            },
            "zones": zones,
            "queues": queues,
            "ai_summary": (
                f"Crowd density is currently {avg_density}% across all zones. "
                f"{'Gate areas are busy — consider using less congested entry points.' if avg_density > 60 else 'Traffic is flowing smoothly.'} "
                f"Parking occupancy is fluctuating."
            ),
        }


simulator = CrowdSimulator()
