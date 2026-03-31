# Boba Seeker 🧋

**Find your next boba tea shop — across Taiwan, Singapore, and the US.**

[![Tests](https://github.com/ytc338/boba-seeker/actions/workflows/tests.yml/badge.svg)](https://github.com/ytc338/boba-seeker/actions/workflows/tests.yml)

🔗 **[Live Demo](https://boba-seeker-frontend.onrender.com/)**

---

## About

Boba Seeker is a full-stack web application for discovering boba tea shops across three countries. It combines an interactive map interface with smart brand matching, personalized drink recommendations, and a playful "Feeling Lucky" roulette — all backed by real-world data from the Google Places API.

### Coverage

| Region | Areas |
|--------|-------|
| 🇹🇼 Taiwan | Nationwide |
| 🇸🇬 Singapore | Nationwide |
| 🇺🇸 United States | CA (LA, Bay Area, San Diego, OC) · NY (Manhattan, Queens, Brooklyn) · WA (Seattle, Bellevue) · TX (Houston) · IL (Chicago) · HI (Honolulu) |

---

## Features

- **Interactive Map** — Mapbox GL with geolocation, custom markers, and "Search This Area" lazy loading
- **Smart Brand Matching** — RapidFuzz fuzzy matching across 90+ brand aliases (handles Chinese/English variants like 50嵐 → Wushiland Boba)
- **Multi-Region Filtering** — Filter by country and brand; brands populate dynamically based on regional presence
- **Feeling Lucky Roulette** — Random shop picker with spinning animation and shareable PNG card generation (canvas-based)
- **Drink Recommendations** — Curated picks for 30+ brands, categorized by "First Timer" and "For Regulars" tiers
- **Shop Details** — Ratings, hours, photos, phone, and one-tap Google Maps directions
- **Favorites** — Client-side persistence via localStorage
- **Distance Sorting** — Real-time Haversine distance calculation with km/m display
- **Contact Form** — Backend email integration via Gmail SMTP with HTML sanitization
- **PWA Support** — Installable on mobile with service worker for offline access

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 19, TypeScript, Vite, Mapbox GL JS, React Router, Axios |
| **Backend** | FastAPI, SQLAlchemy 2.0, PostgreSQL, Pydantic, RapidFuzz, httpx |
| **Testing** | pytest (67 tests), Vitest (54 tests), Testing Library, GitHub Actions CI |
| **DevOps** | Docker, Docker Compose, Nginx, Render, Neon PostgreSQL |

---

## Architecture

```
boba-seeker/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── app/
│   │   ├── api/                 # Route handlers (shops, brands, feedback)
│   │   ├── services/            # Google Places API, brand fuzzy matcher
│   │   ├── models.py            # SQLAlchemy models (Shop, Brand)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   └── database.py          # DB engine and session management
│   └── tests/                   # pytest suite
├── frontend/
│   ├── src/
│   │   ├── pages/               # HomePage, ShopPage, ContactPage
│   │   ├── components/          # Map, FilterPanel, BottomSheet, RouletteOverlay
│   │   ├── hooks/               # useFavorites (localStorage)
│   │   ├── utils/               # Haversine distance, share card canvas renderer
│   │   └── services/            # Axios API client
│   └── nginx.conf               # Production static serving
├── docker-compose.yml           # Dev and production orchestration
├── docker-compose.test.yml      # Test runner compose
├── render.yaml                  # Render deployment blueprint
└── .github/workflows/tests.yml  # CI pipeline
```

The backend serves a RESTful API with PostgreSQL in production (SQLite for local dev). The frontend is a React SPA with code splitting (lazy-loaded routes) and Suspense boundaries. In production, Nginx serves the built frontend and proxies API requests.

---

## Getting Started

### Docker (Recommended)

```bash
# Start all services with hot reload
docker-compose --profile dev up backend frontend-dev

# Or production mode
docker-compose up --build
```

- Frontend: http://localhost:5173 (dev) or http://localhost:3002 (prod)
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

### Manual Setup

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` in the project root:

```env
# Required for map display
VITE_MAPBOX_TOKEN=your_mapbox_token

# Optional — for importing shop data from Google
GOOGLE_PLACES_API_KEY=your_key

# Optional — for contact form emails
SMTP_USER=your_gmail
SMTP_PASSWORD=your_app_password
```

---

## Testing

121 tests across backend and frontend, running on every push and PR via GitHub Actions.

### Docker

```bash
# Backend (pytest)
docker compose -f docker-compose.test.yml run --rm backend-test

# Frontend (Vitest)
docker compose -f docker-compose.test.yml run --rm frontend-test
```

### Local

```bash
# Backend
cd backend && source venv/bin/activate
pytest -v --cov=app

# Frontend
cd frontend
npm test
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/shops` | List shops (paginated, filterable by country/city/brand) |
| `GET` | `/api/shops/search?q=` | Search by name or address |
| `GET` | `/api/shops/nearby?lat=&lng=&radius_km=` | Find shops within radius |
| `GET` | `/api/shops/{id}` | Shop detail |
| `GET` | `/api/brands` | List brands (optionally filtered by country) |
| `GET` | `/api/brands/{id}` | Brand detail |
| `POST` | `/api/feedback` | Submit contact form |
| `GET` | `/health` | Health check |

Full interactive docs available at `/docs` when the backend is running.

---

## Deployment

Deployed on **Render** (backend web service + frontend static site) with **Neon** PostgreSQL. See `render.yaml` for the full blueprint.

```bash
# Backend: Python 3.12, uvicorn
# Frontend: Static site (Vite build → Nginx)
# Database: Neon PostgreSQL (free tier)
```

---

Built by [@ytc338](https://github.com/ytc338)
