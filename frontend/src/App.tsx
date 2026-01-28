import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ContactPage from './pages/ContactPage';
import './App.css';

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
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/contact" element={<ContactPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
