from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.sustainability_log import SustainabilityLog
from app.models.ai_report import AIReport
from app.schemas.sustainability import SustainabilityResponse, Metric
from app.data import fifa2026

router = APIRouter()

METRIC_LABELS = {
    "waste_generated": "Waste Generated",
    "water_usage": "Water Usage",
    "electricity": "Electricity",
    "recycled_waste": "Recycled Waste",
    "carbon_footprint": "Carbon Footprint",
    "solar_generated": "Solar Generated",
}


@router.get("/")
async def get_sustainability(db: Session = Depends(get_db)):
    logs = db.query(SustainabilityLog).all()

    if not logs:
        return SustainabilityResponse(
            metrics=[
                Metric(
                    label=METRIC_LABELS.get(s["metric"], s["metric"].replace("_", " ").title()),
                    value=str(s["value"]),
                    unit=s["unit"],
                    change="0%",
                    trend="neutral",
                )
                for s in fifa2026.SUSTAINABILITY_LOGS
            ],
            ai_recommendation="All sustainability metrics are within normal range. "
                              "The FIFA 2026 tournament is committed to net-zero carbon emissions. "
                              "Solar panels across host stadiums generated 8.2 MWh today.",
        )

    latest_report = db.query(AIReport).filter(AIReport.report_type == "sustainability").order_by(AIReport.generated_at.desc()).first()

    return SustainabilityResponse(
        metrics=[
            Metric(
                label=METRIC_LABELS.get(log.metric_type, log.metric_type.replace("_", " ").title()),
                value=str(log.value),
                unit=log.unit,
                change="0%",
                trend="neutral",
            )
            for log in logs
        ],
        ai_recommendation=latest_report.summary if latest_report else "All sustainability metrics are within normal range.",
    )
