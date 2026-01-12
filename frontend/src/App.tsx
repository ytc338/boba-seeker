import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
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
          </nav>
        </header>

        <main role="main">
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
