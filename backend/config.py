import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Database Configuration
    DEFAULT_DB_TIMEOUT = 30  # seconds
    MAX_QUERY_ROWS = 10000
    
    # Security Settings
    ALLOWED_QUERY_TYPES = ["SELECT", "WITH"]
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", 
        "CREATE", "TRUNCATE", "GRANT", "REVOKE"
    ]
    
    # CORS Settings
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
