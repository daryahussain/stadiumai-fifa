import re
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from app.models.stadium import Stadium
from app.models.match import Match
from app.models.crowd_data import CrowdData
from app.models.route import Route
from app.models.transport_option import TransportOption, ParkingLot
from app.models.sustainability_log import SustainabilityLog
from app.models.volunteer import Volunteer


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
    topics: deque[tuple[IntentType, str]] = field(default_factory=lambda: deque(maxlen=5))
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
        if self.topics:
            return self.topics[-1][0]
        return None

    def last_topic_detail(self) -> str:
        if self.topics:
            return self.topics[-1][1]
        return ""


_INTENT_PATTERNS: list[tuple[IntentType, list[str]]] = [
    (IntentType.GREETING, [
        r"\b(hello|hi|hey|good morning|good afternoon|good evening|howdy|sup|yo)\b",
    ]),
    (IntentType.GOODBYE, [
        r"\b(thanks|thank you|goodbye|bye|see you|cheers|appreciate it|that's all)\b",
    ]),
    (IntentType.SEAT, [
        r"\b(seat|section|row|where (am i|is my)|my seat|gate\s*[a-d]|sitting)\b",
    ]),
    (IntentType.NAVIGATION, [
        r"\b(how (do i|to) get|direction|where is|nearest|way to|navigate|route|map|guide me|walk|stair|elevator|escalator|entrance|exit|how do i)\b",
    ]),
    (IntentType.FOOD, [
        r"\b(food|eat|hungry|restaurant|burger|pizza|snack|drink|water|coffee|concession|dining|menu|meal|lunch|dinner|breakfast)\b",
    ]),
    (IntentType.RESTROOM, [
        r"\b(restroom|bathroom|toilet|washroom|loo|lavatory)\b",
    ]),
    (IntentType.PARKING, [
        r"\b(park|parking|lot|garage|valet|car|drive)\b",
    ]),
    (IntentType.TRANSPORT, [
        r"\b(transport|bus|metro|train|shuttle|taxi|uber|lyft|subway|station|stop|ride|drop off|pick up|commute|get (to|there|here|from))\b",
    ]),
    (IntentType.MATCH_SCHEDULE, [
        r"\b(schedule|match|game|fixture|play|when (is|does|are)|what time|today[']?s match|upcoming|next game|today[']?s game)\b",
    ]),
    (IntentType.MATCH_INFO, [
        r"\b(score|who (is|are) playing|teams|vs|versus|result|won|lost|winner|loser|half time|full time|kickoff)\b",
    ]),
    (IntentType.CROWD, [
        r"\b(crowd|crowded|busy|density|wait (time|line)|queue|traffic|congestion|how full|capacity now|occupancy|packed|empty|people|foot traffic)\b",
    ]),
    (IntentType.CAPACITY, [
        r"\b(capacity|how many people|size|big|large|holds|seats|accommodate)\b",
    ]),
    (IntentType.STADIUM_INFO, [
        r"\b(stadium|venue|arena|ground|field|about|tell me about)\b",
    ]),
    (IntentType.EMERGENCY, [
        r"\b(emergency|help|lost|injured|hurt|accident|medical|doctor|nurse|ambulance|police|security|danger|fire|first aid)\b",
    ]),
    (IntentType.VOLUNTEER, [
        r"\b(volunteer|staff|worker|marshal|steward|help desk|information|guest service)\b",
    ]),
    (IntentType.SUSTAINABILITY, [
        r"\b(sustainability|green|eco|environment|solar|recycle|waste|energy|carbon|water|environmental)\b",
    ]),
]

_FOLLOWUP_PATTERNS = [
    r"^(what about|and|also|how about|what's|tell me more|more|elaborate)",
    r"^(that|there|it|they|them)",
    r"^(where|how|when|why|who|which)\s+(is|are|can|do|does|will)",
]


class EntityExtractor:
    STADIUM_NAMES = {
        "metlife": "MetLife Stadium",
        "at&t": "AT&T Stadium",
        "sofi": "SoFi Stadium",
        "mercedes-benz": "Mercedes-Benz Stadium",
        "mercedes": "Mercedes-Benz Stadium",
        "nrg": "NRG Stadium",
        "lincoln financial": "Lincoln Financial Field",
        "lumen": "Lumen Field",
        "levi": "Levi's Stadium",
        "levi's": "Levi's Stadium",
        "gillette": "Gillette Stadium",
        "hard rock": "Hard Rock Stadium",
        "estadio azteca": "Estadio Azteca",
        "azteca": "Estadio Azteca",
    }

    TEAM_NAMES = [
        "usa", "united states", "mexico", "canada", "brazil", "argentina",
        "germany", "france", "england", "spain", "portugal", "netherlands",
        "italy", "belgium", "croatia", "uruguay", "japan", "south korea",
        "australia", "senegal", "ghana", "nigeria", "cameroon", "morocco",
        "saudi arabia", "iran", "qatar", "switzerland", "poland", "denmark",
    ]

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
        IntentType.EMERGENCY: 100,
        IntentType.GOODBYE: 90,
        IntentType.GREETING: 10,
    }

    def __init__(self, context: ConversationContext):
        self.context = context

    def classify(self, message: str) -> list[IntentType]:
        msg_lower = message.lower().strip()

        matched = []
        seen = set()

        if self._is_followup(msg_lower):
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
        if self.context.turn_count == 0:
            return False
        msg = msg.strip().rstrip("?.")
        if not msg:
            return False
        for pat in _FOLLOWUP_PATTERNS:
            if re.match(pat, msg, re.IGNORECASE):
                return True
        return False


class DataRetriever:
    def __init__(self, db: Session):
        self.db = db

    def get_stadiums(self) -> list[Stadium]:
        return self.db.query(Stadium).order_by(Stadium.name).all()

    def get_stadium_by_name(self, name: str) -> Optional[Stadium]:
        return self.db.query(Stadium).filter(Stadium.name.ilike(f"%{name}%")).first()

    def get_first_stadium(self) -> Optional[Stadium]:
        return self.db.query(Stadium).order_by(Stadium.name).first()

    def get_matches(self, limit: int = 5) -> list[Match]:
        from sqlalchemy import asc
        return self.db.query(Match).order_by(asc(Match.match_date)).limit(limit).all()

    def get_matches_by_team(self, team: str, limit: int = 3) -> list[Match]:
        return self.db.query(Match).filter(
            (Match.home_team.ilike(f"%{team}%")) | (Match.away_team.ilike(f"%{team}%"))
        ).limit(limit).all()

    def get_crowd_data(self, stadium_id, limit: int = 20) -> list[CrowdData]:
        from sqlalchemy import desc
        latest = self.db.query(CrowdData.timestamp).filter(
            CrowdData.stadium_id == stadium_id
        ).order_by(desc(CrowdData.timestamp)).first()
        if not latest:
            return []
        return self.db.query(CrowdData).filter(
            CrowdData.stadium_id == stadium_id,
            CrowdData.timestamp == latest[0],
        ).limit(limit).all()

    def get_routes(self, stadium_id, limit: int = 10) -> list[Route]:
        return self.db.query(Route).filter(
            Route.stadium_id == stadium_id
        ).limit(limit).all()

    def get_transport_options(self, stadium_id) -> list[TransportOption]:
        return self.db.query(TransportOption).filter(
            TransportOption.stadium_id == stadium_id
        ).all()

    def get_parking_lots(self, stadium_id) -> list[ParkingLot]:
        return self.db.query(ParkingLot).filter(
            ParkingLot.stadium_id == stadium_id
        ).all()

    def get_sustainability_logs(self, stadium_id) -> list[SustainabilityLog]:
        from sqlalchemy import desc
        logs = []
        for row in self.db.query(SustainabilityLog.metric_type).filter(
            SustainabilityLog.stadium_id == stadium_id
        ).distinct().all():
            metric = row[0]
            log = self.db.query(SustainabilityLog).filter(
                SustainabilityLog.stadium_id == stadium_id,
                SustainabilityLog.metric_type == metric,
            ).order_by(desc(SustainabilityLog.timestamp)).first()
            if log:
                logs.append(log)
        return logs

    def get_volunteers(self) -> list[Volunteer]:
        return self.db.query(Volunteer).filter(Volunteer.is_active == True).all()


class ResponseGenerator:
    @staticmethod
    def greeting():
        return (
            "Hello! I'm your **StadiumAI** assistant for the FIFA World Cup 2026. "
            "I can help you with:\n\n"
            "- 🏟️ **Stadium info** — capacity, location, details\n"
            "- 🎫 **Match schedules** — teams, dates, tickets\n"
            "- 🪑 **Seat guidance** — where your seat is\n"
            "- 🚶 **Navigation** — directions around the venue\n"
            "- 🍕 **Food & restrooms** — nearest options\n"
            "- 🚗 **Parking & transport** — lots, shuttles, metro\n"
            "- 📊 **Crowd conditions** — density, wait times\n"
            "- 🆘 **Emergency** — first aid, lost & found\n\n"
            "What would you like to know?"
        )

    @staticmethod
    def goodbye():
        return (
            "You're welcome! Enjoy the match! 🎉\n\n"
            "If you need anything else, I'm just a message away."
        )

    @staticmethod
    def capabilities():
        return (
            "Here's what I can help you with:\n\n"
            "- **Seats & Navigation** — \"Where is my seat?\"\n"
            "- **Food** — \"Where can I eat?\"\n"
            "- **Restrooms** — \"Where's the nearest restroom?\"\n"
            "- **Parking** — \"Where should I park?\"\n"
            "- **Transport** — \"How do I get to the stadium?\"\n"
            "- **Schedule** — \"When is the next match?\"\n"
            "- **Crowd** — \"How crowded is it?\"\n"
            "- **Emergency** — \"I need help\"\n\n"
            "What would you like to know?"
        )

    @staticmethod
    def stadium_info(stadium: Stadium) -> str:
        return (
            f"**{stadium.name}** in {stadium.city} has a capacity of "
            f"**{stadium.capacity:,}** seats. "
            f"It's one of the FIFA World Cup 2026 host venues."
        )

    @staticmethod
    def match_schedule(matches: list[Match]) -> str:
        if not matches:
            return "There are no matches scheduled at this time."
        lines = ["Here are the upcoming matches:\n"]
        for m in matches:
            lines.append(f"- **{m.home_team}** vs **{m.away_team}**")
        return "\n".join(lines)

    @staticmethod
    def match_details(matches: list[Match]) -> str:
        if not matches:
            return "I couldn't find information about that match."
        lines = []
        for m in matches:
            stadium = "at the stadium"
            lines.append(
                f"**{m.home_team}** vs **{m.away_team}** — "
                f"{m.sold_tickets:,} / {m.total_tickets:,} tickets sold, "
                f"status: **{m.status}**"
            )
        return "\n".join(lines)

    @staticmethod
    def seat_guidance(_stadium=None):
        return (
            "Your seat is located in **Section 214, Row 12**. "
            "Take the main concourse to **Gate C**, then follow signs for **Section 200**. "
            "There's an elevator available for wheelchair access.\n\n"
            "Would you like directions from a specific entrance?"
        )

    @staticmethod
    def navigation(zone: str = "", routes: list[Route] = None) -> str:
        if routes:
            lines = ["Here are some available routes:\n"]
            for r in routes:
                wc = "♿ Wheelchair accessible" if r.wheelchair_accessible == "yes" else ""
                lines.append(f"- **{r.start_location}** → **{r.end_location}** ({r.distance_km} km) {wc}".strip())
            return "\n".join(lines)
        return (
            "The stadium concourse connects all sections. "
            "Use the signs overhead to find **Gates A-D**, **Sections 100-300**, "
            "the **Food Court**, and **Restrooms**.\n\n"
            "Need directions between two specific points?"
        )

    @staticmethod
    def food() -> str:
        return (
            "There are several food options available:\n\n"
            "- **Fan Favorites** (Burgers & Fries) — Concourse Level\n"
            "- **World Bites** (International Cuisine) — Level 2\n"
            "- **Refresh Zone** (Drinks & Snacks) — Every concourse\n"
            "- **Kickoff Coffee** — Near Gate A\n\n"
            "What are you in the mood for?"
        )

    @staticmethod
    def restroom() -> str:
        return (
            "The nearest restrooms are **50m west** of your section, "
            "past the Fan Favorites food stand. "
            "Family restrooms are available on **Level 1**, "
            "and accessible restrooms are on every concourse."
        )

    @staticmethod
    def parking(lots: list[ParkingLot] = None) -> str:
        if lots:
            lines = ["Here are the available parking options:\n"]
            for lot in lots:
                status_icon = "🟢" if lot.status == "available" else "🟡" if lot.status == "filling" else "🔴"
                lines.append(
                    f"{status_icon} **{lot.lot}** — "
                    f"{lot.available_spots}/{lot.total_spots} spots, "
                    f"{lot.distance_m}m from gate"
                )
            return "\n".join(lines)
        return (
            "Parking is available at **Lot A** (East Entrance) and **Lot B** (West Entrance). "
            "Lot A is currently at 80% capacity. "
            "I'd recommend **Lot B** — it's less crowded and a short 5-minute walk to Gate 3."
        )

    @staticmethod
    def transport(options: list[TransportOption] = None) -> str:
        if options:
            lines = ["Here are the available transport options:\n"]
            for opt in options:
                status_icon = "🟢" if opt.status == "running" else "🟡" if opt.status == "delayed" else "🔴"
                lines.append(
                    f"{status_icon} **{opt.name}** ({opt.type}) — "
                    f"{opt.status}, next arrival {opt.next_arrival}"
                )
            return "\n".join(lines)
        return (
            "The **Stadium Express Metro** runs every 5 minutes from Downtown. "
            "Get off at **World Cup Station**. "
            "Shuttle buses are also operating from the City Center parking lots."
        )

    @staticmethod
    def crowd(data: list[CrowdData] = None) -> str:
        if data:
            total_density = sum(d.density for d in data) / len(data)
            avg_wait = sum(d.wait_time or 0 for d in data) / len(data)
            busy_zones = sorted(data, key=lambda x: x.density, reverse=True)[:3]

            level = "🟢 Low" if total_density < 0.4 else "🟡 Moderate" if total_density < 0.7 else "🔴 High"

            lines = [
                f"Crowd level: **{level}** (avg density: {total_density:.0%})\n",
                f"Average wait time: **{avg_wait:.0f} min**\n",
                "Busiest areas:",
            ]
            for z in busy_zones:
                lines.append(f"- **{z.zone}**: density {z.density:.0%}")
            return "\n".join(lines)
        return (
            "Crowd conditions are currently **moderate** across the stadium. "
            "**Gate A** is the busiest area. I'd recommend using **Gate C** for quicker entry."
        )

    @staticmethod
    def emergency():
        return (
            "🆘 **Emergency Assistance**\n\n"
            "If this is a **medical emergency**, please contact the nearest staff member "
            "or call **+1-800-FIFA-HELP** immediately.\n\n"
            "- **Medical stations** are located on every concourse level\n"
            "- **Lost child** — report to Guest Services near Gate A\n"
            "- **Security concerns** — notify any staff member or call the hotline\n\n"
            "Stay calm and follow the instructions of stadium personnel."
        )

    @staticmethod
    def volunteer():
        return (
            "Volunteers and staff are available throughout the stadium. "
            "Look for staff in **yellow vests** at:\n\n"
            "- **Gate A, B, C, D** — Entry assistance\n"
            "- **Fan Zone** — Information & activities\n"
            "- **Section 100** — Seating help\n"
            "- **Parking** — Traffic direction\n\n"
            "Guest Services desks are located near Gates A and C."
        )

    @staticmethod
    def sustainability(logs: list[SustainabilityLog] = None) -> str:
        if logs:
            lines = ["🌱 **Sustainability Metrics**:\n"]
            for log in logs:
                lines.append(f"- **{log.metric_type.replace('_', ' ').title()}**: {log.value} {log.unit}")
            return "\n".join(lines)
        return (
            "StadiumAI is committed to sustainability! The venue uses:\n\n"
            "- ☀️ **Solar panels** generating clean energy\n"
            "- ♻️ **Waste recycling** with 65% diversion rate\n"
            "- 💧 **Water conservation** systems\n"
            "- 🌿 **Carbon offset** programs\n\n"
            "Ask me for specific sustainability metrics!"
        )

    @staticmethod
    def capacity(stadium: Stadium = None) -> str:
        if stadium:
            return (
                f"**{stadium.name}** can hold **{stadium.capacity:,}** spectators. "
                f"It's one of the premier venues for the FIFA World Cup 2026."
            )
        return (
            "The stadium has a capacity of **82,500** seats for the World Cup. "
            "This includes general seating, VIP boxes, and accessible areas."
        )

    @staticmethod
    def unknown():
        return (
            "I'm not sure I understand. I specialize in stadium information — "
            "seats, navigation, food, parking, matches, and crowd conditions.\n\n"
            "Try asking me something like:\n"
            "- \"Where is my seat?\"\n"
            "- \"When is the next match?\"\n"
            "- \"Where can I park?\"\n"
            "- \"How crowded is Gate A?\""
        )


def get_stadium_id(db: Session, stadium_name: str = None) -> Optional[str]:
    if stadium_name:
        stadium = db.query(Stadium).filter(Stadium.name.ilike(f"%{stadium_name}%")).first()
        if stadium:
            return str(stadium.id)
    stadium = db.query(Stadium).order_by(Stadium.name).first()
    return str(stadium.id) if stadium else None


class SmartChatEngine:
    def __init__(self, db: Session):
        self.db = db
        self.context = ConversationContext()
        self.classifier = IntentClassifier(self.context)
        self.retriever = DataRetriever(db)
        self.generator = ResponseGenerator()

    async def get_response(self, message: str, history: list[dict]) -> str:
        entities = EntityExtractor.extract(message)
        intents = self.classifier.classify(message)

        self.context.update(intents, entities)

        primary = intents[0]

        if primary == IntentType.GREETING and self.context.turn_count <= 1:
            return self.generator.greeting()

        if primary == IntentType.GOODBYE:
            return self.generator.goodbye()

        if primary == IntentType.CAPABILITIES:
            return self.generator.capabilities()

        if primary == IntentType.SEAT:
            stadium_name = entities.get("stadium")
            return self.generator.seat_guidance()

        if primary == IntentType.NAVIGATION:
            stadium_name = entities.get("stadium")
            sid = get_stadium_id(self.db, stadium_name)
            routes = self.retriever.get_routes(sid) if sid else []
            zone = entities.get("zone", "")
            return self.generator.navigation(zone, routes)

        if primary == IntentType.FOOD:
            return self.generator.food()

        if primary == IntentType.RESTROOM:
            return self.generator.restroom()

        if primary == IntentType.PARKING:
            stadium_name = entities.get("stadium")
            sid = get_stadium_id(self.db, stadium_name)
            lots = self.retriever.get_parking_lots(sid) if sid else []
            return self.generator.parking(lots)

        if primary == IntentType.TRANSPORT:
            stadium_name = entities.get("stadium")
            sid = get_stadium_id(self.db, stadium_name)
            options = self.retriever.get_transport_options(sid) if sid else []
            return self.generator.transport(options)

        if primary == IntentType.MATCH_SCHEDULE or primary == IntentType.MATCH_INFO:
            teams = entities.get("teams", [])
            if teams:
                matches = self.retriever.get_matches_by_team(teams[0])
            else:
                matches = self.retriever.get_matches()
            if primary == IntentType.MATCH_SCHEDULE:
                return self.generator.match_schedule(matches)
            return self.generator.match_details(matches)

        if primary == IntentType.CROWD:
            stadium_name = entities.get("stadium")
            sid = get_stadium_id(self.db, stadium_name)
            crowd_data = self.retriever.get_crowd_data(sid) if sid else []
            return self.generator.crowd(crowd_data)

        if primary == IntentType.EMERGENCY:
            return self.generator.emergency()

        if primary == IntentType.VOLUNTEER:
            return self.generator.volunteer()

        if primary == IntentType.SUSTAINABILITY:
            stadium_name = entities.get("stadium")
            sid = get_stadium_id(self.db, stadium_name)
            logs = self.retriever.get_sustainability_logs(sid) if sid else []
            return self.generator.sustainability(logs)

        if primary == IntentType.STADIUM_INFO or primary == IntentType.CAPACITY:
            stadium_name = entities.get("stadium")
            stadium = self.retriever.get_stadium_by_name(stadium_name) if stadium_name else self.retriever.get_first_stadium()
            if primary == IntentType.CAPACITY and stadium:
                return self.generator.capacity(stadium)
            if stadium:
                return self.generator.stadium_info(stadium)
            if primary == IntentType.CAPACITY:
                return self.generator.capacity()
            return self.generator.stadium_info(self.retriever.get_first_stadium())

        return self.generator.unknown()
