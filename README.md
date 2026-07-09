# StadiumAI

**GenAI-Powered Smart Stadium Assistant for FIFA World Cup 2026**

Full-stack web application that uses Generative AI to improve stadium operations and enhance the experience for fans, organizers, volunteers, and security personnel.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts |
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic |
| Database | PostgreSQL (production) / SQLite (local dev) |
| AI | OpenAI GPT-4o-mini (optional), built-in rule-based fallback |
| Auth | JWT (python-jose) + bcrypt |
| State | Zustand 5 |

## Prerequisites

- Python 3.13+
- Node.js 18+
- npm

## Project Structure

```
fifa_opencode/
├── backend/
│   ├── alembic/          # Database migrations
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   └── services/     # Business logic (LLM, etc.)
│   ├── tests/            # Pytest test suite
│   ├── seed.py           # Database seed script
│   ├── requirements.txt
│   └── .env
├── frontend/
│   └── src/
│       ├── app/          # Next.js App Router pages
│       ├── components/   # React components
│       ├── lib/          # API client modules
│       └── store/        # Zustand state stores
└── README.md
```

## Setup & Run

### 1. Backend

```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (or copy from .env.example)
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux
```

Edit `.env` and set your `DATABASE_URL`. For local development with SQLite (default):

```
DATABASE_URL=sqlite:///./stadiumai.db
```

For PostgreSQL:

```
DATABASE_URL=postgresql://user:password@localhost:5432/stadiumai
```

#### Run database migrations

```bash
alembic upgrade head
```

#### Seed the database

```bash
python seed.py
```

#### Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open `http://localhost:3000` in your browser.

### 3. Build for production

```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm start
```

## Docker Deployment

### Prerequisites

- Docker & Docker Compose

### Deploy with Docker Compose

```bash
# 1. Clone the repo and cd into it

# 2. Create .env from example
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY to a secure random value

# 3. Build and start all services
docker compose up --build -d

# 4. Run database migrations
docker compose run --rm migrations

# 5. (Optional) Seed the database
docker compose run --rm backend python seed.py
```

Services:

| Service   | URL                           |
|-----------|-------------------------------|
| Frontend  | http://localhost:3000         |
| Backend   | http://localhost:8000         |
| API Docs  | http://localhost:8000/docs    |

### Configuration

Copy `.env.example` to `.env` and adjust:

| Variable             | Description                              |
|----------------------|------------------------------------------|
| `DB_PASSWORD`        | PostgreSQL password (default: stadiumai_pass) |
| `SECRET_KEY`         | JWT signing secret (**required**)        |
| `OPENAI_API_KEY`     | OpenAI API key (optional, for AI features) |
| `PUBLIC_API_URL`     | Public API URL for browser requests      |
| `PUBLIC_WS_URL`      | Public WebSocket URL for browser requests |
| `CORS_ORIGINS`       | JSON array of allowed CORS origins       |

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login | No |
| GET | `/api/v1/auth/me` | Current user info | Yes |
| POST | `/api/v1/chat/message` | Send chat message | No |
| GET | `/api/v1/chat/history/{session_id}` | Get chat history | No |
| GET | `/api/v1/crowd/` | Live crowd data | No |
| GET | `/api/v1/dashboard/` | Operational dashboard | No |
| POST | `/api/v1/navigation/route` | Get route between points | No |
| GET | `/api/v1/navigation/data` | Stadium map data | No |
| GET | `/api/v1/notifications/` | User notifications | No |
| POST | `/api/v1/notifications/{id}/read` | Mark notification read | No |
| GET | `/api/v1/reports/incidents` | List incidents | No |
| POST | `/api/v1/reports/incidents` | Report an incident | No |
| GET | `/api/v1/sustainability/` | Sustainability metrics | No |
| GET | `/api/v1/transport/` | Transport & parking info | No |
| POST | `/api/v1/translation/translate` | Translate text | No |
| GET | `/health` | Health check | No |

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Default Credentials (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@stadiumai.com | admin123 |
| Fan | fan@example.com | fan123 |
| Staff | staff@stadiumai.com | staff123 |

## AI Features

The chatbot and translation endpoints try OpenAI first. If `OPENAI_API_KEY` is not set in `.env`, they fall back to built-in rule-based responses covering:
- Stadium navigation & seating
- Food & restroom locations
- Match schedules
- Transport & parking
- Emergency assistance

Supported translation languages: English, Spanish, French, Arabic, Hindi.
