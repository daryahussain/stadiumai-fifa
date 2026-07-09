import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class SustainabilityLog(Base):
    __tablename__ = "sustainability_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    stadium_id = Column(Uuid, ForeignKey("stadiums.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
