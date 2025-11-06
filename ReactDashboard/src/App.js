import React, { useState } from 'react';
import './App.css';
import ValuationChart from './components/ValuationChart';
import UndervaluedStocks from './components/UndervaluedStocks';
import TickerManagement from './components/TickerManagement';
import './components/ValuationChart.css';
// API base URL - relative path through Apache proxy
// Apache proxies /valuation-api to the FastAPI container
import { API_BASE_URL } from './config';

function App() {
  const [activeTab, setActiveTab] = useState('valuation');
  const [isComputeDisabled, setIsComputeDisabled] = useState(false);
  const [ticker, setTicker] = useState('');
  const [valuations, setValuations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');


  const handleComputeValuations = async () => {
    setIsComputeDisabled(true);
    console.log('Computing valuations...');
    
    try {
      const response = await fetch(`${API_BASE_URL}/compute_valuations_async`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      console.log('Compute response:', data);
      
      if (response.ok) {
        console.log('✓ Valuations triggered successfully');
      } else {
        console.error('✗ Error kicking off valuations:', data);
      }
    } catch (err) {
      console.error('✗ Network error:', err);
    }
    
    // Re-enable button after 10 seconds
    setTimeout(() => {
      setIsComputeDisabled(false);
      console.log('Button re-enabled');
    }, 10000);
  };

  const handleTickerSearch = async (e) => {
    e.preventDefault();
    if (!ticker.trim()) {
      setError('Please enter a ticker symbol');
      return;
    }

    setLoading(true);
    setError('');
    setValuations([]);
    console.log(`Searching for ticker: ${ticker}`);

    try {
      const response = await fetch(`${API_BASE_URL}/ticker/${ticker.toUpperCase()}`);
      const data = await response.json();
      
      if (response.ok) {
        console.log('Ticker data:', data);
        // Sort by created_at descending (most recent first)
        const valuationsArray = data.valuations || [];

        // Sort by created_at descending (most recent first)
        const sorted = [...valuationsArray].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at));

        setValuations(sorted);
      } else {
        setError(data.detail || 'Ticker not found');
        console.error('Error fetching ticker:', data);
      }
    } catch (err) {
      setError('Network error - could not fetch data');
      console.error('Network error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderValuationTab = () => (
    <>
      <h1>Valuation Dashboard</h1>
        
        {/* Compute Valuations Button */}
        <div className="compute-section">
          <button 
            className={`control-button compute-button ${isComputeDisabled ? 'disabled' : ''}`}
            onClick={handleComputeValuations}
            disabled={isComputeDisabled}
          >
            {isComputeDisabled ? 'Computing... (10s)' : 'Compute Valuations'}
          </button>
        </div>

        {/* Ticker Search */}
        <div className="search-section">
          <form onSubmit={handleTickerSearch} className="search-form">
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="Enter ticker (e.g., AAPL)"
              className="search-input"
            />
            <button type="submit" className="control-button search-button">
              Search
            </button>
          </form>
          {error && <p className="error-message">{error}</p>}
        </div>

        {/* Loading State */}
        {loading && <p className="loading">Loading...</p>}

        {/* Valuations Chart */}
        {valuations.length > 1 && (
          <ValuationChart valuations={valuations} />
        )}

        {/* Valuations Table */}
        {valuations.length > 0 && (
          <div className="table-container">
            <h2>{ticker.toUpperCase()} Valuations</h2>
            <table className="valuations-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Valuation Date</th>
                  <th>Market Price</th>
                  <th>Val (Growth)</th>
                  <th>Val (Sales)</th>
                  <th>EPS</th>
                  <th>Avg Target</th>
                  <th>Recommendation</th>
                  <th>Growth Rate</th>
                  <th>Sales Growth</th>
                  <th>Bond Yield</th>
                </tr>
              </thead>
              <tbody>
                {valuations.map((val, idx) => (
                  <tr key={idx}>
                    <td>{new Date(val.created_at).toLocaleDateString() || 'N/A'}</td>
                    <td>{val.valuation_date || 'N/A'}</td>
                    <td>${val.market_price?.toFixed(2) || 'N/A'}</td>
                    <td>${val.valuation_growth?.toFixed(2) || 'N/A'}</td>
                    <td>${val.valuation_sales_growth?.toFixed(2) || 'N/A'}</td>
                    <td>${val.eps?.toFixed(2) || 'N/A'}</td>
                    <td>${val.avg_price_target?.toFixed(2) || 'N/A'}</td>
                    <td>{val.recommendation_key || 'N/A'}</td>
                    <td>{val.growth_rate ? `${(val.growth_rate).toFixed(2)}%` : 'N/A'}</td>
                    <td>{val.sales_growth_rate ? `${(val.sales_growth_rate).toFixed(2)}%` : 'N/A'}</td>
                    <td>{val.bond_yield ? `${(val.bond_yield).toFixed(2)}%` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </>
  );

  return (
    <div className="App">
      <header className="App-header">
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'valuation' ? 'active' : ''}`}
            onClick={() => setActiveTab('valuation')}
          >
            Valuation Analysis
          </button>
          <button 
            className={`tab-button ${activeTab === 'undervalued' ? 'active' : ''}`}
            onClick={() => setActiveTab('undervalued')}
          >
            Undervalued Stocks
          </button>
          <button 
            className={`tab-button ${activeTab === 'manage-tickers' ? 'active' : ''}`}
            onClick={() => setActiveTab('manage-tickers')}
          >
            Manage Tickers
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'valuation' && renderValuationTab()}
          {activeTab === 'undervalued' && <UndervaluedStocks />}
          {activeTab === 'manage-tickers' && <TickerManagement />}
        </div>
      </header>
    </div>
  );
}

export default App;