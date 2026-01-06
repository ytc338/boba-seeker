# Boba Seeker - Product Roadmap

> **Philosophy**: Build something actually useful first, polish later.

## ✅ Completed Features
- [x] Map display with Mapbox GL JS
- [x] Shop markers with custom boba icon
- [x] "Search This Area" lazy loading
- [x] Multi-select brand filtering
- [x] User geolocation with fallback to Taipei
- [x] Backend API (FastAPI + SQLite)
- [x] Docker containerization
- [x] Seed data for initial shops
- [x] Singapore location data
- [x] Drink recommendations component

---

## 🔥 Phase 1: Make It Actually Usable

These are blockers for real daily use.

- [x] **Real shop data import** - Import actual Taiwan boba shops via Google Places API
- [ ] **Directions button** - "Open in Google Maps" when viewing a shop
- [ ] **Search by name** - Quick search for shop/brand names
- [ ] **Shop detail panel** - View hours, phone, address, rating on click

---

## 🌟 Phase 2: Quality of Life

Makes daily use smoother.

- [ ] **Custom icon** - Custom icon for each brand
- [ ] **Save favorites** - Bookmark shops locally (no login needed)
- [ ] **Map clustering** - Group markers when zoomed out
- [ ] **Sort options** - Sort by distance, rating
- [ ] **List view toggle** - Alternative to map view
- [ ] **Price range filter** - Filter by $ / $$ / $$$
- [ ] **Open now filter** - Filter to only show currently open shops

---

## 💡 Phase 3: Expand & Share

Once it works well for you, share with others.

- [x] **US location data** - Add major US cities (LA, SF, NYC)
- [ ] **Mobile responsiveness** - Bottom sheet, collapsible sidebar
- [ ] **Share shop** - Copy link to specific shop
- [ ] **Language toggle** - English/Chinese interface
- [ ] **PWA support** - Install as app

---

## 🔧 Phase 4: Scale & Maintain

When you have real users.

- [ ] **User accounts** - Cloud sync favorites
- [ ] **Submit a shop** - User contributions
- [ ] **Admin dashboard** - Manage content
- [ ] **CI/CD pipeline** - Automated deployments
- [ ] **Database migrations** - Alembic setup
- [ ] **Store checker** - Check if a shop is still open and new stores are added
- [ ] **Rate limiting** - Implement rate limiting for API calls
- [ ] **Cache** - Implement caching for API responses

---

## 🐛 Known Issues
- [ ] Search button sometimes needs two clicks
- [ ] No 404 page for invalid routes

---

## 📝 Technical Debt (Do when it hurts)
- [ ] Unit tests for backend API
- [ ] E2E tests for frontend
- [ ] Rate limiting for API
- [ ] Better error handling

---

## 🎯 Next Action

**Start here → Import real shop data via Google Places API**

Without real data, the app is just a tech demo.