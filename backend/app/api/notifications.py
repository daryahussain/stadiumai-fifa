from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationListResponse, NotificationItem

router = APIRouter()

FALLBACK_NOTIFICATIONS = [
    {"id": "n1", "title": "Quarter-Final Tonight", "message": "France vs Morocco kicks off at 8PM ET at Gillette Stadium. Gates open at 5PM.", "type": "match"},
    {"id": "n2", "title": "Crowd Alert", "message": "Gate A is experiencing high traffic. Use Gate C for quicker entry.", "type": "crowd"},
    {"id": "n3", "title": "Transport Update", "message": "Stadium Express Metro running on schedule. Shuttle Bus 202 is experiencing minor delays.", "type": "transport"},
    {"id": "n4", "title": "Weather Advisory", "message": "Clear skies expected for tonight's match. Temperature at kickoff: 72°F.", "type": "weather"},
    {"id": "n5", "title": "Sustainability Milestone", "message": "All FIFA 2026 venues running on 40% solar energy today — a tournament record!", "type": "sustainability"},
]


@router.get("/")
async def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()

    if not notifications:
        return NotificationListResponse(
            notifications=[
                NotificationItem(
                    id=n["id"],
                    title=n["title"],
                    message=n["message"],
                    notification_type=n["type"],
                    is_read=False,
                    created_at=datetime.now(timezone.utc),
                )
                for n in FALLBACK_NOTIFICATIONS
            ],
            unread_count=len(FALLBACK_NOTIFICATIONS),
        )

    unread = db.query(Notification).filter(Notification.is_read.is_(False)).count()

    return NotificationListResponse(
        notifications=[
            NotificationItem(
                id=str(n.id),
                title=n.title,
                message=n.message,
                notification_type=n.notification_type,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ],
        unread_count=unread,
    )


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str, db: Session = Depends(get_db)):
    try:
        uid = UUID(notification_id)
    except ValueError:
        return {"status": "ok"}
    notification = db.query(Notification).filter(Notification.id == uid).first()
    if notification:
        notification.is_read = True
        db.commit()
    return {"status": "ok"}
