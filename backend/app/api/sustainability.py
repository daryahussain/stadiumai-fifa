from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sustainability_log import SustainabilityLog
from app.models.ai_report import AIReport
from app.schemas.sustainability import SustainabilityResponse, Metric
from app.data import fifa2026

router = APIRouter()

METRIC_LABELS: dict[str, str] = {
    "waste_generated": "Waste Generated",
    "water_usage": "Water Usage",
    "electricity": "Electricity",
    "recycled_waste": "Recycled Waste",
    "carbon_footprint": "Carbon Footprint",
    "solar_generated": "Solar Generated",
}

_DEFAULT_RECOMMENDATION = "All sustainability metrics are within normal range. The FIFA 2026 tournament is committed to net-zero carbon emissions. Solar panels across host stadiums generated 8.2 MWh today."


def _dict_to_metric(s: dict) -> Metric:
    label = METRIC_LABELS.get(s["metric"], s["metric"].replace("_", " ").title())
    return Metric(label=label, value=str(s["value"]), unit=s["unit"], change="0%", trend="neutral")


@router.get("/")
async def get_sustainability(db: Session = Depends(get_db)):
    logs = db.query(SustainabilityLog).all()

    if not logs:
        return SustainabilityResponse(
            metrics=[_dict_to_metric(s) for s in fifa2026.SUSTAINABILITY_LOGS],
            ai_recommendation=_DEFAULT_RECOMMENDATION,
        )

    latest_report = db.query(AIReport).filter(AIReport.report_type == "sustainability").order_by(AIReport.generated_at.desc()).first()

    def log_to_metric(log) -> Metric:
        label = METRIC_LABELS.get(log.metric_type, log.metric_type.replace("_", " ").title())
        return Metric(label=label, value=str(log.value), unit=log.unit, change="0%", trend="neutral")

    return SustainabilityResponse(
        metrics=[log_to_metric(log) for log in logs],
        ai_recommendation=latest_report.summary if latest_report else _DEFAULT_RECOMMENDATION,
    )
