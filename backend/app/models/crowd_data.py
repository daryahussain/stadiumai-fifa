import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class CrowdData(Base):
    __tablename__ = "crowd_data"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    stadium_id = Column(Uuid, ForeignKey("stadiums.id"), nullable=False)
    zone = Column(String, nullable=False)
    density = Column(Float, nullable=False)
    wait_time = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
