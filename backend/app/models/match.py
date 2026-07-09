import uuid
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    stadium_id = Column(Uuid, nullable=False)
    match_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="scheduled")
    total_tickets = Column(Integer, default=0)
    sold_tickets = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
