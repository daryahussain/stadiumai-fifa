import asyncio
import os
from typing import AsyncGenerator

from sqlalchemy.orm import Session

STADIUM_CONTEXT = """You are StadiumAI, an AI assistant for the FIFA World Cup 2026.
You help fans with: stadium navigation, seat guidance, food, restrooms, match schedules, transportation, parking, emergency assistance, and general FAQs.
Be concise, friendly, and helpful."""


def _build_messages(message: str, history: list[dict]) -> list[dict]:
    messages = [{"role": "system", "content": STADIUM_CONTEXT}]
    for h in history[-10:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})
    return messages


async def get_llm_response(message: str, history: list[dict], db: Session = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=_build_messages(message, history),
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content or ""
        except Exception:
            return await get_smart_fallback(message, history, db)

    return await get_smart_fallback(message, history, db)


async def stream_llm_response(message: str, history: list[dict], db: Session = None) -> AsyncGenerator[str, None]:
    api_key = os.getenv("OPENAI_API_KEY", "")

    if api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=_build_messages(message, history),
                temperature=0.7,
                max_tokens=500,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception:
            async for token in stream_smart_fallback(message, history, db):
                yield token
    else:
        async for token in stream_smart_fallback(message, history, db):
            yield token


async def get_smart_fallback(message: str, history: list[dict], db: Session = None) -> str:
    from app.services.smart_chat import SmartChatEngine
    engine = SmartChatEngine()
    try:
        return await engine.get_response(message, history)
    except Exception:
        return _get_basic_fallback(message)


async def stream_smart_fallback(message: str, history: list[dict], db: Session = None) -> AsyncGenerator[str, None]:
    response = await get_smart_fallback(message, history, db)
    words = response.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.02)


def _get_basic_fallback(message: str) -> str:
    msg = message.lower()
    if "hello" in msg or "hi " in msg or "hey" in msg:
        return (
            "Hello! I'm your **StadiumAI** assistant for the FIFA World Cup 2026. "
            "I can help with navigation, matches, food, parking, and more. What would you like to know?"
        )
    if "seat" in msg or "where" in msg or "section" in msg or "gate" in msg:
        return (
            "Your seat is in **Section 214, Row 12**. "
            "Take the main concourse to Gate C, then follow the signs for Section 200. "
            "There's an elevator if you need wheelchair access."
        )
    if "food" in msg or "eat" in msg or "hungry" in msg:
        return (
            "There are several options:\n"
            "- **Fan Favorites** (Burgers & Fries) — Concourse Level\n"
            "- **World Bites** (International Cuisine) — Level 2\n"
            "- **Refresh Zone** (Drinks & Snacks) — Every concourse"
        )
    if "bathroom" in msg or "restroom" in msg or "toilet" in msg:
        return (
            "The nearest restrooms are **50m west** of your section, "
            "past the Fan Favorites food stand. Family restrooms are available on Level 1."
        )
    if "park" in msg or "parking" in msg:
        return (
            "Parking is available at **Lot A** (East Entrance) and **Lot B** (West Entrance). "
            "Lot A is currently at 80% capacity. I'd recommend **Lot B**."
        )
    if "transport" in msg or "bus" in msg or "metro" in msg or "train" in msg:
        return (
            "The **Stadium Express Metro** runs every 5 minutes from Downtown. "
            "Get off at **World Cup Station**. "
            "Shuttle buses are also operating from the City Center parking lots."
        )
    if "match" in msg or "game" in msg or "schedule" in msg:
        return (
            "Today's matches:\n"
            "- **12:00** — Brazil vs Argentina\n"
            "- **16:00** — Germany vs France\n"
            "- **20:00** — Japan vs Spain\n\n"
            "Gates open 2 hours before each match."
        )
    if "crowd" in msg or "crowded" in msg or "busy" in msg:
        return (
            "Crowd conditions are currently **moderate**. "
            "Gate A is the busiest area. I'd recommend using Gate C for quicker entry."
        )
    if "emergency" in msg or "help" in msg or "lost" in msg:
        return (
            "If this is an emergency, please contact the nearest staff member or call **+1-800-FIFA-HELP**.\n\n"
            "For a lost child, go to the **Guest Services** desk near Gate A. "
            "Medical stations are located on every concourse level."
    )
    return (
        "I'd be happy to help! You can ask me about:\n\n"
        "- **Seats & Navigation**\n"
        "- **Food & Restrooms**\n"
        "- **Parking & Transport**\n"
        "- **Match Schedule**\n"
        "- **Crowd Conditions**\n"
        "- **Emergency Assistance**\n\n"
        "What would you like to know?"
    )
