import React, { useState } from 'react';
import DatabaseConnector from './components/DatabaseConnector';
import QueryInterface from './components/QueryInterface';
import ResultsDisplay from './components/ResultsDisplay';
import SchemaExplorer from './components/SchemaExplorer';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [schema, setSchema] = useState(null);
  const [queryResult, setQueryResult] = useState(null);
  const [connectionError, setConnectionError] = useState('');

  const handleConnectionSuccess = (schemaData) => {
    setIsConnected(!!schemaData);
    setSchema(schemaData);
    setConnectionError('');
    if (!schemaData) {
      setQueryResult(null);
    }
  };

  const handleConnectionError = (error) => {
    setConnectionError(error);
    setIsConnected(false);
    setSchema(null);
    setQueryResult(null);
  };

  const handleQueryResult = (result) => {
    setQueryResult(result);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>🗣️ Talk to Your Data</h1>
          <p>Ask questions in natural language and get insights with interactive visualizations</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="app-grid">
            <div className="left-column">
              <DatabaseConnector 
                onConnectionSuccess={handleConnectionSuccess}
                onConnectionError={handleConnectionError}
              />
              
              {isConnected && (
                <SchemaExplorer isConnected={isConnected} />
              )}
            </div>

            <div className="right-column">
              <QueryInterface 
                isConnected={isConnected}
                onQueryResult={handleQueryResult}
              />
              
              <ResultsDisplay queryResult={queryResult} />
            </div>
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>Powered by OpenAI GPT-4 and Plotly</p>
        </div>
      </footer>
    </div>
  );
}

export default App;