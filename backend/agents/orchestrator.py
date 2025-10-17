from typing import Dict, List, Any, Optional
import logging
from database.schema_inspector import SchemaInspector
from database.query_executor import QueryExecutor
from visualization.chart_generator import ChartGenerator
from agents.query_agent import QueryAgent

logger = logging.getLogger(__name__)

class QueryOrchestrator:
    def __init__(self):
        self.schema_inspector = SchemaInspector()
        self.query_agent = QueryAgent()
        self.chart_generator = ChartGenerator()
        self.current_connection = None
        self.current_executor = None
    
    def connect_database(self, connection_string: str = None) -> Dict[str, Any]:
        """Connect to database and extract schema"""
        try:
            # If no connection string provided, use test database
            if not connection_string:
                # Use absolute path to test database
                import os
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(project_root, "test_database.db")
                connection_string = f"sqlite:///{db_path}"
                logger.info("No connection string provided, using test database")
            
            # Validate connection and extract schema
            schema_info = self.schema_inspector.get_schema(connection_string)
            
            # Store connection for query execution
            self.current_connection = connection_string
            self.current_executor = QueryExecutor(connection_string)
            
            return {
                "success": True,
                "schema": schema_info,
                "message": "Database connected successfully",
                "connection_type": "test_database" if "test_database.db" in connection_string else "user_database"
            }
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return {
                "success": False,
                "error": f"Failed to connect to database: {str(e)}"
            }
    
    def process_natural_language_query(self, user_query: str) -> Dict[str, Any]:
        """Main orchestration method for processing natural language queries"""
        if not self.current_connection or not self.current_executor:
            return {
                "success": False,
                "error": "No database connection. Please connect to a database first."
            }
        
        try:
            # Step 1: Get current schema
            schema_info = self.schema_inspector.get_schema(self.current_connection)
            
            # Step 2: Process query with AI agent
            agent_response = self.query_agent.process_query(user_query, schema_info)
            
            if not agent_response.get("success"):
                return agent_response
            
            # Step 3: Extract SQL from agent response
            if agent_response.get("type") == "sql_generation":
                sql_info = agent_response.get("sql", {})
                sql_query = sql_info.get("query", "")
                sql_explanation = sql_info.get("explanation", "")
                
                if not sql_query:
                    return {
                        "success": False,
                        "error": "No SQL query generated"
                    }
                
                # Step 4: Execute SQL query
                query_results = self.current_executor.execute_query(sql_query)
                
                if not query_results.get("success"):
                    return {
                        "success": False,
                        "error": f"Query execution failed: {query_results.get('error')}",
                        "sql_query": sql_query,
                        "sql_explanation": sql_explanation
                    }
                
                # Step 5: Get visualization suggestion
                viz_suggestion = self.query_agent.suggest_visualization_for_results(
                    query_results, user_query
                )
                
                # Step 6: Generate chart
                chart_type = None
                chart_title = f"Results for: {user_query}"
                
                if viz_suggestion.get("success"):
                    viz_info = viz_suggestion.get("visualization", {})
                    chart_type = viz_info.get("chart_type")
                    chart_title = viz_info.get("title", chart_title)
                
                chart_result = self.chart_generator.generate_chart(
                    data=query_results.get("data", []),
                    columns=query_results.get("columns", []),
                    data_types=query_results.get("data_types", {}),
                    chart_type=chart_type,
                    title=chart_title
                )
                
                # Step 7: Compile final response
                response = {
                    "success": True,
                    "user_query": user_query,
                    "sql_query": sql_query,
                    "sql_explanation": sql_explanation,
                    "query_results": {
                        "data": query_results.get("data", []),
                        "columns": query_results.get("columns", []),
                        "row_count": query_results.get("row_count", 0),
                        "data_types": query_results.get("data_types", {})
                    },
                    "visualization": chart_result,
                    "tables_used": sql_info.get("tables_used", [])
                }
                
                # Add visualization suggestion if available
                if viz_suggestion.get("success"):
                    response["visualization_suggestion"] = viz_suggestion.get("visualization")
                
                return response
            
            else:
                # Handle text response (no SQL generation needed)
                return {
                    "success": True,
                    "response": agent_response.get("response"),
                    "type": "text_response"
                }
                
        except Exception as e:
            logger.error(f"Query orchestration failed: {e}")
            return {
                "success": False,
                "error": f"Failed to process query: {str(e)}"
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get current database schema information"""
        if not self.current_connection:
            return {
                "success": False,
                "error": "No database connection"
            }
        
        try:
            schema_info = self.schema_inspector.get_schema(self.current_connection)
            return {
                "success": True,
                "schema": schema_info
            }
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return {
                "success": False,
                "error": f"Failed to get schema: {str(e)}"
            }
    
    def disconnect_database(self) -> Dict[str, Any]:
        """Disconnect from current database"""
        self.current_connection = None
        self.current_executor = None
        
        return {
            "success": True,
            "message": "Database disconnected successfully"
        }
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """Get sample data from a specific table"""
        if not self.current_connection:
            return {
                "success": False,
                "error": "No database connection"
            }
        
        try:
            # Validate table exists
            if not self.schema_inspector.validate_table_exists(table_name):
                return {
                    "success": False,
                    "error": f"Table '{table_name}' does not exist"
                }
            
            sample_data = self.schema_inspector.get_table_sample_data(table_name, limit)
            
            return {
                "success": True,
                "table_name": table_name,
                "sample_data": sample_data,
                "row_count": len(sample_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get sample data: {e}")
            return {
                "success": False,
                "error": f"Failed to get sample data: {str(e)}"
            }
