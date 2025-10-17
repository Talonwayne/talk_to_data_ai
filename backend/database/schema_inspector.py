import psycopg2
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import json
from typing import Dict, List, Optional, Any
import logging
import os

logger = logging.getLogger(__name__)

class SchemaInspector:
    def __init__(self):
        self.engine = None
        self.schema_cache = {}
    
    def connect(self, connection_string: str) -> bool:
        """Connect to database (PostgreSQL or SQLite) and cache connection"""
        try:
            # Handle SQLite connection strings
            if connection_string.startswith('sqlite:///'):
                # Convert to absolute path for SQLite
                db_path = connection_string.replace('sqlite:///', '')
                if not os.path.isabs(db_path):
                    # Make relative path absolute from project root
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    db_path = os.path.join(project_root, db_path)
                connection_string = f'sqlite:///{db_path}'
            
            self.engine = create_engine(connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_schema(self, connection_string: str) -> Dict[str, Any]:
        """Extract and return database schema information"""
        if connection_string in self.schema_cache:
            return self.schema_cache[connection_string]
        
        # Always reconnect to ensure fresh connection
        if not self.connect(connection_string):
            raise Exception("Failed to connect to database")
        
        try:
            inspector = inspect(self.engine)
            schema_info = {
                "tables": {},
                "relationships": [],
                "natural_language_description": ""
            }
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                # Get column information
                columns = inspector.get_columns(table_name)
                column_info = {}
                
                for column in columns:
                    column_info[column['name']] = {
                        "type": str(column['type']),
                        "nullable": column['nullable'],
                        "default": column.get('default'),
                        "primary_key": column.get('primary_key', False)
                    }
                
                # Get foreign key relationships
                foreign_keys = inspector.get_foreign_keys(table_name)
                fk_info = []
                for fk in foreign_keys:
                    fk_info.append({
                        "column": fk['constrained_columns'][0],
                        "referenced_table": fk['referred_table'],
                        "referenced_column": fk['referred_columns'][0]
                    })
                
                schema_info["tables"][table_name] = {
                    "columns": column_info,
                    "foreign_keys": fk_info
                }
                
                # Add to relationships
                for fk in fk_info:
                    schema_info["relationships"].append({
                        "from_table": table_name,
                        "from_column": fk["column"],
                        "to_table": fk["referenced_table"],
                        "to_column": fk["referenced_column"]
                    })
            
            # Generate natural language description
            schema_info["natural_language_description"] = self._generate_schema_description(schema_info)
            
            # Cache the schema
            self.schema_cache[connection_string] = schema_info
            return schema_info
            
        except Exception as e:
            logger.error(f"Schema extraction failed: {e}")
            raise Exception(f"Failed to extract schema: {e}")
    
    def _generate_schema_description(self, schema_info: Dict[str, Any]) -> str:
        """Generate a natural language description of the database schema"""
        description_parts = []
        
        for table_name, table_info in schema_info["tables"].items():
            columns = list(table_info["columns"].keys())
            primary_keys = [col for col, info in table_info["columns"].items() if info["primary_key"]]
            
            table_desc = f"Table '{table_name}' contains columns: {', '.join(columns)}"
            if primary_keys:
                table_desc += f" (primary key: {', '.join(primary_keys)})"
            
            # Add foreign key information
            if table_info["foreign_keys"]:
                fk_descriptions = []
                for fk in table_info["foreign_keys"]:
                    fk_descriptions.append(f"{fk['column']} references {fk['referenced_table']}.{fk['referenced_column']}")
                table_desc += f". Foreign keys: {'; '.join(fk_descriptions)}"
            
            description_parts.append(table_desc)
        
        return ". ".join(description_parts) + "."
    
    def get_table_sample_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample data from a table for context"""
        if not self.engine:
            raise Exception("No database connection")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get sample data from {table_name}: {e}")
            return []
    
    def validate_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        if not self.engine:
            return False
        
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except Exception:
            return False
