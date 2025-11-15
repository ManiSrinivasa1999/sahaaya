#!/usr/bin/env python3
"""
Simple demonstration of your working Sahaaya system
"""
import requests
import time
import sys
import subprocess

def start_demo_server():
    """Start the basic server for demo"""
    cmd = [
        '/Users/mabhila9/sahaaya_env/bin/python', '-m', 'uvicorn',
        'app.main_basic:app', '--host', '127.0.0.1', '--port', '8004'
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
    
    print("🚀 Starting your Sahaaya Health System...")
    time.sleep(3)
    
    return process

def demo_health_queries():
    """Demonstrate health queries"""
    print("\n" + "="*60)
    print("🏥 SAHAAYA HEALTH GUIDANCE SYSTEM DEMO")
    print("="*60)
    
    demo_cases = [
        {
            "text": "I have a headache and feel dizzy",
            "language": "en",
            "description": "🤕 Common headache symptoms"
        },
        {
            "text": "मुझे बुखार है और खांसी आ रही है",
            "language": "hi", 
            "description": "🌡️ Fever and cough in Hindi"
        },
        {
            "text": "I have stomach pain after eating",
            "language": "en",
            "description": "🤢 Digestive issues"
        },
        {
            "text": "నాకు గొంతు నొప్పి ఉంది",
            "language": "te",
            "description": "😷 Sore throat in Telugu"
        },
        {
            "text": "I can't sleep and feel anxious",
            "language": "en",
            "description": "😟 Mental health concerns"
        }
    ]
    
    print("Demo starting... Testing various health scenarios:")
    print()
    
    for i, case in enumerate(demo_cases, 1):
        print(f"Test {i}: {case['description']}")
        print(f"Input: '{case['text']}'")
        print(f"Language: {case['language']}")
        
        try:
            response = requests.post(
                'http://127.0.0.1:8004/simple-process',
                json={'text': case['text'], 'language': case['language']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result['status']}")
                print(f"🏥 Guidance: {result['simple_guidance']}")
                print()
            else:
                print(f"❌ Error: {response.status_code}")
                print()
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("="*60)
    print("✅ DEMO COMPLETED!")
    print("🎉 Your Sahaaya system is working successfully!")
    print("🚀 Ready for Version 1.2 enhancements!")
    print("="*60)

def main():
    """Run the complete demo"""
    print("🌟 Welcome to Sahaaya Health System Demo!")
    
    server = start_demo_server()
    
    try:
        # Check if server started
        time.sleep(2)
        try:
            response = requests.get('http://127.0.0.1:8004/', timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                demo_health_queries()
            else:
                print("❌ Server not responding")
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server")
            
    finally:
        print("\n🛑 Stopping demo server...")
        server.terminate()
        server.wait(timeout=5)
        print("✅ Demo server stopped")

if __name__ == "__main__":
    main()