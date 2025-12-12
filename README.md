# Boba Seeker

A boba tea shop directory for Taiwan and the US.

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

## Project Structure

```
boba-seeker/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── models.py     # SQLAlchemy models
│   │   └── services/     # External services
│   ├── main.py           # App entry point
│   └── seed_data.py      # Sample data script
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   └── services/     # API client
│   └── nginx.conf        # Production nginx config
└── docker-compose.yml    # Docker orchestration
```
