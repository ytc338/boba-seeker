import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import './App.css';

const ShopPage = lazy(() => import('./pages/ShopPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));

function NotFound() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h2>Page not found</h2>
      <p>The page you're looking for doesn't exist.</p>
      <Link to="/">Back to Boba Seeker</Link>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header" role="banner">
          <Link to="/" className="logo">
            <span className="logo-icon" aria-hidden="true">🧋</span>
            <h1 className="logo-text">Boba Seeker</h1>
          </Link>
          <nav className="nav" aria-label="Main navigation">
            <Link to="/?action=explore" className="nav-link">Feeling Lucky</Link>
            <Link to="/contact" className="nav-link">Contact</Link>
          </nav>
        </header>

        <main role="main">
          <Suspense fallback={<div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/shop/:id" element={<ShopPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
