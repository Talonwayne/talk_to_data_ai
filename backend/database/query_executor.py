import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Optional
import logging
import re
import os
from config import Config

logger = logging.getLogger(__name__)

class QueryExecutor:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        
        # Handle SQLite connection strings
        if connection_string.startswith('sqlite:///'):
            db_path = connection_string.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                # Make relative path absolute from project root
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(project_root, db_path)
            connection_string = f'sqlite:///{db_path}'
        
        self.engine = create_engine(connection_string)
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate SQL query for safety and correctness"""
        query_upper = query.upper().strip()
        
        # Check for forbidden keywords
        for keyword in Config.FORBIDDEN_KEYWORDS:
            if keyword in query_upper:
                return {
                    "valid": False,
                    "error": f"Query contains forbidden keyword: {keyword}",
                    "safe": False
                }
        
        # Check if query starts with allowed types
        if not any(query_upper.startswith(allowed) for allowed in Config.ALLOWED_QUERY_TYPES):
            return {
                "valid": False,
                "error": "Query must start with SELECT or WITH",
                "safe": False
            }
        
        # Basic SQL injection protection
        dangerous_patterns = [
            r';\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE)',
            r'--',
            r'/\*.*\*/',
            r'UNION\s+SELECT',
            r'EXEC\s*\(',
            r'EXECUTE\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    "valid": False,
                    "error": "Query contains potentially dangerous patterns",
                    "safe": False
                }
        
        return {"valid": True, "safe": True}
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute SQL query and return results"""
        # Validate query first
        validation = self.validate_query(query)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "data": None,
                "row_count": 0
            }
        
        try:
            with self.engine.connect() as conn:
                # Execute query with timeout
                result = conn.execute(
                    text(query),
                    execution_options={"timeout": Config.DEFAULT_DB_TIMEOUT}
                )
                
                # Convert to DataFrame
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                # Limit rows if necessary
                if len(df) > Config.MAX_QUERY_ROWS:
                    df = df.head(Config.MAX_QUERY_ROWS)
                    logger.warning(f"Query result truncated to {Config.MAX_QUERY_ROWS} rows")
                
                return {
                    "success": True,
                    "data": df.to_dict('records'),
                    "columns": list(df.columns),
                    "row_count": len(df),
                    "data_types": df.dtypes.astype(str).to_dict()
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "row_count": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "data": None,
                "row_count": 0
            }
    
    def get_query_explanation(self, query: str) -> str:
        """Generate a human-readable explanation of what the query does"""
        try:
            # Parse query to extract basic information
            query_upper = query.upper()
            
            # Extract table names (basic regex)
            table_pattern = r'FROM\s+(\w+)'
            tables = re.findall(table_pattern, query_upper)
            
            # Extract column names
            select_pattern = r'SELECT\s+(.*?)\s+FROM'
            select_match = re.search(select_pattern, query_upper)
            columns = []
            if select_match:
                columns = [col.strip() for col in select_match.group(1).split(',')]
            
            # Extract WHERE conditions
            where_pattern = r'WHERE\s+(.*?)(?:\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)'
            where_match = re.search(where_pattern, query_upper)
            conditions = where_match.group(1) if where_match else None
            
            # Extract GROUP BY
            group_pattern = r'GROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+LIMIT|$)'
            group_match = re.search(group_pattern, query_upper)
            group_by = group_match.group(1) if group_match else None
            
            # Build explanation
            explanation_parts = []
            
            if columns:
                explanation_parts.append(f"Selects {', '.join(columns)}")
            
            if tables:
                explanation_parts.append(f"from {', '.join(tables)}")
            
            if conditions:
                explanation_parts.append(f"where {conditions}")
            
            if group_by:
                explanation_parts.append(f"grouped by {group_by}")
            
            return " ".join(explanation_parts) + "."
            
        except Exception as e:
            logger.error(f"Failed to generate query explanation: {e}")
            return "Query explanation could not be generated."
