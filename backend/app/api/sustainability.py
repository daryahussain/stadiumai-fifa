from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.sustainability_log import SustainabilityLog
from app.models.ai_report import AIReport
from app.schemas.sustainability import SustainabilityResponse, Metric

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
    latest_per_metric = (
        db.query(
            SustainabilityLog.metric_type,
            func.max(SustainabilityLog.timestamp).label("max_ts"),
        )
        .group_by(SustainabilityLog.metric_type)
        .subquery()
    )

    logs = (
        db.query(SustainabilityLog)
        .join(
            latest_per_metric,
            (SustainabilityLog.metric_type == latest_per_metric.c.metric_type)
            & (SustainabilityLog.timestamp == latest_per_metric.c.max_ts),
        )
        .all()
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
