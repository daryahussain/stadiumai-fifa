import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func

from app.core.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
