import React, { useEffect, useState } from 'react';
import './App.css'; 

function App() {
    const [message, setMessage] = useState("Loading...");
  useEffect(() => {
    fetch('/api/hello')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage("Error: " + err));
}, []);

return (
    <div className="App">
      <h1>Stock Forecasting Dashboard</h1>
      <p>{message}</p>
    </div>
  );
}

export default App; 