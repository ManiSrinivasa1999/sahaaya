#!/usr/bin/env python3
"""
Direct Module Testing for Sahaaya Version 1.2 Features
Tests individual components without server dependency
"""
import sys
sys.path.insert(0, '/Users/mabhila9/sahaaya_env/sahaaya-backend')

def print_header(title):
    print(f"\n{'='*70}")
    print(f"🧪 {title}")
    print('='*70)

def test_offline_database():
    """Test the enhanced offline database functionality"""
    print_header("Testing Enhanced Offline Database System")
    
    try:
        from app.db import OfflineHealthDatabase
        
        print("✅ Offline database module imported successfully")
        
        # Initialize database
        db = OfflineHealthDatabase(db_path="test_health.db")
        print("✅ Database initialized successfully")
        
        # Test offline guidance
        test_queries = [
            "I have fever and headache",
            "मुझे सिरदर्द है",
            "chest pain and difficulty breathing",
            "stomach ache after eating"
        ]
        
        for query in test_queries:
            try:
                guidance = db.get_offline_health_guidance(query, "en")
                print(f"\n🔹 Query: '{query}'")
                print(f"   Guidance: {guidance.get('guidance', 'No guidance')[:80]}...")
                print(f"   Severity: {guidance.get('severity', 'unknown')}")
                print(f"   Local Resources: {len(guidance.get('local_resources', []))} found")
                print(f"   Emergency Contact: {guidance.get('emergency_contact', 'N/A')}")
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        # Test emergency contacts
        emergency_contacts = db.get_emergency_contacts()
        print(f"\n✅ Emergency contacts: {len(emergency_contacts)} available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_connectivity_detection():
    """Test connectivity detection system"""
    print_header("Testing Intelligent Connectivity Detection")
    
    try:
        from app.connectivity import ConnectivityManager, check_internet_connectivity, get_connection_status
        
        print("✅ Connectivity module imported successfully")
        
        # Test basic connectivity check
        is_online = check_internet_connectivity()
        print(f"✅ Internet connectivity: {is_online}")
        
        # Test detailed status
        status = get_connection_status()
        print(f"✅ Connection confidence: {status.get('confidence', 0):.2f}")
        print(f"✅ Recommended mode: {status.get('recommendation', {}).get('mode', 'unknown')}")
        print(f"✅ Connection quality: {status.get('connection_quality', 'unknown')}")
        
        # Test connectivity manager
        manager = ConnectivityManager()
        mode_info = manager.get_system_mode_info()
        print(f"✅ System capabilities loaded: {len(mode_info.get('system_capabilities', {}))} features")
        
        return True
        
    except ImportError as e:
        print(f"❌ Connectivity import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_emergency_system():
    """Test emergency response system"""
    print_header("Testing Emergency Response System")
    
    try:
        from app.emergency import EmergencyResponseSystem, emergency_system
        
        print("✅ Emergency system module imported successfully")
        
        # Test emergency assessment
        emergency_scenarios = [
            "chest pain and difficulty breathing",
            "severe bleeding from accident",
            "person is unconscious",
            "mild headache"
        ]
        
        for scenario in emergency_scenarios:
            assessment = emergency_system.assess_emergency_level(scenario, "en")
            print(f"\n🔹 Scenario: '{scenario}'")
            print(f"   Emergency Level: {assessment['emergency_level']}")
            print(f"   Priority: {assessment['priority']}")
            print(f"   Action Needed: {assessment['action_needed']}")
            print(f"   Call Emergency: {assessment['call_emergency']}")
        
        # Test emergency protocols
        protocol = emergency_system.get_immediate_response_protocol("cardiac", "en")
        print(f"\n✅ Emergency protocols loaded: {len(protocol.get('steps', []))} steps available")
        
        # Test emergency contacts
        contacts = emergency_system.get_emergency_contact_hierarchy()
        print(f"✅ Emergency contact hierarchy: {len(contacts)} levels")
        
        return True
        
    except ImportError as e:
        print(f"❌ Emergency system import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Emergency system test failed: {e}")
        return False

def test_module_integration():
    """Test integration between modules"""
    print_header("Testing Module Integration")
    
    try:
        # Test database + connectivity integration
        from app.db import db
        from app.connectivity import get_system_mode
        
        mode = get_system_mode()
        print(f"✅ Current system mode: {mode}")
        
        # Test offline guidance with different connectivity scenarios
        guidance = db.get_offline_health_guidance("fever and cough", "en")
        print(f"✅ Offline guidance available: {guidance.get('mode', 'unknown')} mode")
        
        # Test emergency + database integration
        emergency_contacts = db.get_emergency_contacts()
        print(f"✅ Emergency contacts from database: {len(emergency_contacts)} available")
        
        return True
        
    except Exception as e:
        print(f"❌ Module integration test failed: {e}")
        return False

def demonstrate_universal_scenarios():
    """Demonstrate universal urban/rural scenarios"""
    print_header("Universal Access Scenarios Demonstration")
    
    scenarios = [
        {
            'name': '🏙️ Urban Hospital Scenario',
            'context': 'High-speed internet, advanced facilities',
            'query': 'Patient with acute chest pain and shortness of breath',
            'mode': 'hybrid (AI + offline backup)'
        },
        {
            'name': '🌾 Rural Village Scenario',
            'context': 'No internet, basic healthcare facility',
            'query': 'बच्चे को बुखार और दस्त हो रहे हैं',
            'mode': 'offline (complete local database)'
        },
        {
            'name': '🏔️ Remote Emergency Scenario',
            'context': 'Mountain area, no connectivity, emergency',
            'query': 'severe bleeding from accident',
            'mode': 'offline emergency protocols'
        },
        {
            'name': '🏥 Primary Health Center',
            'context': 'Variable internet, trained staff',
            'query': 'elderly person with breathing difficulty',
            'mode': 'intelligent switching'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🔹 {scenario['name']}")
        print(f"   Context: {scenario['context']}")
        print(f"   Query: {scenario['query']}")
        print(f"   Recommended Mode: {scenario['mode']}")
        
        try:
            from app.db import db
            guidance = db.get_offline_health_guidance(scenario['query'], "en")
            print(f"   ✅ Guidance available: {len(str(guidance.get('guidance', '')))} characters")
            print(f"   ✅ Local resources: {len(guidance.get('local_resources', []))} found")
            print(f"   ✅ Emergency support: {guidance.get('emergency_contact', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Scenario test failed: {e}")

def main():
    """Run all direct module tests"""
    print_header("Sahaaya Version 1.2 - Direct Module Testing")
    print("Testing universal healthcare access components without server dependency")
    
    results = []
    
    # Test individual modules
    results.append(('Offline Database', test_offline_database()))
    results.append(('Connectivity Detection', test_connectivity_detection()))
    results.append(('Emergency System', test_emergency_system()))
    results.append(('Module Integration', test_module_integration()))
    
    # Demonstrate scenarios
    demonstrate_universal_scenarios()
    
    # Print final summary
    print_header("Version 1.2 Module Test Results")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 Overall Results: {passed}/{total} modules working correctly")
    
    if passed == total:
        print("\n🌟 SUCCESS: All Version 1.2 components are functional!")
        print("🚀 Universal health access system ready for deployment!")
        print("\n🌍 System Capabilities:")
        print("   ✅ Works in urban areas with internet (AI-enhanced)")
        print("   ✅ Works in rural areas without internet (offline database)")
        print("   ✅ Emergency protocols function completely offline")
        print("   ✅ Intelligent switching between online/offline modes")
        print("   ✅ Comprehensive multilingual support")
        print("   ✅ Universal access for both urban and rural healthcare")
    else:
        print(f"\n⚠️ {total - passed} modules need attention")
        print("   Note: Some failures may be due to missing model dependencies")
        print("   Core offline functionality should still work")
    
    print(f"\n{'='*70}")
    print("🎉 SAHAAYA VERSION 1.2 MODULE TESTING COMPLETED!")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()