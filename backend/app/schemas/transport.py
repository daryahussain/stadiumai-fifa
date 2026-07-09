from pydantic import BaseModel


class TransportOption(BaseModel):
    type: str
    name: str
    status: str
    next_arrival: str
    wait_minutes: int


class ParkingInfo(BaseModel):
    lot: str
    available_spots: int
    total_spots: int
    distance_m: int
    status: str


class TransportResponse(BaseModel):
    options: list[TransportOption]
    parking: list[ParkingInfo]
    ai_recommendation: str
