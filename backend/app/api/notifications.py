from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationListResponse, NotificationItem

router = APIRouter()


@router.get("/")
async def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(20).all()
    unread = db.query(Notification).filter(Notification.is_read == False).count()  # noqa: E712

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
