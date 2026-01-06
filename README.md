# Boba Seeker

A boba tea shop directory for Taiwan, Singapore, and the US.

## 🌍 Service Coverage

- **Taiwan** 🇹🇼: Nationwide coverage
- **Singapore** 🇸🇬: Nationwide coverage
- **United States** 🇺🇸:
  - **California**: Los Angeles (SGV, OC), Bay Area, San Diego
  - **New York**: New York City (Manhattan, Queens, Brooklyn)
  - **Washington**: Seattle, Bellevue
  - **Texas**: Houston
  - **Illinois**: Chicago
  - **Hawaii**: Honolulu

## Quick Start with Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Or for development with hot reload
docker-compose --profile dev up backend frontend-dev
```

- **Frontend**: http://localhost:3002 (production) or http://localhost:5173 (dev)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Seed Sample Data

After containers are running:
```bash
docker-compose exec backend python seed_data.py
```

---

## Local Development (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py       # Seed sample data
uvicorn main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

---

## Environment Variables

Create a `.env` file in the root:
```
# Optional - for Google Places API integration
GOOGLE_PLACES_API_KEY=your_key_here

# Optional - for Mapbox map display
VITE_MAPBOX_TOKEN=your_token_here
```

---

## Testing

![Tests](https://github.com/ytc338/boba-seeker/actions/workflows/tests.yml/badge.svg)

The project includes **121 tests** across backend and frontend.

### Run Tests with Docker
```bash
# Backend tests (67 tests - pytest)
docker compose -f docker-compose.test.yml run --rm backend-test

# Frontend tests (54 tests - Vitest)
docker compose -f docker-compose.test.yml run --rm frontend-test
```

### Run Tests Locally
```bash
# Backend
cd backend
source venv/bin/activate
pip install pytest pytest-asyncio pytest-cov
pytest -v

# Frontend
cd frontend
npm install
npm test
```

### CI/CD
Tests run automatically on GitHub Actions for every push and pull request.

---

## Project Structure

```
boba-seeker/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models.py     # SQLAlchemy models
│   │   └── services/     # External services
│   ├── tests/            # Backend tests (pytest)
│   ├── main.py           # App entry point
│   └── seed_data.py      # Sample data script
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   └── services/     # API client
│   └── nginx.conf        # Production nginx config
├── .github/workflows/    # CI/CD configuration
└── docker-compose.yml    # Docker orchestration
```

