#!/usr/bin/env python3
"""
Test script to verify the system is working correctly
"""

import requests
import json
import time

def test_backend():
    """Test backend API endpoints"""
    print("🧪 Testing Backend API...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print("❌ Root endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    return True

def test_frontend():
    """Test frontend accessibility"""
    print("🧪 Testing Frontend...")
    
    try:
        response = requests.get("http://localhost:5173")
        if response.status_code == 200 and "root" in response.text and "main.jsx" in response.text:
            print("✅ Frontend accessible and serving React app")
            return True
        else:
            print("❌ Frontend not loading correctly")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_database_connection():
    """Test database connection with SQLite"""
    print("🧪 Testing Database Connection...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/connect",
            json={},  # No connection string - should use test database automatically
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Database connection successful")
                print(f"📊 Found {len(data.get('schema', {}).get('tables', {}))} tables")
                return True
            else:
                print(f"❌ Database connection failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_query():
    """Test a simple natural language query"""
    print("🧪 Testing Natural Language Query...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={"query": "Show me total sales by category"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Query processing successful")
                print(f"📈 Generated SQL: {data.get('sql_query', 'N/A')[:100]}...")
                print(f"📊 Results: {data.get('query_results', {}).get('row_count', 0)} rows")
                return True
            else:
                print(f"❌ Query processing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Query request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🗣️  Talk to Your Data - System Test")
    print("=" * 50)
    
    tests = [
        ("Backend API", test_backend),
        ("Frontend", test_frontend),
        ("Database Connection", test_database_connection),
        ("Natural Language Query", test_query)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} Test:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! System is working correctly.")
        print("\n💡 You can now:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Use connection string: sqlite:///test_database.db")
        print("   3. Try queries like 'Show me total sales by category'")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return all_passed

if __name__ == "__main__":
    main()
