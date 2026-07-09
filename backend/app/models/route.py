import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.types import Uuid

from app.core.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    stadium_id = Column(Uuid, ForeignKey("stadiums.id"), nullable=False)
    name = Column(String, nullable=False)
    start_location = Column(String, nullable=False)
    end_location = Column(String, nullable=False)
    distance_km = Column(Float)
    wheelchair_accessible = Column(String, default="no")
