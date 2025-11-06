import React, { useState } from 'react';
import './UndervaluedStocks.css';
import { API_BASE_URL } from '../config';

const UndervaluedStocks = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchUndervaluedStocks = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/undervalued-stocks`);
            if (!response.ok) {
                throw new Error('Failed to fetch undervalued stocks');
            }
            const data = await response.json();
            setStocks(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="undervalued-stocks">
            <h2>Undervalued Stocks Analysis</h2>
            <button 
                onClick={fetchUndervaluedStocks}
                disabled={loading}
                className="fetch-button"
            >
                {loading ? 'Loading...' : 'Fetch Undervalued Stocks'}
            </button>

            {error && <div className="error-message">{error}</div>}

            {stocks.length > 0 && (
                <div className="stocks-grid">
                    <table>
                        <thead>
                            <tr>
                                <th>Ticker</th>
                                <th>Rating</th>
                                <th>Market Price</th>
                                <th>Price Target</th>
                                <th>Growth Valuation</th>
                                <th>Sales Growth Valuation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stocks.map((stock) => (
                                <tr key={stock.ticker} className={stock.rating === 'great' ? 'great-value' : 'good-value'}>
                                    <td>{stock.ticker}</td>
                                    <td>{stock.rating}</td>
                                    <td>{stock.market_price ? `$${stock.market_price.toFixed(2)}` : 'N/A'}</td>
                                    <td>{stock.price_target ? `$${stock.price_target.toFixed(2)}` : 'N/A'}</td>
                                    <td>{stock.valuation_growth ? `$${stock.valuation_growth.toFixed(2)}` : 'N/A'}</td>
                                    <td>{stock.valuation_sales_growth ? `$${stock.valuation_sales_growth.toFixed(2)}` : 'N/A'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default UndervaluedStocks;