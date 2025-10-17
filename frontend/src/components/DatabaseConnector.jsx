import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const DatabaseConnector = ({ onConnectionSuccess, onConnectionError }) => {
  const [connectionString, setConnectionString] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState('');

  const handleConnect = async (e) => {
    e.preventDefault();
    setIsConnecting(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/connect`, {
        connection_string: connectionString
      });

      if (response.data.success) {
        onConnectionSuccess(response.data.schema);
      } else {
        throw new Error(response.data.error || 'Connection failed');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Connection failed';
      setError(errorMessage);
      onConnectionError(errorMessage);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/disconnect`);
      setConnectionString('');
      onConnectionSuccess(null);
    } catch (err) {
      console.error('Disconnect error:', err);
    }
  };

  return (
    <div className="database-connector">
      <div className="card">
        <h2>Database Connection</h2>
        
        <form onSubmit={handleConnect}>
          <div className="form-group">
            <label htmlFor="connectionString">PostgreSQL Connection String:</label>
            <input
              type="text"
              id="connectionString"
              value={connectionString}
              onChange={(e) => setConnectionString(e.target.value)}
              placeholder="postgresql://username:password@localhost:5432/database_name"
              className="connection-input"
              required
            />
            <small className="help-text">
              Format: postgresql://username:password@host:port/database_name
            </small>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="button-group">
            <button 
              type="submit" 
              disabled={isConnecting || !connectionString.trim()}
              className="btn btn-primary"
            >
              {isConnecting ? 'Connecting...' : 'Connect'}
            </button>
            
            {connectionString && (
              <button 
                type="button" 
                onClick={handleDisconnect}
                className="btn btn-secondary"
              >
                Disconnect
              </button>
            )}
          </div>
        </form>
      </div>

      <style jsx>{`
        .database-connector {
          margin-bottom: 2rem;
        }

        .card {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          border: 1px solid #e1e5e9;
        }

        .card h2 {
          margin: 0 0 1rem 0;
          color: #2c3e50;
          font-size: 1.5rem;
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

        .connection-input {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
          font-family: monospace;
        }

        .connection-input:focus {
          outline: none;
          border-color: #3498db;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
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

        .button-group {
          display: flex;
          gap: 0.75rem;
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
          background: #3498db;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #2980b9;
        }

        .btn-secondary {
          background: #95a5a6;
          color: white;
        }

        .btn-secondary:hover {
          background: #7f8c8d;
        }
      `}</style>
    </div>
  );
};

export default DatabaseConnector;
