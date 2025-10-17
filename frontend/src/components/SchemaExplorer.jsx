import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const SchemaExplorer = ({ isConnected }) => {
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedTables, setExpandedTables] = useState(new Set());
  const [sampleData, setSampleData] = useState({});

  useEffect(() => {
    if (isConnected) {
      fetchSchema();
    } else {
      setSchema(null);
      setSampleData({});
    }
  }, [isConnected]);

  const fetchSchema = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await axios.get(`${API_BASE_URL}/api/schema`);
      if (response.data.success) {
        setSchema(response.data.schema);
      } else {
        throw new Error(response.data.error || 'Failed to fetch schema');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch schema';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleTable = (tableName) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const fetchSampleData = async (tableName) => {
    if (sampleData[tableName]) return; // Already fetched

    try {
      const response = await axios.post(`${API_BASE_URL}/api/sample-data`, {
        table_name: tableName,
        limit: 3
      });

      if (response.data.success) {
        setSampleData(prev => ({
          ...prev,
          [tableName]: response.data.sample_data
        }));
      }
    } catch (err) {
      console.error(`Failed to fetch sample data for ${tableName}:`, err);
    }
  };

  const getColumnTypeIcon = (columnInfo) => {
    const type = columnInfo.type.toLowerCase();
    if (type.includes('int') || type.includes('numeric') || type.includes('decimal')) {
      return '🔢';
    } else if (type.includes('varchar') || type.includes('text') || type.includes('char')) {
      return '📝';
    } else if (type.includes('date') || type.includes('time')) {
      return '📅';
    } else if (type.includes('bool')) {
      return '✅';
    } else {
      return '📄';
    }
  };

  if (!isConnected) {
    return (
      <div className="schema-explorer">
        <div className="card">
          <div className="empty-state">
            <h3>Schema Explorer</h3>
            <p>Connect to a database to explore its schema.</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="schema-explorer">
        <div className="card">
          <div className="loading-state">
            <h3>Loading Schema...</h3>
            <p>Fetching database structure...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="schema-explorer">
        <div className="card">
          <div className="error-state">
            <h3>Schema Error</h3>
            <p>{error}</p>
            <button onClick={fetchSchema} className="btn btn-primary">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!schema || !schema.tables) {
    return (
      <div className="schema-explorer">
        <div className="card">
          <div className="empty-state">
            <h3>No Schema Found</h3>
            <p>No tables found in the connected database.</p>
          </div>
        </div>
      </div>
    );
  }

  const tableNames = Object.keys(schema.tables);

  return (
    <div className="schema-explorer">
      <div className="card">
        <div className="schema-header">
          <h3>Database Schema</h3>
          <p className="schema-description">{schema.natural_language_description}</p>
        </div>

        <div className="tables-list">
          {tableNames.map(tableName => {
            const tableInfo = schema.tables[tableName];
            const isExpanded = expandedTables.has(tableName);
            const columns = Object.keys(tableInfo.columns);
            const foreignKeys = tableInfo.foreign_keys || [];

            return (
              <div key={tableName} className="table-item">
                <div 
                  className="table-header"
                  onClick={() => {
                    toggleTable(tableName);
                    if (!isExpanded) {
                      fetchSampleData(tableName);
                    }
                  }}
                >
                  <div className="table-name">
                    <span className="table-icon">🗂️</span>
                    <strong>{tableName}</strong>
                    <span className="column-count">({columns.length} columns)</span>
                  </div>
                  <div className="expand-icon">
                    {isExpanded ? '▼' : '▶'}
                  </div>
                </div>

                {isExpanded && (
                  <div className="table-details">
                    <div className="columns-section">
                      <h4>Columns</h4>
                      <div className="columns-list">
                        {columns.map(columnName => {
                          const columnInfo = tableInfo.columns[columnName];
                          const isPrimaryKey = columnInfo.primary_key;
                          const isNullable = columnInfo.nullable;
                          
                          return (
                            <div key={columnName} className="column-item">
                              <span className="column-icon">
                                {getColumnTypeIcon(columnInfo)}
                              </span>
                              <span className="column-name">
                                {columnName}
                                {isPrimaryKey && <span className="primary-key">🔑</span>}
                                {!isNullable && <span className="not-null">*</span>}
                              </span>
                              <span className="column-type">{columnInfo.type}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {foreignKeys.length > 0 && (
                      <div className="relationships-section">
                        <h4>Relationships</h4>
                        <div className="relationships-list">
                          {foreignKeys.map((fk, index) => (
                            <div key={index} className="relationship-item">
                              <span className="fk-icon">🔗</span>
                              <span>
                                {fk.column} → {fk.referenced_table}.{fk.referenced_column}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {sampleData[tableName] && (
                      <div className="sample-data-section">
                        <h4>Sample Data</h4>
                        <div className="sample-data-table">
                          <table>
                            <thead>
                              <tr>
                                {Object.keys(sampleData[tableName][0] || {}).map(col => (
                                  <th key={col}>{col}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {sampleData[tableName].map((row, index) => (
                                <tr key={index}>
                                  {Object.values(row).map((value, colIndex) => (
                                    <td key={colIndex}>
                                      {value !== null ? String(value) : <span className="null-value">null</span>}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      <style jsx>{`
        .schema-explorer {
          margin-bottom: 2rem;
        }

        .card {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          border: 1px solid #e1e5e9;
        }

        .schema-header h3 {
          margin: 0 0 0.5rem 0;
          color: #2c3e50;
          font-size: 1.25rem;
        }

        .schema-description {
          color: #7f8c8d;
          font-size: 0.9rem;
          margin: 0 0 1.5rem 0;
          line-height: 1.4;
        }

        .empty-state, .loading-state, .error-state {
          text-align: center;
          padding: 2rem;
          color: #7f8c8d;
        }

        .error-state {
          color: #c0392b;
        }

        .error-state button {
          margin-top: 1rem;
        }

        .tables-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .table-item {
          border: 1px solid #e1e5e9;
          border-radius: 4px;
          overflow: hidden;
        }

        .table-header {
          background: #f8f9fa;
          padding: 0.75rem 1rem;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: background 0.2s;
        }

        .table-header:hover {
          background: #e9ecef;
        }

        .table-name {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .table-icon {
          font-size: 1.2rem;
        }

        .column-count {
          color: #7f8c8d;
          font-weight: normal;
          font-size: 0.9rem;
        }

        .expand-icon {
          color: #7f8c8d;
          font-size: 0.8rem;
        }

        .table-details {
          padding: 1rem;
          background: white;
        }

        .columns-section, .relationships-section, .sample-data-section {
          margin-bottom: 1.5rem;
        }

        .columns-section:last-child, .relationships-section:last-child, .sample-data-section:last-child {
          margin-bottom: 0;
        }

        .columns-section h4, .relationships-section h4, .sample-data-section h4 {
          margin: 0 0 0.75rem 0;
          color: #34495e;
          font-size: 1rem;
        }

        .columns-list, .relationships-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .column-item, .relationship-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .column-name {
          flex: 1;
          font-weight: 500;
        }

        .primary-key {
          color: #e74c3c;
          margin-left: 0.25rem;
        }

        .not-null {
          color: #e67e22;
          margin-left: 0.25rem;
        }

        .column-type {
          color: #7f8c8d;
          font-family: monospace;
          font-size: 0.8rem;
        }

        .sample-data-table {
          overflow-x: auto;
          border: 1px solid #e1e5e9;
          border-radius: 4px;
        }

        .sample-data-table table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.8rem;
        }

        .sample-data-table th {
          background: #f8f9fa;
          padding: 0.5rem;
          text-align: left;
          font-weight: 600;
          border-bottom: 1px solid #e1e5e9;
        }

        .sample-data-table td {
          padding: 0.5rem;
          border-bottom: 1px solid #f1f3f4;
        }

        .sample-data-table tr:last-child td {
          border-bottom: none;
        }

        .null-value {
          color: #95a5a6;
          font-style: italic;
        }

        .btn {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          font-size: 0.9rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #3498db;
          color: white;
        }

        .btn-primary:hover {
          background: #2980b9;
        }
      `}</style>
    </div>
  );
};

export default SchemaExplorer;
