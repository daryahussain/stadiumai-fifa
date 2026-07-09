import uuid
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.types import Uuid

from app.core.database import Base


class Stadium(Base):
    __tablename__ = "stadiums"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
