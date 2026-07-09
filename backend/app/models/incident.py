import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    reporter_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    incident_type = Column(String, nullable=False)
    severity = Column(Integer, default=1)
    description = Column(Text)
    location = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
