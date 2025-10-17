#!/usr/bin/env python3
"""
Demo script to test the Natural Language Database Query System
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import openai
        import psycopg2
        import plotly
        print("✅ Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js and npm
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✅ Node.js and npm are available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js or npm not found")
        return False
    
    return True

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        print("Please set your OpenAI API key in the .env file")
        return False
    
    print("✅ Environment variables are set")
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Start backend in background
    process = subprocess.Popen([
        sys.executable, "main.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for backend to start
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=1)
            if response.status_code == 200:
                print("✅ Backend server is running on http://localhost:8000")
                return process
        except requests.exceptions.RequestException:
            time.sleep(1)
    
    print("❌ Backend server failed to start")
    process.terminate()
    return None

def start_frontend():
    """Start the React frontend"""
    print("🚀 Starting frontend server...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Start frontend in background
    process = subprocess.Popen([
        "npm", "run", "dev"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for frontend to start
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:5173", timeout=1)
            if response.status_code == 200:
                print("✅ Frontend server is running on http://localhost:5173")
                return process
        except requests.exceptions.RequestException:
            time.sleep(1)
    
    print("❌ Frontend server failed to start")
    process.terminate()
    return None

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing API endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print("❌ Root endpoint failed")
            return False
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main demo function"""
    print("🗣️  Talk to Your Data - Demo Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    try:
        # Test API
        if not test_api():
            print("❌ API tests failed")
            sys.exit(1)
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ Frontend failed to start")
            sys.exit(1)
        
        print("\n🎉 Demo is ready!")
        print("=" * 50)
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n💡 To test the system:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Connect to a PostgreSQL database")
        print("3. Ask questions like 'Show me total sales by category'")
        print("\n⏹️  Press Ctrl+C to stop the demo")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping demo...")
            
    finally:
        # Clean up processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if 'frontend_process' in locals() and frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")

if __name__ == "__main__":
    main()
