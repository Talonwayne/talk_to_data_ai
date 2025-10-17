import React, { useState } from 'react';
import Plot from 'react-plotly.js';

const ResultsDisplay = ({ queryResult }) => {
  const [activeTab, setActiveTab] = useState('visualization');

  if (!queryResult) {
    return (
      <div className="results-display">
        <div className="card">
          <div className="empty-state">
            <h3>No Results Yet</h3>
            <p>Ask a question to see your data visualized here.</p>
          </div>
        </div>
      </div>
    );
  }

  const { 
    user_query, 
    sql_query, 
    sql_explanation, 
    query_results, 
    visualization,
    visualization_suggestion 
  } = queryResult;

  const renderVisualization = () => {
    if (!visualization || !visualization.success) {
      return (
        <div className="error-state">
          <h4>Visualization Error</h4>
          <p>{visualization?.error || 'Failed to generate visualization'}</p>
        </div>
      );
    }

    try {
      const chartData = JSON.parse(visualization.chart_data);
      return (
        <div className="chart-container">
          <Plot
            data={chartData.data}
            layout={{
              ...chartData.layout,
              title: visualization.title,
              autosize: true,
              responsive: true
            }}
            config={{
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            }}
            style={{ width: '100%', height: '400px' }}
          />
        </div>
      );
    } catch (error) {
      return (
        <div className="error-state">
          <h4>Chart Rendering Error</h4>
          <p>Failed to render chart: {error.message}</p>
        </div>
      );
    }
  };

  const renderDataTable = () => {
    if (!query_results || !query_results.data || query_results.data.length === 0) {
      return (
        <div className="empty-state">
          <p>No data to display</p>
        </div>
      );
    }

    const { data, columns } = query_results;

    return (
      <div className="data-table-container">
        <div className="table-info">
          <span>{query_results.row_count} rows returned</span>
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={index}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((column, colIndex) => (
                    <td key={colIndex}>
                      {row[column] !== null && row[column] !== undefined 
                        ? String(row[column]) 
                        : <span className="null-value">null</span>
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderSQLDetails = () => {
    return (
      <div className="sql-details">
        <div className="sql-section">
          <h4>Generated SQL Query</h4>
          <pre className="sql-code">
            <code>{sql_query}</code>
          </pre>
        </div>
        
        <div className="sql-section">
          <h4>Query Explanation</h4>
          <p className="sql-explanation">{sql_explanation}</p>
        </div>

        {visualization_suggestion && (
          <div className="sql-section">
            <h4>Visualization Suggestion</h4>
            <p>
              <strong>Chart Type:</strong> {visualization_suggestion.chart_type}<br/>
              <strong>Reason:</strong> {visualization_suggestion.reason}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="results-display">
      <div className="card">
        <div className="results-header">
          <h2>Query Results</h2>
          <p className="query-text">"{user_query}"</p>
        </div>

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'visualization' ? 'active' : ''}`}
            onClick={() => setActiveTab('visualization')}
          >
            📊 Visualization
          </button>
          <button 
            className={`tab ${activeTab === 'data' ? 'active' : ''}`}
            onClick={() => setActiveTab('data')}
          >
            📋 Data Table
          </button>
          <button 
            className={`tab ${activeTab === 'sql' ? 'active' : ''}`}
            onClick={() => setActiveTab('sql')}
          >
            🔍 SQL Details
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'visualization' && renderVisualization()}
          {activeTab === 'data' && renderDataTable()}
          {activeTab === 'sql' && renderSQLDetails()}
        </div>
      </div>

      <style jsx>{`
        .results-display {
          margin-bottom: 2rem;
        }

        .card {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          border: 1px solid #e1e5e9;
        }

        .results-header h2 {
          margin: 0 0 0.5rem 0;
          color: #2c3e50;
          font-size: 1.5rem;
        }

        .query-text {
          color: #7f8c8d;
          font-style: italic;
          margin: 0 0 1.5rem 0;
          font-size: 1rem;
        }

        .tabs {
          display: flex;
          border-bottom: 1px solid #e1e5e9;
          margin-bottom: 1.5rem;
        }

        .tab {
          background: none;
          border: none;
          padding: 0.75rem 1rem;
          cursor: pointer;
          font-size: 1rem;
          color: #7f8c8d;
          border-bottom: 2px solid transparent;
          transition: all 0.2s;
        }

        .tab:hover {
          color: #3498db;
        }

        .tab.active {
          color: #3498db;
          border-bottom-color: #3498db;
          font-weight: 600;
        }

        .tab-content {
          min-height: 200px;
        }

        .empty-state {
          text-align: center;
          padding: 2rem;
          color: #7f8c8d;
        }

        .empty-state h3 {
          margin: 0 0 0.5rem 0;
          color: #95a5a6;
        }

        .error-state {
          background: #fee;
          color: #c0392b;
          padding: 1rem;
          border-radius: 4px;
          border: 1px solid #f5c6cb;
        }

        .error-state h4 {
          margin: 0 0 0.5rem 0;
        }

        .chart-container {
          width: 100%;
          min-height: 400px;
        }

        .data-table-container {
          overflow-x: auto;
        }

        .table-info {
          margin-bottom: 0.5rem;
          color: #7f8c8d;
          font-size: 0.9rem;
        }

        .table-wrapper {
          max-height: 400px;
          overflow-y: auto;
          border: 1px solid #e1e5e9;
          border-radius: 4px;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.9rem;
        }

        .data-table th {
          background: #f8f9fa;
          padding: 0.75rem;
          text-align: left;
          font-weight: 600;
          color: #495057;
          border-bottom: 1px solid #e1e5e9;
          position: sticky;
          top: 0;
        }

        .data-table td {
          padding: 0.75rem;
          border-bottom: 1px solid #f1f3f4;
        }

        .data-table tr:hover {
          background: #f8f9fa;
        }

        .null-value {
          color: #95a5a6;
          font-style: italic;
        }

        .sql-details {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .sql-section h4 {
          margin: 0 0 0.75rem 0;
          color: #34495e;
          font-size: 1.1rem;
        }

        .sql-code {
          background: #f8f9fa;
          border: 1px solid #e1e5e9;
          border-radius: 4px;
          padding: 1rem;
          overflow-x: auto;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.9rem;
          line-height: 1.4;
        }

        .sql-code code {
          color: #2c3e50;
        }

        .sql-explanation {
          background: #e8f4fd;
          border: 1px solid #bee5eb;
          border-radius: 4px;
          padding: 1rem;
          color: #0c5460;
          line-height: 1.5;
        }
      `}</style>
    </div>
  );
};

export default ResultsDisplay;
