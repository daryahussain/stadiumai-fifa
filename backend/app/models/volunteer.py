import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.types import Uuid

from app.core.database import Base


class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    zone = Column(String, nullable=False)
    status = Column(String, default="available")
    is_active = Column(Boolean, default=True)
