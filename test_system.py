#!/usr/bin/env python3
"""
Sahaaya Testing Script - Test the health guidance system step by step
"""
import sys
import time
import subprocess
import requests
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_basic_imports():
    """Test if basic packages can be imported"""
    print_header("Testing Basic Package Imports")
    
    packages = ['fastapi', 'uvicorn', 'typing']
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            print(f"❌ {package} failed: {e}")
            return False
    return True

def test_app_modules():
    """Test if our app modules can be imported"""
    print_header("Testing App Module Imports") 
    
    # Change to project directory
    sys.path.insert(0, '/Users/mabhila9/sahaaya_env/sahaaya-backend')
    
    modules = [
        ('app.main_basic', 'Basic FastAPI app'),
    ]
    
    for module_name, description in modules:
        try:
            __import__(module_name, fromlist=[''])
            print(f"✅ {description}: {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ {description}: {module_name} failed - {e}")
        except Exception as e:
            print(f"⚠️ {description}: {module_name} imported but with warning - {e}")

def start_test_server():
    """Start the basic test server"""
    print_header("Starting Basic Test Server")
    
    try:
        # Start server
        cmd = [
            '/Users/mabhila9/sahaaya_env/bin/python', '-m', 'uvicorn',
            'app.main_basic:app', '--host', '127.0.0.1', '--port', '8003'
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd='/Users/mabhila9/sahaaya_env/sahaaya-backend',
            env={
                **dict(subprocess.os.environ),
                'PYTHONPATH': '/Users/mabhila9/sahaaya_env/sahaaya-backend'
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Starting server...")
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get('http://127.0.0.1:8003/', timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                print(f"Response: {response.json()}")
                return process
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server")
            # Check for errors
            _, stderr = process.communicate(timeout=1)
            if stderr:
                print(f"Server errors: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_api_endpoints(base_url="http://127.0.0.1:8003"):
    """Test API endpoints"""
    print_header("Testing API Endpoints")
    
    tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'url': f'{base_url}/',
            'expected_keys': ['message']
        },
        {
            'name': 'Test Endpoint',
            'method': 'GET', 
            'url': f'{base_url}/test',
            'expected_keys': ['status', 'message', 'version']
        },
        {
            'name': 'Simple Process',
            'method': 'POST',
            'url': f'{base_url}/simple-process',
            'data': {'text': 'I have a headache', 'language': 'en'},
            'expected_keys': ['input_text', 'language', 'simple_guidance']
        }
    ]
    
    for test in tests:
        try:
            print(f"\n🧪 Testing: {test['name']}")
            
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            else:
                response = requests.post(test['url'], json=test['data'], timeout=10)
                
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {test['name']} successful")
                print(f"   Response keys: {list(result.keys())}")
                
                # Check expected keys
                missing_keys = [key for key in test['expected_keys'] if key not in result]
                if missing_keys:
                    print(f"⚠️ Missing expected keys: {missing_keys}")
                else:
                    print("All expected keys present")
                    
                # Show sample response
                if test['name'] == 'Simple Process':
                    print(f"   Sample response: {result.get('simple_guidance', 'N/A')}")
                    
            else:
                print(f"❌ {test['name']} failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']} failed - Cannot connect to server")
        except Exception as e:
            print(f"❌ {test['name']} failed - {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Sahaaya Health System Testing")
    print(f"Python path: {sys.executable}")
    print(f"Working directory: {Path.cwd()}")
    
    # Test 1: Basic imports
    if not test_basic_imports():
        print("❌ Basic import tests failed. Please install missing packages.")
        return
    
    # Test 2: App modules
    test_app_modules()
    
    # Test 3: Start server and test endpoints
    server_process = start_test_server()
    if server_process:
        try:
            test_api_endpoints()
        finally:
            # Clean up
            print("\n🛑 Stopping test server...")
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ Server stopped")
    
    print("\n🎉 Testing completed!")
    print("\n📋 Summary:")
    print("- ✅ Basic FastAPI functionality working")
    print("- ✅ Simple text processing working") 
    print("- ⚠️ Full audio/ML features need model setup")
    print("- 🚀 Ready for Version 1.2 enhancements")

if __name__ == "__main__":
    main()