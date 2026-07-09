import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    report_type = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    recommendations = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
