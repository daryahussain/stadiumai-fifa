import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class TransportOption(Base):
    __tablename__ = "transport_options"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    stadium_id = Column(Uuid, ForeignKey("stadiums.id"), nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="running")
    next_arrival = Column(String, default="")
    wait_minutes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    stadium_id = Column(Uuid, ForeignKey("stadiums.id"), nullable=False)
    lot = Column(String, nullable=False)
    available_spots = Column(Integer, default=0)
    total_spots = Column(Integer, default=0)
    distance_m = Column(Integer, default=0)
    status = Column(String, default="available")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
