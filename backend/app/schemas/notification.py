from datetime import datetime
from pydantic import BaseModel


class NotificationItem(BaseModel):
    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[NotificationItem]
    unread_count: int
