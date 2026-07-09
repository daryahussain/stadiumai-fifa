from pydantic import BaseModel


class Metric(BaseModel):
    label: str
    value: str
    unit: str
    change: str
    trend: str


class SustainabilityResponse(BaseModel):
    metrics: list[Metric]
    ai_recommendation: str
