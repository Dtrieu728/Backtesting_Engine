import { useState } from 'react';
import './App.css';
import Backtest from './pages/Backtest';
import History from './pages/History';

function App() {
  const [page, setPage] = useState('backtest');

  return (
    <div className="App">
      <nav className="app-nav">
        <button
          className={`app-nav-btn ${page === 'backtest' ? 'active' : ''}`}
          onClick={() => setPage('backtest')}
        >
          Backtest
        </button>
        <button
          className={`app-nav-btn ${page === 'history' ? 'active' : ''}`}
          onClick={() => setPage('history')}
        >
          History
        </button>
      </nav>
      {page === 'backtest' ? <Backtest /> : <History />}
    </div>
  );
}

export default App;