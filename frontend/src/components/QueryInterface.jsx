import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const QueryInterface = ({ isConnected, onQueryResult }) => {
  const [query, setQuery] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [queryHistory, setQueryHistory] = useState([]);
  const textareaRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || !isConnected) return;

    setIsProcessing(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/query`, {
        query: query.trim()
      });

      if (response.data.success) {
        // Add to history
        setQueryHistory(prev => [query.trim(), ...prev.slice(0, 9)]); // Keep last 10 queries
        
        // Pass result to parent
        onQueryResult(response.data);
        
        // Clear input
        setQuery('');
      } else {
        throw new Error(response.data.error || 'Query failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Query failed';
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleHistoryClick = (historyQuery) => {
    setQuery(historyQuery);
    textareaRef.current?.focus();
  };

  const exampleQueries = [
    "Show me the total sales by product category",
    "What are the top 10 customers by revenue?",
    "How many orders were placed last month?",
    "Show me sales trends over the past 6 months",
    "Which products have the highest profit margins?"
  ];

  return (
    <div className="query-interface">
      <div className="card">
        <h2>Ask Your Data</h2>
        <p className="subtitle">Ask questions in natural language and get insights with visualizations</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="query">Your Question:</label>
            <textarea
              ref={textareaRef}
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g., Show me total sales by product category for Q4 2024"
              className="query-input"
              rows={3}
              disabled={!isConnected || isProcessing}
              required
            />
            <small className="help-text">
              Press Cmd+Enter (Mac) or Ctrl+Enter (Windows) to submit
            </small>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={!isConnected || isProcessing || !query.trim()}
            className="btn btn-primary"
          >
            {isProcessing ? 'Processing...' : 'Ask Question'}
          </button>
        </form>

        {!isConnected && (
          <div className="connection-warning">
            <p>Please connect to a database first to start asking questions.</p>
          </div>
        )}
      </div>

      {/* Example Queries */}
      <div className="card">
        <h3>Example Questions</h3>
        <div className="example-queries">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="example-query"
              disabled={!isConnected}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* Query History */}
      {queryHistory.length > 0 && (
        <div className="card">
          <h3>Recent Queries</h3>
          <div className="query-history">
            {queryHistory.map((historyQuery, index) => (
              <button
                key={index}
                onClick={() => handleHistoryClick(historyQuery)}
                className="history-query"
                disabled={!isConnected}
              >
                {historyQuery}
              </button>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .query-interface {
          margin-bottom: 2rem;
        }

        .card {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          border: 1px solid #e1e5e9;
          margin-bottom: 1rem;
        }

        .card h2 {
          margin: 0 0 0.5rem 0;
          color: #2c3e50;
          font-size: 1.5rem;
        }

        .card h3 {
          margin: 0 0 1rem 0;
          color: #34495e;
          font-size: 1.25rem;
        }

        .subtitle {
          color: #7f8c8d;
          margin: 0 0 1.5rem 0;
          font-size: 1rem;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 600;
          color: #34495e;
        }

        .query-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
          font-family: inherit;
          resize: vertical;
          min-height: 80px;
        }

        .query-input:focus {
          outline: none;
          border-color: #3498db;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }

        .query-input:disabled {
          background: #f8f9fa;
          cursor: not-allowed;
        }

        .help-text {
          display: block;
          margin-top: 0.25rem;
          color: #7f8c8d;
          font-size: 0.875rem;
        }

        .error-message {
          background: #fee;
          color: #c0392b;
          padding: 0.75rem;
          border-radius: 4px;
          margin-bottom: 1rem;
          border: 1px solid #f5c6cb;
        }

        .btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-primary {
          background: #27ae60;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #229954;
        }

        .connection-warning {
          background: #fff3cd;
          color: #856404;
          padding: 0.75rem;
          border-radius: 4px;
          border: 1px solid #ffeaa7;
          margin-top: 1rem;
        }

        .example-queries, .query-history {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .example-query, .history-query {
          background: #f8f9fa;
          border: 1px solid #e9ecef;
          border-radius: 4px;
          padding: 0.75rem;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.9rem;
          color: #495057;
        }

        .example-query:hover:not(:disabled), .history-query:hover:not(:disabled) {
          background: #e9ecef;
          border-color: #3498db;
        }

        .example-query:disabled, .history-query:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default QueryInterface;
