import React, { useState } from 'react';
import './App.css';

function App() {
  const [button1Count, setButton1Count] = useState(0);
  const [button2Count, setButton2Count] = useState(0);

  const handleButton1Click = () => {
    const newCount = button1Count + 1;
    setButton1Count(newCount);
    console.log('Button 1 clicked!', { count: newCount, timestamp: new Date().toISOString() });
  };

  const handleButton2Click = () => {
    const newCount = button2Count + 1;
    setButton2Count(newCount);
    console.log('Button 2 clicked!', { count: newCount, timestamp: new Date().toISOString() });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Home Server Control Panel</h1>
        <div className="button-container">
          <div className="button-wrapper">
            <button 
              className="control-button button-1"
              onClick={handleButton1Click}
            >
              Action 1
            </button>
            <p className="counter">Clicks: {button1Count}</p>
          </div>
          <div className="button-wrapper">
            <button 
              className="control-button button-2"
              onClick={handleButton2Click}
            >
              Action 2
            </button>
            <p className="counter">Clicks: {button2Count}</p>
          </div>
        </div>
        <p className="hint">Open developer tools to see console logs</p>
      </header>
    </div>
  );
}

export default App;