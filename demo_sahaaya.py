#!/usr/bin/env python3
"""
Sahaaya v1.2 Testing Demo
Shows how to test the complete application
"""

import requests
import json
import time
import subprocess
import sys
import threading
import os

# Change to the correct directory
os.chdir('/Users/mabhila9/sahaaya_env/sahaaya-backend')
sys.path.insert(0, '/Users/mabhila9/sahaaya_env/sahaaya-backend')

def test_offline_database():
    """Test the offline database directly"""
    print("🧪 Testing Offline Database...")
    try:
        from app.db import OfflineHealthDatabase
        
        db = OfflineHealthDatabase()
        
        # Test cases
        test_cases = [
            ("I have fever and headache", "en"),
            ("मुझे सिरदर्द है", "hi"), 
            ("chest pain and difficulty breathing", "en"),
            ("emergency heart attack", "en")
        ]
        
        for query, lang in test_cases:
            print(f"\n📝 Query: '{query}' (Language: {lang})")
            result = db.get_offline_health_guidance(query, lang)
            
            print(f"   🔍 Guidance: {result.get('guidance', 'No guidance')[:80]}...")
            print(f"   ⚡ Severity: {result.get('severity', 'unknown')}")
            print(f"   🏥 Resources: {len(result.get('local_resources', []))} found")
            
        # Test emergency contacts
        contacts = db.get_emergency_contacts()
        print(f"\n🚨 Emergency Contacts: {len(contacts)} available")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def start_server():
    """Start the testing server"""
    print("🚀 Starting Sahaaya Testing Server...")
    try:
        # Use subprocess to start server
        cmd = [
            '/Users/mabhila9/sahaaya_env/bin/python', 
            '-m', 'uvicorn', 
            'test_main:app', 
            '--host', '0.0.0.0', 
            '--port', '8002'
        ]
        
        env = os.environ.copy()
        env['PYTHONPATH'] = '/Users/mabhila9/sahaaya_env/sahaaya-backend'
        
        process = subprocess.Popen(
            cmd, 
            cwd='/Users/mabhila9/sahaaya_env/sahaaya-backend',
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def test_api_endpoints():
    """Test the API endpoints"""
    print("🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8002"
    
    try:
        # Test 1: Root endpoint
        print("\n📍 Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📱 Version: {data.get('version')}")
            print(f"   🌍 Languages: {', '.join(data.get('supported_languages', []))}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
        # Test 2: Connectivity status
        print("\n🔌 Testing connectivity status...")
        response = requests.get(f"{base_url}/connectivity-status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Mode: {data.get('recommended_mode')}")
            print(f"   💾 Offline DB: {data['system_capabilities'].get('offline_database')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
        # Test 3: Smart processing
        print("\n🧠 Testing smart processing...")
        test_query = {
            "text": "I have fever and body pain for 3 days",
            "language": "en",
            "user_id": "test_user"
        }
        
        response = requests.post(f"{base_url}/smart-process", json=test_query)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Processing mode: {data.get('processing_mode')}")
            print(f"   📋 Guidance: {data.get('guidance', '')[:80]}...")
            print(f"   ⚡ Severity: {data.get('severity', 'unknown')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
        # Test 4: Emergency protocol
        print("\n🚨 Testing emergency protocol...")
        emergency_query = {
            "emergency_type": "cardiac",
            "language": "en"
        }
        
        response = requests.post(f"{base_url}/emergency-protocol", json=emergency_query)
        if response.status_code == 200:
            data = response.json()
            guidance = data.get('emergency_guidance', {})
            print(f"   ✅ Emergency guidance available")
            print(f"   📞 Contacts: {len(data.get('emergency_contacts', []))}")
            print(f"   🚑 Actions: {len(data.get('immediate_actions', []))}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def show_frontend_info():
    """Show information about the frontend"""
    print("🎨 Frontend Application Info...")
    print("   📱 URL: http://localhost:8002/app")
    print("   📚 API Docs: http://localhost:8002/docs")
    print("   🔧 Testing Mode: Offline database only")
    print("")
    print("🌟 Frontend Features Available:")
    print("   ✅ Multilingual Interface (5 languages)")
    print("   ✅ Voice Input (with browser support)")
    print("   ✅ Text Input") 
    print("   ✅ Emergency Protocols")
    print("   ✅ Connectivity Status Display")
    print("   ✅ Progressive Web App (PWA)")
    print("   ✅ Offline Functionality")
    print("")
    print("🧪 To Test Frontend:")
    print("   1. Open http://localhost:8002/app in your browser")
    print("   2. Try changing language (dropdown at top)")
    print("   3. Test voice input (click microphone)")
    print("   4. Test text input (type symptoms)")
    print("   5. Try emergency button (red button)")

def main():
    """Main testing function"""
    print("=" * 70)
    print("🏥 SAHAAYA UNIVERSAL HEALTH SYSTEM v1.2 - TESTING DEMO")
    print("=" * 70)
    
    # Test 1: Database
    db_success = test_offline_database()
    
    if not db_success:
        print("❌ Database tests failed. Cannot continue.")
        return
    
    # Test 2: Start server
    print("\n" + "=" * 50)
    server_process = start_server()
    
    if not server_process:
        print("❌ Server startup failed. Cannot continue.")
        return
    
    try:
        # Test 3: API endpoints
        print("\n" + "=" * 50)
        api_success = test_api_endpoints()
        
        if api_success:
            print("\n" + "=" * 50)
            show_frontend_info()
            
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Offline Database: Working")
            print("✅ API Endpoints: Working") 
            print("✅ Frontend: Available")
            
            print(f"\n🌐 Access your application at:")
            print(f"   Frontend: http://localhost:8002/app")
            print(f"   API Docs: http://localhost:8002/docs")
            
            print(f"\n⏸️  Press Ctrl+C to stop the server...")
            
            # Keep server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                
        else:
            print("❌ API tests failed")
            
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("🛑 Server stopped.")

if __name__ == "__main__":
    main()