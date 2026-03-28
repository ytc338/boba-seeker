# Boba Seeker - Product Roadmap

> **Vision**: The boba-literate map — not just where to find it, but what to order when you get there.

## ✅ Completed Features
- [x] Map display with Mapbox GL JS
- [x] Shop markers with custom boba icon
- [x] "Search This Area" lazy loading
- [x] Multi-select brand filtering
- [x] User geolocation with fallback
- [x] Backend API (FastAPI + PostgreSQL)
- [x] Docker containerization
- [x] Seed data for initial shops
- [x] Real shop data import via Google Places API
- [x] Singapore location data
- [x] US location data (LA, SF, NYC, Seattle, Houston, Chicago, Honolulu)
- [x] Roulette / "Feeling Lucky" feature
- [x] Contact / feedback form (Gmail SMTP)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Structured logging
- [x] Pre-commit linting (ruff, eslint)
- [x] **Shop detail panel** — hours, phone, photo, rating, address, brand info
- [x] **Directions button** — "Directions" and "View on Google Maps" buttons
- [x] **Search by name** — search bar in bottom sheet, uses /api/shops/search
- [x] **Drink recommendations** — 30+ brands with "Start here" / "For regulars" tiers
- [x] **Shareable shop URLs** — /shop/:id permalink pages with detail + map
- [x] **Share button** — copy shop link to clipboard
- [x] **Save favorites** — localStorage-based, heart toggle on detail + list
- [x] **PWA support** — manifest, service worker, installable on mobile
- [x] **Singapore country display** — fixed missing SG flag in shop cards

---

## 🌟 Phase 2: Quality of Life

Makes daily use smoother.

- [ ] **Custom icon** — Custom icon for each brand on map markers
- [ ] **Map clustering** — Group markers when zoomed out
- [ ] **Sort options** — Sort by distance, rating
- [ ] **List view toggle** — Alternative to map view
- [ ] **Price range filter** — Filter by $ / $$ / $$$
- [ ] **Open now filter** — Filter to only show currently open shops

---

## 💡 Phase 3: Expand & Share

- [ ] **Language toggle** — English/Chinese interface
- [ ] **Brand profile pages** — /brand/:slug with all locations across countries
- [ ] **City-specific boba guides** — Shareable filtered map views
- [ ] **Roulette share card** — "Boba Seeker picked this for me" image card

---

## 🔧 Phase 4: Scale & Maintain

When you have real users.

- [ ] **User accounts** — Cloud sync favorites
- [ ] **Submit a shop** — User contributions
- [ ] **User-submitted drink recs** — Community recommendations
- [ ] **Admin dashboard** — Manage content
- [ ] **Database migrations** — Alembic setup
- [ ] **Store checker** — Verify shops still open, detect new stores
- [ ] **Rate limiting** — Implement rate limiting for API calls
- [ ] **Cache** — Implement caching for API responses

---

## 🐛 Known Issues
- [ ] Search button sometimes needs two clicks
- [ ] No 404 page for invalid routes

---

## 📝 Technical Debt (Do when it hurts)
- [ ] E2E tests for frontend
- [ ] Better error handling
- [ ] Code splitting (JS bundle is ~2MB)
