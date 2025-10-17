import openai
from typing import Dict, List, Any, Optional
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class QueryAgent:
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.functions = self._define_functions()
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """Define function schemas for OpenAI function calling"""
        return [
            {
                "name": "analyze_query",
                "description": "Analyze a natural language query to understand user intent and extract key information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "The main intent of the query (e.g., 'compare', 'summarize', 'filter', 'aggregate')"
                        },
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key entities mentioned in the query (table names, column names, values)"
                        },
                        "filters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "column": {"type": "string"},
                                    "operator": {"type": "string"},
                                    "value": {"type": "string"}
                                }
                            },
                            "description": "Filter conditions extracted from the query"
                        },
                        "aggregations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "function": {"type": "string"},
                                    "column": {"type": "string"}
                                }
                            },
                            "description": "Aggregation functions needed (SUM, COUNT, AVG, etc.)"
                        },
                        "group_by": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Columns to group by"
                        },
                        "time_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "string"},
                                "end": {"type": "string"},
                                "column": {"type": "string"}
                            },
                            "description": "Time range filters if mentioned"
                        }
                    },
                    "required": ["intent", "entities"]
                }
            },
            {
                "name": "generate_sql",
                "description": "Generate SQL query based on analyzed query intent and database schema",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The complete SQL SELECT query"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Human-readable explanation of what the query does"
                        },
                        "tables_used": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tables used in the query"
                        }
                    },
                    "required": ["query", "explanation", "tables_used"]
                }
            },
            {
                "name": "suggest_visualization",
                "description": "Suggest the best visualization type based on query results and data characteristics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "enum": ["bar", "line", "pie", "scatter", "table"],
                            "description": "Recommended chart type"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Explanation for why this chart type is recommended"
                        },
                        "title": {
                            "type": "string",
                            "description": "Suggested title for the visualization"
                        }
                    },
                    "required": ["chart_type", "reason", "title"]
                }
            }
        ]
    
    def process_query(self, user_query: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a natural language query using OpenAI function calling"""
        try:
            # Create system prompt with schema context
            system_prompt = self._create_system_prompt(schema_info)
            
            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                functions=self.functions,
                function_call="auto",
                temperature=0.1
            )
            
            message = response.choices[0].message
            
            # Handle function calls
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                if function_name == "analyze_query":
                    return self._handle_analyze_query(function_args, user_query, schema_info)
                elif function_name == "generate_sql":
                    return self._handle_generate_sql(function_args)
                elif function_name == "suggest_visualization":
                    return self._handle_suggest_visualization(function_args)
            
            # If no function call, return the text response
            return {
                "success": True,
                "response": message.content,
                "type": "text"
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "success": False,
                "error": f"Failed to process query: {str(e)}"
            }
    
    def _create_system_prompt(self, schema_info: Dict[str, Any]) -> str:
        """Create system prompt with database schema context"""
        schema_desc = schema_info.get("natural_language_description", "")
        tables_info = schema_info.get("tables", {})
        
        prompt = f"""You are a SQL query assistant for a PostgreSQL database. Your job is to help users query their data using natural language.

Database Schema:
{schema_desc}

Available Tables and Columns:
"""
        
        for table_name, table_info in tables_info.items():
            columns = list(table_info["columns"].keys())
            prompt += f"\nTable '{table_name}': {', '.join(columns)}"
            
            # Add foreign key information
            if table_info.get("foreign_keys"):
                fk_info = []
                for fk in table_info["foreign_keys"]:
                    fk_info.append(f"{fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}")
                prompt += f" (Foreign keys: {'; '.join(fk_info)})"
        
        prompt += """

Instructions:
1. When a user asks a question, first analyze their intent using the analyze_query function
2. Then generate appropriate SQL using the generate_sql function
3. Always use proper JOIN syntax when connecting related tables
4. Use appropriate aggregation functions (SUM, COUNT, AVG, etc.) when needed
5. Include proper WHERE clauses for filtering
6. Use GROUP BY when aggregating data
7. Only generate SELECT queries - never DROP, DELETE, UPDATE, or INSERT
8. Be specific with column and table names from the schema
9. If the query involves time-based data, use proper date filtering

Remember: You can only query the tables and columns that exist in the schema above."""
        
        return prompt
    
    def _handle_analyze_query(self, args: Dict[str, Any], user_query: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query analysis and proceed to SQL generation"""
        try:
            # Now generate SQL based on the analysis
            sql_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._create_system_prompt(schema_info)},
                    {"role": "user", "content": user_query}
                ],
                functions=[self.functions[1]],  # generate_sql function
                function_call={"name": "generate_sql"},
                temperature=0.1
            )
            
            sql_message = sql_response.choices[0].message
            if sql_message.function_call and sql_message.function_call.name == "generate_sql":
                sql_args = json.loads(sql_message.function_call.arguments)
                return {
                    "success": True,
                    "analysis": args,
                    "sql": sql_args,
                    "type": "sql_generation"
                }
            
            return {
                "success": False,
                "error": "Failed to generate SQL after analysis"
            }
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {
                "success": False,
                "error": f"SQL generation failed: {str(e)}"
            }
    
    def _handle_generate_sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SQL generation response"""
        return {
            "success": True,
            "sql": args,
            "type": "sql_generation"
        }
    
    def _handle_suggest_visualization(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization suggestion response"""
        return {
            "success": True,
            "visualization": args,
            "type": "visualization_suggestion"
        }
    
    def suggest_visualization_for_results(self, query_results: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Suggest visualization type based on query results"""
        try:
            # Create context about the results
            columns = query_results.get("columns", [])
            data_types = query_results.get("data_types", {})
            row_count = query_results.get("row_count", 0)
            
            context = f"""
Query Results Summary:
- Columns: {', '.join(columns)}
- Data Types: {data_types}
- Row Count: {row_count}
- Original Query: {user_query}

Based on this data, suggest the best visualization type.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a data visualization expert. Analyze query results and suggest the best chart type."},
                    {"role": "user", "content": context}
                ],
                functions=[self.functions[2]],  # suggest_visualization function
                function_call={"name": "suggest_visualization"},
                temperature=0.1
            )
            
            message = response.choices[0].message
            if message.function_call and message.function_call.name == "suggest_visualization":
                viz_args = json.loads(message.function_call.arguments)
                return {
                    "success": True,
                    "visualization": viz_args
                }
            
            return {
                "success": False,
                "error": "Failed to get visualization suggestion"
            }
            
        except Exception as e:
            logger.error(f"Visualization suggestion failed: {e}")
            return {
                "success": False,
                "error": f"Visualization suggestion failed: {str(e)}"
            }
