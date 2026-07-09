from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = False


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]


class StreamChunk(BaseModel):
    token: str | None = None
    done: bool | None = None
    session_id: str | None = None
    message_id: str | None = None
