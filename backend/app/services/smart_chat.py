import re
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime as dt
from enum import Enum
from functools import lru_cache
from typing import Optional

from app.data import fifa2026


class IntentType(str, Enum):
    GREETING = "greeting"
    GOODBYE = "goodbye"
    SEAT = "seat"
    NAVIGATION = "navigation"
    FOOD = "food"
    RESTROOM = "restroom"
    PARKING = "parking"
    TRANSPORT = "transport"
    MATCH_SCHEDULE = "match_schedule"
    MATCH_INFO = "match_info"
    CROWD = "crowd"
    CAPACITY = "capacity"
    STADIUM_INFO = "stadium_info"
    EMERGENCY = "emergency"
    VOLUNTEER = "volunteer"
    SUSTAINABILITY = "sustainability"
    CAPABILITIES = "capabilities"
    UNKNOWN = "unknown"


@dataclass
class ConversationContext:
    last_intents: list[IntentType] = field(default_factory=list)
    last_entities: dict = field(default_factory=dict)
    topics: deque = field(default_factory=lambda: deque(maxlen=5))
    turn_count: int = 0
    last_stadium_id: Optional[str] = None

    def update(self, intents: list[IntentType], entities: dict):
        self.turn_count += 1
        self.last_intents = intents
        if entities:
            self.last_entities.update(entities)
        for intent in intents:
            detail = entities.get("stadium") or entities.get("zone") or ""
            self.topics.append((intent, detail))

    def last_topic(self) -> Optional[IntentType]:
        return self.topics[-1][0] if self.topics else None

    def last_topic_detail(self) -> str:
        return self.topics[-1][1] if self.topics else ""


_INTENT_PATTERNS: list[tuple[IntentType, list[str]]] = [
    (IntentType.GREETING, [r"\b(hello|hi|hey|good morning|good afternoon|good evening|howdy|sup|yo)\b"]),
    (IntentType.GOODBYE, [r"\b(thanks|thank you|goodbye|bye|see you|cheers|appreciate it|that's all)\b"]),
    (IntentType.SEAT, [r"\b(seat|section|row|where (am i|is my)|my seat|gate\s*[a-d]|sitting)\b"]),
    (IntentType.NAVIGATION, [r"\b(how (do i|to) get|direction|where is|nearest|way to|navigate|route|map|guide me|walk|stair|elevator|escalator|entrance|exit|how do i)\b"]),
    (IntentType.FOOD, [r"\b(food|eat|hungry|restaurant|burger|pizza|snack|drink|water|coffee|concession|dining|menu|meal|lunch|dinner|breakfast)\b"]),
    (IntentType.RESTROOM, [r"\b(restroom|bathroom|toilet|washroom|loo|lavatory)\b"]),
    (IntentType.PARKING, [r"\b(park|parking|lot|garage|valet|car|drive)\b"]),
    (IntentType.TRANSPORT, [r"\b(transport|bus|metro|train|shuttle|taxi|uber|lyft|subway|station|stop|ride|drop off|pick up|commute|get (to|there|here|from))\b"]),
    (IntentType.MATCH_SCHEDULE, [r"\b(schedule|match|game|fixture|play|when (is|does|are)|what time|today[']?s match|upcoming|next game|today[']?s game)\b"]),
    (IntentType.MATCH_INFO, [r"\b(score|who (is|are) playing|teams|vs|versus|result|won|lost|winner|loser|half time|full time|kickoff)\b"]),
    (IntentType.CROWD, [r"\b(crowd|crowded|busy|density|wait (time|line)|queue|traffic|congestion|how full|capacity now|occupancy|packed|empty|people|foot traffic)\b"]),
    (IntentType.CAPACITY, [r"\b(capacity|how many people|size|big|large|holds|seats|accommodate)\b"]),
    (IntentType.STADIUM_INFO, [r"\b(stadium|venue|arena|ground|field|about|tell me about)\b"]),
    (IntentType.EMERGENCY, [r"\b(emergency|help|lost|injured|hurt|accident|medical|doctor|nurse|ambulance|police|security|danger|fire|first aid)\b"]),
    (IntentType.VOLUNTEER, [r"\b(volunteer|staff|worker|marshal|steward|help desk|information|guest service)\b"]),
    (IntentType.SUSTAINABILITY, [r"\b(sustainability|green|eco|environment|solar|recycle|waste|energy|carbon|water|environmental)\b"]),
]

_FOLLOWUP_PATTERNS = [
    r"^(what about|and|also|how about|what's|tell me more|more|elaborate)",
    r"^(that|there|it|they|them)",
    r"^(where|how|when|why|who|which)\s+(is|are|can|do|does|will)",
]

_TOTAL_STADIUM_CAPACITY = sum(s["capacity"] for s in fifa2026.STADIUMS)
_TOTAL_MATCHES = len(fifa2026.MATCHES)
_AVG_TICKETS_PER_MATCH = int(_TOTAL_STADIUM_CAPACITY / _TOTAL_MATCHES) if _TOTAL_MATCHES else 0


class EntityExtractor:
    STADIUM_NAMES = {
        "metlife": "MetLife Stadium", "at&t": "AT&T Stadium", "sofi": "SoFi Stadium",
        "mercedes-benz": "Mercedes-Benz Stadium", "mercedes": "Mercedes-Benz Stadium",
        "nrg": "NRG Stadium", "lincoln financial": "Lincoln Financial Field",
        "lumen": "Lumen Field", "levi": "Levi's Stadium", "levi's": "Levi's Stadium",
        "gillette": "Gillette Stadium", "hard rock": "Hard Rock Stadium",
        "estadio azteca": "Estadio Azteca", "azteca": "Estadio Azteca",
    }

    TEAM_NAMES = ["usa", "united states", "mexico", "canada", "brazil", "argentina",
        "germany", "france", "england", "spain", "portugal", "netherlands",
        "italy", "belgium", "croatia", "uruguay", "japan", "south korea",
        "australia", "senegal", "ghana", "nigeria", "cameroon", "morocco",
        "saudi arabia", "iran", "qatar", "switzerland", "poland", "denmark"]

    @classmethod
    def extract(cls, message: str) -> dict:
        msg_lower = message.lower()
        entities = {}

        for key, name in cls.STADIUM_NAMES.items():
            if key in msg_lower:
                entities["stadium"] = name
                break

        found_teams = [t for t in cls.TEAM_NAMES if t in msg_lower]
        if found_teams:
            entities["teams"] = found_teams

        zone_match = re.search(r"(gate\s*[a-d]|section\s+\d+|food\s+court|fan\s+zone|concourse)", msg_lower)
        if zone_match:
            entities["zone"] = zone_match.group(1).title()

        num_match = re.search(r"(\d+)", msg_lower)
        if num_match:
            entities["number"] = num_match.group(1)

        return entities


class IntentClassifier:
    _PRIORITY: dict[IntentType, int] = {
        IntentType.EMERGENCY: 100, IntentType.GOODBYE: 90, IntentType.GREETING: 10,
    }

    def __init__(self, context: ConversationContext):
        self.context = context

    def classify(self, message: str) -> list[IntentType]:
        msg_lower = message.lower().strip()

        matched = []
        seen = set()

        if self.context.turn_count > 0 and self._is_followup(msg_lower):
            last = self.context.last_topic()
            if last:
                matched.append(last)
                seen.add(last)

        for intent, patterns in _INTENT_PATTERNS:
            if intent in seen:
                continue
            for pattern in patterns:
                if re.search(pattern, msg_lower):
                    matched.append(intent)
                    seen.add(intent)
                    break

        if not matched:
            return [IntentType.UNKNOWN]

        if IntentType.GREETING in seen and len(matched) > 1:
            matched = [m for m in matched if m != IntentType.GREETING]
        if IntentType.GOODBYE in seen and len(matched) > 1:
            matched = [m for m in matched if m != IntentType.GOODBYE]
        if IntentType.STADIUM_INFO in seen and IntentType.CAPACITY in seen:
            matched = [m for m in matched if m != IntentType.STADIUM_INFO]

        matched.sort(key=lambda x: self._PRIORITY.get(x, 50), reverse=True)
        return matched

    def _is_followup(self, msg: str) -> bool:
        msg = msg.strip().rstrip("?.")
        return bool(msg) and any(re.match(pat, msg, re.IGNORECASE) for pat in _FOLLOWUP_PATTERNS)


@lru_cache(maxsize=1)
def _get_all_stadiums():
    return fifa2026.STADIUMS


@lru_cache(maxsize=32)
def _get_stadium_by_name(name: str) -> Optional[dict]:
    nl = name.lower()
    for s in _get_all_stadiums():
        if nl in s["name"].lower() or nl in s["city"].lower():
            return s
    return None


@lru_cache(maxsize=1)
def _get_first_stadium() -> dict:
    return _get_all_stadiums()[0]


@lru_cache(maxsize=1)
def _get_all_matches():
    return tuple(sorted(fifa2026.MATCHES, key=lambda m: m["date"]))


@lru_cache(maxsize=1)
def _get_all_zones():
    return tuple(fifa2026.ZONES)


@lru_cache(maxsize=1)
def _get_all_routes():
    return tuple(fifa2026.ROUTES)


@lru_cache(maxsize=1)
def _get_all_transport_options():
    return tuple(fifa2026.TRANSPORT_OPTIONS)


@lru_cache(maxsize=1)
def _get_all_parking_lots():
    return tuple(fifa2026.PARKING_LOTS)


@lru_cache(maxsize=1)
def _get_all_sustainability_logs():
    return tuple(fifa2026.SUSTAINABILITY_LOGS)


def get_stadium_id(stadium_name: str = None) -> Optional[str]:
    if stadium_name:
        s = _get_stadium_by_name(stadium_name)
        if s:
            return s["id"]
    return _get_first_stadium()["id"]


class DataRetriever:
    def get_stadiums(self) -> list:
        return _get_all_stadiums()

    def get_stadium_by_name(self, name: str) -> Optional[dict]:
        return _get_stadium_by_name(name)

    def get_first_stadium(self) -> dict:
        return _get_first_stadium()

    def get_matches(self, limit: int = 5) -> list:
        return list(_get_all_matches()[:limit])

    def get_matches_by_team(self, team: str, limit: int = 3) -> list:
        tl = team.lower()
        filtered = [m for m in _get_all_matches() if tl in m["home"].lower() or tl in m["away"].lower()]
        return list(filtered[:limit])

    def get_crowd_data(self, stadium_id=None, limit: int = 20) -> list:
        return list(_get_all_zones()[:limit])

    def get_routes(self, stadium_id=None, limit: int = 10) -> list:
        return list(_get_all_routes()[:limit])

    def get_transport_options(self, stadium_id=None) -> list:
        return list(_get_all_transport_options())

    def get_parking_lots(self, stadium_id=None) -> list:
        return list(_get_all_parking_lots())

    def get_sustainability_logs(self, stadium_id=None) -> list:
        return list(_get_all_sustainability_logs())

    def get_volunteers(self) -> list:
        return list(fifa2026.VOLUNTEER_ZONES)


class ResponseGenerator:
    @staticmethod
    def greeting():
        return "Hello! I'm your **StadiumAI** assistant for the FIFA World Cup 2026. I can help you with:\n\n- 🏟️ **Stadium info** — capacity, location, details\n- 🎫 **Match schedules** — teams, dates, tickets\n- 🪑 **Seat guidance** — where your seat is\n- 🚶 **Navigation** — directions around the venue\n- 🍕 **Food & restrooms** — nearest options\n- 🚗 **Parking & transport** — lots, shuttles, metro\n- 📊 **Crowd conditions** — density, wait times\n- 🆘 **Emergency** — first aid, lost & found\n\nWhat would you like to know?"

    @staticmethod
    def goodbye():
        return "You're welcome! Enjoy the match! 🎉\n\nIf you need anything else, I'm just a message away."

    @staticmethod
    def capabilities():
        return "Here's what I can help you with:\n\n- **Seats & Navigation** — \"Where is my seat?\"\n- **Food** — \"Where can I eat?\"\n- **Restrooms** — \"Where's the nearest restroom?\"\n- **Parking** — \"Where should I park?\"\n- **Transport** — \"How do I get to the stadium?\"\n- **Schedule** — \"When is the next match?\"\n- **Crowd** — \"How crowded is it?\"\n- **Emergency** — \"I need help\"\n\nWhat would you like to know?"

    @staticmethod
    def stadium_info(stadium: dict) -> str:
        return f"**{stadium['name']}** in {stadium['city']} has a capacity of **{stadium['capacity']:,}** seats. It's one of the FIFA World Cup 2026 host venues."

    @staticmethod
    def match_schedule(matches: list) -> str:
        if not matches:
            return "There are no matches scheduled at this time."
        lines = ["Here are the upcoming matches:\n"]
        for m in matches:
            lines.append(f"- **{m['home']}** vs **{m['away']}**")
        return "\n".join(lines)

    @staticmethod
    def match_details(matches: list) -> str:
        if not matches:
            return "I couldn't find information about that match."
        lines = []
        for m in matches:
            lines.append(f"**{m['home']}** vs **{m['away']}** — {_AVG_TICKETS_PER_MATCH:,} / {_TOTAL_STADIUM_CAPACITY:,} tickets sold, status: **{m.get('status', 'scheduled')}**")
        return "\n".join(lines)

    @staticmethod
    def seat_guidance(_stadium=None):
        return "Your seat is located in **Section 214, Row 12**. Take the main concourse to **Gate C**, then follow signs for **Section 200**. There's an elevator available for wheelchair access.\n\nWould you like directions from a specific entrance?"

    @staticmethod
    def navigation(zone: str = "", routes: list = None) -> str:
        if routes:
            lines = ["Here are some available routes:\n"]
            for r in routes:
                wc = "♿ Wheelchair accessible" if r.get("wc") == "yes" else ""
                lines.append(f"- **{r['start']}** → **{r['end']}** ({r['dist']} km) {wc}".strip())
            return "\n".join(lines)
        return "The stadium concourse connects all sections. Use the signs overhead to find **Gates A-D**, **Sections 100-300**, the **Food Court**, and **Restrooms**.\n\nNeed directions between two specific points?"

    @staticmethod
    def food() -> str:
        return "There are several food options available:\n\n- **Fan Favorites** (Burgers & Fries) — Concourse Level\n- **World Bites** (International Cuisine) — Level 2\n- **Refresh Zone** (Drinks & Snacks) — Every concourse\n- **Kickoff Coffee** — Near Gate A\n\nWhat are you in the mood for?"

    @staticmethod
    def restroom() -> str:
        return "The nearest restrooms are **50m west** of your section, past the Fan Favorites food stand. Family restrooms are available on **Level 1**, and accessible restrooms are on every concourse."

    @staticmethod
    def parking(lots: list = None) -> str:
        if lots:
            lines = ["Here are the available parking options:\n"]
            for lot in lots:
                status_icon = "🟢" if lot["status"] == "available" else "🟡" if lot["status"] == "filling" else "🔴"
                lines.append(f"{status_icon} **{lot['lot']}** — {lot['available']}/{lot['total']} spots, {lot['dist']}m from gate")
            return "\n".join(lines)
        return "Parking is available at **Lot A** (East Entrance) and **Lot B** (West Entrance). Lot A is currently at 80% capacity. I'd recommend **Lot B** — it's less crowded and a short 5-minute walk to Gate 3."

    @staticmethod
    def transport(options: list = None) -> str:
        if options:
            lines = ["Here are the available transport options:\n"]
            for opt in options:
                status_icon = "🟢" if opt["status"] == "running" else "🟡" if opt["status"] == "delayed" else "🔴"
                lines.append(f"{status_icon} **{opt['name']}** ({opt['type']}) — {opt['status']}, next arrival {opt['next']}")
            return "\n".join(lines)
        return "The **Stadium Express Metro** runs every 5 minutes from Downtown. Get off at **World Cup Station**. Shuttle buses are also operating from the City Center parking lots."

    @staticmethod
    def crowd(zones: list = None) -> str:
        if zones:
            import random
            zone_data = [(z, round(0.2 + 0.6 * (hash(z) % 100) / 100, 2)) for z in zones]
            total_density = sum(d for _, d in zone_data) / len(zone_data)
            busy_zones = sorted(zone_data, key=lambda x: x[1], reverse=True)[:3]
            level = "🟢 Low" if total_density < 0.4 else "🟡 Moderate" if total_density < 0.7 else "🔴 High"
            lines = [f"Crowd level: **{level}** (avg density: {total_density:.0%})\n", "Busiest areas:"]
            for z, d in busy_zones:
                lines.append(f"- **{z}**: density {d:.0%}")
            return "\n".join(lines)
        return "Crowd conditions are currently **moderate** across the stadium. **Gate A** is the busiest area. I'd recommend using **Gate C** for quicker entry."

    @staticmethod
    def emergency():
        return "🆘 **Emergency Assistance**\n\nIf this is a **medical emergency**, please contact the nearest staff member or call **+1-800-FIFA-HELP** immediately.\n\n- **Medical stations** are located on every concourse level\n- **Lost child** — report to Guest Services near Gate A\n- **Security concerns** — notify any staff member or call the hotline\n\nStay calm and follow the instructions of stadium personnel."

    @staticmethod
    def volunteer():
        return "Volunteers and staff are available throughout the stadium. Look for staff in **yellow vests** at:\n\n- **Gate A, B, C, D** — Entry assistance\n- **Fan Zone** — Information & activities\n- **Section 100** — Seating help\n- **Parking** — Traffic direction\n\nGuest Services desks are located near Gates A and C."

    @staticmethod
    def sustainability(logs: list = None) -> str:
        if logs:
            lines = ["🌱 **Sustainability Metrics**:\n"]
            for log in logs:
                lines.append(f"- **{log['metric'].replace('_', ' ').title()}**: {log['value']} {log['unit']}")
            return "\n".join(lines)
        return "StadiumAI is committed to sustainability! The venue uses:\n\n- ☀️ **Solar panels** generating clean energy\n- ♻️ **Waste recycling** with 65% diversion rate\n- 💧 **Water conservation** systems\n- 🌿 **Carbon offset** programs\n\nAsk me for specific sustainability metrics!"

    @staticmethod
    def capacity(stadium: dict = None) -> str:
        if stadium:
            return f"**{stadium['name']}** can hold **{stadium['capacity']:,}** spectators. It's one of the premier venues for the FIFA World Cup 2026."
        return "The stadium has a capacity of **82,500** seats for the World Cup. This includes general seating, VIP boxes, and accessible areas."

    @staticmethod
    def unknown():
        return "I'm not sure I understand. I specialize in stadium information — seats, navigation, food, parking, matches, and crowd conditions.\n\nTry asking me something like:\n- \"Where is my seat?\"\n- \"When is the next match?\"\n- \"Where can I park?\"\n- \"How crowded is Gate A?\""


class SmartChatEngine:
    def __init__(self, db=None):
        self.context = ConversationContext()
        self.classifier = IntentClassifier(self.context)
        self.retriever = DataRetriever()
        self.generator = ResponseGenerator()
        self._handlers = {
            IntentType.GREETING: self._handle_greeting,
            IntentType.GOODBYE: self._handle_goodbye,
            IntentType.CAPABILITIES: self._handle_capabilities,
            IntentType.SEAT: self._handle_seat,
            IntentType.NAVIGATION: self._handle_navigation,
            IntentType.FOOD: self._handle_food,
            IntentType.RESTROOM: self._handle_restroom,
            IntentType.PARKING: self._handle_parking,
            IntentType.TRANSPORT: self._handle_transport,
            IntentType.CROWD: self._handle_crowd,
            IntentType.EMERGENCY: self._handle_emergency,
            IntentType.VOLUNTEER: self._handle_volunteer,
            IntentType.SUSTAINABILITY: self._handle_sustainability,
            IntentType.CAPACITY: self._handle_capacity,
            IntentType.STADIUM_INFO: self._handle_stadium_info,
        }

    def _get_sid(self, entities: dict) -> Optional[str]:
        return get_stadium_id(entities.get("stadium"))

    def _handle_greeting(self, entities: dict, primary: IntentType) -> str:
        return self.generator.greeting() if self.context.turn_count <= 1 else ""

    def _handle_goodbye(self, entities: dict, primary: IntentType) -> str:
        return self.generator.goodbye()

    def _handle_capabilities(self, entities: dict, primary: IntentType) -> str:
        return self.generator.capabilities()

    def _handle_seat(self, entities: dict, primary: IntentType) -> str:
        return self.generator.seat_guidance()

    def _handle_navigation(self, entities: dict, primary: IntentType) -> str:
        routes = self.retriever.get_routes(self._get_sid(entities))
        return self.generator.navigation(entities.get("zone", ""), routes)

    def _handle_food(self, entities: dict, primary: IntentType) -> str:
        return self.generator.food()

    def _handle_restroom(self, entities: dict, primary: IntentType) -> str:
        return self.generator.restroom()

    def _handle_parking(self, entities: dict, primary: IntentType) -> str:
        return self.generator.parking(self.retriever.get_parking_lots(self._get_sid(entities)))

    def _handle_transport(self, entities: dict, primary: IntentType) -> str:
        return self.generator.transport(self.retriever.get_transport_options(self._get_sid(entities)))

    def _handle_crowd(self, entities: dict, primary: IntentType) -> str:
        return self.generator.crowd(self.retriever.get_crowd_data(self._get_sid(entities)))

    def _handle_emergency(self, entities: dict, primary: IntentType) -> str:
        return self.generator.emergency()

    def _handle_volunteer(self, entities: dict, primary: IntentType) -> str:
        return self.generator.volunteer()

    def _handle_sustainability(self, entities: dict, primary: IntentType) -> str:
        return self.generator.sustainability(self.retriever.get_sustainability_logs(self._get_sid(entities)))

    def _handle_capacity(self, entities: dict, primary: IntentType) -> str:
        stadium = self.retriever.get_stadium_by_name(entities.get("stadium")) if entities.get("stadium") else self.retriever.get_first_stadium()
        return self.generator.capacity(stadium)

    def _handle_stadium_info(self, entities: dict, primary: IntentType) -> str:
        stadium = self.retriever.get_stadium_by_name(entities.get("stadium")) if entities.get("stadium") else self.retriever.get_first_stadium()
        return self.generator.stadium_info(stadium)

    def _handle_match(self, entities: dict, primary: IntentType) -> str:
        teams = entities.get("teams", [])
        matches = self.retriever.get_matches_by_team(teams[0]) if teams else self.retriever.get_matches()
        if primary == IntentType.MATCH_SCHEDULE:
            return self.generator.match_schedule(matches)
        return self.generator.match_details(matches)

    async def get_response(self, message: str, history: list[dict]) -> str:
        entities = EntityExtractor.extract(message)
        intents = self.classifier.classify(message)
        self.context.update(intents, entities)

        primary = intents[0]
        if primary in (IntentType.MATCH_SCHEDULE, IntentType.MATCH_INFO):
            return self._handle_match(entities, primary)

        handler = self._handlers.get(primary)
        if handler:
            return handler(entities, primary)
        return self.generator.unknown()
