import React, { useState } from 'react';
import './TickerManagement.css';
import { API_BASE_URL } from '../config';

const TickerManagement = () => {
    const [tickerInput, setTickerInput] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        // Split by commas or newlines and clean up the tickers
        const tickers = tickerInput
            .split(/[,\n]/)
            .map(t => t.trim().toUpperCase())
            .filter(t => t); // Remove empty strings

        try {
            const response = await fetch(`${API_BASE_URL}/tickers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tickers }),
            });

            const data = await response.json();
            
            if (response.ok) {
                setMessage(`Success: ${data.message}`);
                setTickerInput(''); // Clear input on success
            } else {
                setMessage(`Error: ${data.detail || 'Failed to add tickers'}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ticker-management">
            <h2>Add Tickers</h2>
            <p className="description">
                Enter stock tickers to add to the database. Separate multiple tickers with commas or newlines.
            </p>
            <form onSubmit={handleSubmit}>
                <div className="input-group">
                    <textarea
                        value={tickerInput}
                        onChange={(e) => setTickerInput(e.target.value)}
                        placeholder="Example:&#10;AAPL&#10;MSFT, GOOGL&#10;NVDA, AMD, INTC"
                        rows="6"
                        disabled={loading}
                    />
                </div>
                <button type="submit" disabled={loading || !tickerInput.trim()}>
                    {loading ? 'Adding Tickers...' : 'Add Tickers'}
                </button>
            </form>
            {message && (
                <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
                    {message}
                </div>
            )}
        </div>
    );
};

export default TickerManagement;