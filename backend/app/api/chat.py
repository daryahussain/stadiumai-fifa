import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat_history import ChatHistory
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatHistoryResponse, StreamChunk
from app.services.llm import get_llm_response, stream_llm_response

router = APIRouter()


@router.post("/message")
async def chat_message(body: ChatMessageRequest, db: Session = Depends(get_db)):
    session_id = body.session_id or str(uuid.uuid4())

    user_msg = ChatHistory(
        session_id=session_id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    history_dicts = [{"role": h.role, "content": h.content} for h in history]

    ai_content = await get_llm_response(body.message, history_dicts[:-1], db)

    ai_msg = ChatHistory(
        session_id=session_id,
        role="assistant",
        content=ai_content,
    )
    db.add(ai_msg)
    db.commit()

    return {
        "session_id": session_id,
        "message": ChatMessageResponse(
            id=str(ai_msg.id),
            role="assistant",
            content=ai_content,
            created_at=ai_msg.created_at,
        ),
    }


@router.post("/stream")
async def chat_stream(body: ChatMessageRequest, db: Session = Depends(get_db)):
    session_id = body.session_id or str(uuid.uuid4())

    user_msg = ChatHistory(
        session_id=session_id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    history_dicts = [{"role": h.role, "content": h.content} for h in history]

    async def generate():
        full_content = ""
        async for token in stream_llm_response(body.message, history_dicts[:-1], db):
            full_content += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        ai_msg = ChatHistory(
            session_id=session_id,
            role="assistant",
            content=full_content,
        )
        db.add(ai_msg)
        db.commit()

        yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'message_id': str(ai_msg.id)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}")
async def chat_history(session_id: str, db: Session = Depends(get_db)):
    messages = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )
    return ChatHistoryResponse(
        messages=[
            ChatMessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                created_at=m.created_at,
            )
            for m in messages
        ]
    )
