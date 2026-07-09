from pydantic import BaseModel


class RouteRequest(BaseModel):
    from_location: str
    to_location: str
    wheelchair: bool = False


class RouteStep(BaseModel):
    instruction: str
    distance_m: int
    landmark: str


class RouteResponse(BaseModel):
    from_location: str
    to_location: str
    total_distance_m: int
    estimated_minutes: int
    steps: list[RouteStep]
    wheelchair_accessible: bool


class GateInfo(BaseModel):
    gate: str
    recommended_for: list[str]
    distance_m: int
    crowd_level: str


class NavigationData(BaseModel):
    zones: list[str]
    gates: list[GateInfo]
    amenities: list[str]
