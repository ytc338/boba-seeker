import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <Link to="/" className="logo">
            <span className="logo-icon">🧋</span>
            <span className="logo-text">Boba Seeker</span>
          </Link>
          <nav className="nav">
            <Link to="/" className="nav-link">Explore</Link>
          </nav>
        </header>

        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
