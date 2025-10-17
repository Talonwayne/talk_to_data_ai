from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv
from agents.orchestrator import QueryOrchestrator
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Natural Language Database Query System",
    description="Convert natural language queries to SQL and visualize results",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = QueryOrchestrator()

# Pydantic models for request/response
class DatabaseConnection(BaseModel):
    connection_string: Optional[str] = None

class QueryRequest(BaseModel):
    query: str

class SampleDataRequest(BaseModel):
    table_name: str
    limit: Optional[int] = 5

# API Endpoints
@app.post("/api/connect")
async def connect_database(connection: DatabaseConnection):
    """Connect to a PostgreSQL database"""
    try:
        logger.info(f"Connecting to database: {connection.connection_string}")
        result = orchestrator.connect_database(connection.connection_string)
        logger.info(f"Connection result: {result['success']}, tables: {len(result.get('schema', {}).get('tables', {}))}")
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "schema": result["schema"],
                "connection_type": result.get("connection_type", "unknown")
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/query")
async def process_query(query_request: QueryRequest):
    """Process a natural language query"""
    try:
        result = orchestrator.process_natural_language_query(query_request.query)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/api/schema")
async def get_schema():
    """Get current database schema information"""
    try:
        result = orchestrator.get_schema_info()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Schema retrieval failed: {str(e)}")

@app.post("/api/sample-data")
async def get_sample_data(request: SampleDataRequest):
    """Get sample data from a specific table"""
    try:
        result = orchestrator.get_sample_data(request.table_name, request.limit)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Sample data retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Sample data retrieval failed: {str(e)}")

@app.post("/api/disconnect")
async def disconnect_database():
    """Disconnect from current database"""
    try:
        result = orchestrator.disconnect_database()
        return result
        
    except Exception as e:
        logger.error(f"Database disconnection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database disconnection failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Natural Language Database Query System is running"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Natural Language Database Query System",
        "version": "1.0.0",
        "endpoints": {
            "connect": "POST /api/connect",
            "query": "POST /api/query", 
            "schema": "GET /api/schema",
            "sample_data": "POST /api/sample-data",
            "disconnect": "POST /api/disconnect",
            "health": "GET /api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
