#!/usr/bin/env python3
"""
Test individual modules of the Sahaaya system
"""
import sys
sys.path.insert(0, '/Users/mabhila9/sahaaya_env/sahaaya-backend')

def test_module(module_name, description):
    """Test importing and basic functionality of a module"""
    print(f"\n🧪 Testing {description}")
    print("-" * 50)
    
    try:
        if module_name == "stt_multilingual":
            from app.stt_multilingual import transcribe_audio
            print("✅ STT module imported successfully")
            print("📝 Note: Actual audio processing will need model download")
            return True
            
        elif module_name == "nlp":
            from app.nlp import get_health_guidance
            print("✅ NLP module imported successfully")
            
            # Test basic text processing
            test_text = "I have a headache and fever"
            try:
                result = get_health_guidance(test_text, "en")
                print("✅ NLP processing test successful")
                print(f"   Input: '{test_text}'")
                print(f"   Output type: {type(result)}")
                if isinstance(result, dict):
                    print(f"   Keys: {list(result.keys())}")
                else:
                    print(f"   Output preview: {str(result)[:100]}...")
                return True
            except Exception as e:
                print(f"⚠️ NLP module imported but processing failed: {e}")
                return False
                
        elif module_name == "tts":
            from app.tts import generate_multilingual_audio
            print("✅ TTS module imported successfully")
            print("📝 Note: Audio generation will need model setup")
            return True
            
        elif module_name == "db":
            from app.db import init_db, get_user_profile
            print("✅ Database module imported successfully")
            
            # Test basic DB functionality
            try:
                init_db()
                print("✅ Database initialization successful")
                return True
            except Exception as e:
                print(f"⚠️ Database module imported but init failed: {e}")
                return False
                
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Module imported but with issues: {e}")
        return False

def main():
    print("🔬 Individual Module Testing")
    print("=" * 60)
    
    modules = [
        ("nlp", "Natural Language Processing"),
        ("db", "Database Operations"),
        ("tts", "Text-to-Speech"),
        ("stt_multilingual", "Speech-to-Text (Multilingual)")
    ]
    
    results = {}
    
    for module_name, description in modules:
        results[module_name] = test_module(module_name, description)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MODULE TEST SUMMARY")
    print("=" * 60)
    
    working_modules = [name for name, status in results.items() if status]
    failing_modules = [name for name, status in results.items() if not status]
    
    print(f"✅ Working Modules ({len(working_modules)}):")
    for module in working_modules:
        print(f"   - {module}")
    
    if failing_modules:
        print(f"\n❌ Modules Needing Attention ({len(failing_modules)}):")
        for module in failing_modules:
            print(f"   - {module}")
    
    print(f"\n🎯 Overall Status: {len(working_modules)}/{len(modules)} modules functional")
    
    print("\n📝 Next Steps:")
    if len(working_modules) >= 2:
        print("   ✅ Core functionality is working")
        print("   🚀 Ready to test complete system integration")
        print("   📦 Can proceed with Version 1.2 offline features")
    else:
        print("   ⚠️ Need to fix module issues before proceeding")
        print("   🔧 Focus on getting basic modules working first")

if __name__ == "__main__":
    main()