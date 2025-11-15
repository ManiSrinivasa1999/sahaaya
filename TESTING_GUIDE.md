# 🧪 **Sahaaya Health System - Beginner Testing Guide**

## **Prerequisites Setup**

### **Step 1: Verify Your Environment**
First, let's make sure everything is properly installed in your virtual environment.

```bash
# Make sure you're in the right directory
cd /Users/mabhila9/sahaaya_env/sahaaya-backend

# Activate your virtual environment (if not already active)
source /Users/mabhila9/sahaaya_env/bin/activate

# Verify Python packages are installed
pip list | grep -E "(fastapi|transformers|whisper|torch|TTS)"
```

### **Step 2: Install Missing Dependencies (if needed)**
```bash
# If any packages are missing, install them
pip install fastapi uvicorn openai-whisper transformers torch TTS soundfile
```

---

## **🚀 Phase 1: Start the Server**

### **Step 1: Start FastAPI Server**
```bash
# In your terminal, from the sahaaya-backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Step 2: Test Basic Server Connection**
Open a new terminal and test:
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{"message": "Sahaaya Backend is running"}
```

✅ **If you see this message, your server is working!**

---

## **🗣️ Phase 2: Test Individual Components**

### **Test 1: Speech-to-Text (STT) Module**

#### **Create a Test Script:**
```python
# Create file: test_stt.py
from app.stt_multilingual import transcribe_audio
import json

# Test with different languages
test_cases = [
    {"text": "I have a headache", "language": "en"},
    {"text": "मुझे सिरदर्द है", "language": "hi"}, 
    {"text": "నాకు తలనొప్పి ఉంది", "language": "te"}
]

print("🎤 Testing Speech-to-Text Module...")
print("Note: This test simulates audio input with text")

for i, case in enumerate(test_cases, 1):
    print(f"\nTest {i}: {case['language'].upper()}")
    print(f"Input: '{case['text']}'")
    
    try:
        # Note: In real testing, you'd use actual audio files
        # For now, we'll test the text processing part
        result = transcribe_audio("dummy_audio.wav", case['language'])
        print(f"✅ STT Module loaded successfully for {case['language']}")
        print(f"Function signature working: {type(result)}")
    except Exception as e:
        print(f"❌ Error in STT: {e}")
```

#### **Run the Test:**
```bash
python test_stt.py
```

### **Test 2: Natural Language Processing (NLP) Module**

#### **Create NLP Test:**
```python
# Create file: test_nlp.py
from app.nlp import get_health_guidance
import json

test_symptoms = [
    {"text": "I have fever and headache", "lang": "en"},
    {"text": "मुझे बुखार और सिरदर्द है", "lang": "hi"},
    {"text": "నాకు జ్వరం మరియు తలనొప్పి ఉంది", "lang": "te"},
    {"text": "chest pain and difficulty breathing", "lang": "en"},
    {"text": "stomach pain after eating", "lang": "en"}
]

print("🧠 Testing NLP Health Guidance Module...")

for i, case in enumerate(test_symptoms, 1):
    print(f"\n{'='*50}")
    print(f"Test {i}: {case['lang'].upper()}")
    print(f"Input: '{case['text']}'")
    
    try:
        guidance = get_health_guidance(case['text'], case['lang'])
        print(f"✅ NLP Processing successful")
        print(f"Guidance type: {type(guidance)}")
        
        if isinstance(guidance, dict):
            print(f"Detected symptoms: {guidance.get('symptoms', 'N/A')}")
            print(f"Severity: {guidance.get('severity', 'N/A')}")
            print(f"Guidance preview: {str(guidance.get('guidance', 'N/A'))[:100]}...")
        else:
            print(f"Guidance preview: {str(guidance)[:100]}...")
            
    except Exception as e:
        print(f"❌ Error in NLP: {e}")
        print(f"Error type: {type(e)}")
```

#### **Run NLP Test:**
```bash
python test_nlp.py
```

### **Test 3: Text-to-Speech (TTS) Module**

#### **Create TTS Test:**
```python
# Create file: test_tts.py
from app.tts import generate_multilingual_audio
import os

test_texts = [
    {"text": "Take rest and drink plenty of water", "lang": "en"},
    {"text": "आराम करें और खूब पानी पिएं", "lang": "hi"},
    {"text": "విశ్రాంతి తీసుకోండి మరియు చాలా నీరు తాగండి", "lang": "te"}
]

print("🔊 Testing Text-to-Speech Module...")

for i, case in enumerate(test_texts, 1):
    print(f"\nTest {i}: {case['lang'].upper()}")
    print(f"Text: '{case['text']}'")
    
    try:
        audio_result = generate_multilingual_audio(case['text'], case['lang'])
        print(f"✅ TTS Processing successful")
        print(f"Result type: {type(audio_result)}")
        
        if isinstance(audio_result, dict):
            if audio_result.get('success'):
                file_path = audio_result.get('file_path', 'N/A')
                print(f"Audio file generated: {file_path}")
                if file_path != 'N/A' and os.path.exists(file_path):
                    print(f"✅ File exists and is {os.path.getsize(file_path)} bytes")
                else:
                    print("⚠️ Audio file path provided but file doesn't exist")
            else:
                print(f"❌ TTS failed: {audio_result.get('error', 'Unknown error')}")
        else:
            print(f"Audio result: {audio_result}")
            
    except Exception as e:
        print(f"❌ Error in TTS: {e}")
        print(f"Error details: {type(e)}")
```

#### **Run TTS Test:**
```bash
python test_tts.py
```

---

## **🌐 Phase 3: Test Complete API Endpoints**

### **Test 4: End-to-End API Testing**

#### **Method 1: Using curl (Simple)**
```bash
# Test the main processing endpoint
# Note: Since we don't have actual audio files, we'll test with a dummy path first

curl -X POST "http://localhost:8000/process" \
     -H "Content-Type: application/json" \
     -d '{"audio_file": "test_audio.wav", "language": "en"}'
```

#### **Method 2: Python Test Script (Recommended)**
```python
# Create file: test_api.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🌐 Testing Complete API Endpoints...")
    
    # Test 1: Basic health check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Health check passed!")
        else:
            print("❌ Health check failed!")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Process endpoint (with dummy audio file)
    print("\n2. Testing Process Endpoint...")
    test_cases = [
        {"audio_file": "dummy_english.wav", "language": "en"},
        {"audio_file": "dummy_hindi.wav", "language": "hi"},
        {"audio_file": "dummy_telugu.wav", "language": "te"}
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest 2.{i}: {case['language'].upper()} Processing")
        try:
            response = requests.post(
                f"{BASE_URL}/process",
                json=case
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API call successful!")
                print(f"Detected Language: {result.get('detected_language', 'N/A')}")
                print(f"Input Text: {result.get('input_text', 'N/A')}")
                print(f"Has Guidance: {'guidance' in result}")
                print(f"Has Audio: {'audio' in result}")
            else:
                print(f"❌ API call failed: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure FastAPI is running!")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
```

#### **Run API Test:**
```bash
python test_api.py
```

---

## **📝 Phase 4: Manual Feature Testing**

### **Test 5: Real Audio Testing (Optional)**

If you want to test with real audio:

#### **Create Simple Audio Files:**
```python
# Create file: create_test_audio.py
import numpy as np
import soundfile as sf

def create_test_audio():
    """Create simple test audio files for different scenarios"""
    
    # Generate simple sine wave (represents speech)
    duration = 3  # seconds
    sample_rate = 16000
    frequency = 440  # A note
    
    t = np.linspace(0, duration, duration * sample_rate, False)
    sine_wave = np.sin(frequency * 2 * np.pi * t)
    
    # Add some noise to make it more realistic
    noise = np.random.normal(0, 0.1, sine_wave.shape)
    audio_data = sine_wave + noise
    
    # Normalize
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # Save test files
    test_files = [
        "test_english.wav",
        "test_hindi.wav", 
        "test_telugu.wav"
    ]
    
    for filename in test_files:
        sf.write(filename, audio_data, sample_rate)
        print(f"✅ Created {filename}")

if __name__ == "__main__":
    create_test_audio()
```

#### **Run Audio Creation:**
```bash
python create_test_audio.py
```

### **Test 6: Error Handling**

#### **Test Error Scenarios:**
```python
# Create file: test_errors.py
import requests

BASE_URL = "http://localhost:8000"

def test_error_handling():
    print("⚠️ Testing Error Handling...")
    
    error_cases = [
        {
            "name": "Missing audio file",
            "data": {"language": "en"}
        },
        {
            "name": "Invalid language code", 
            "data": {"audio_file": "test.wav", "language": "invalid"}
        },
        {
            "name": "Empty request",
            "data": {}
        }
    ]
    
    for case in error_cases:
        print(f"\nTesting: {case['name']}")
        try:
            response = requests.post(f"{BASE_URL}/process", json=case['data'])
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code >= 400:
                print("✅ Error handling working correctly")
            else:
                print("⚠️ Expected error but got success")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_error_handling()
```

#### **Run Error Test:**
```bash
python test_errors.py
```

---

## **📊 Expected Results Summary**

### **✅ What Should Work:**
1. **Server Startup**: FastAPI should start without errors
2. **Health Check**: GET `/` should return welcome message
3. **Module Loading**: STT, NLP, TTS modules should load without import errors
4. **Basic Processing**: API should accept requests and return structured responses
5. **Language Support**: System should handle multiple languages (en, hi, te, etc.)

### **⚠️ Expected Limitations in Current Version:**
1. **Audio Processing**: Real audio files might not work without proper Whisper setup
2. **TTS Output**: Audio generation might fail without TTS models
3. **Medical Accuracy**: NLP responses are basic and for testing only

### **❌ Potential Issues & Solutions:**

#### **Common Problems:**

1. **"No module named 'app'"**
   ```bash
   # Solution: Make sure you're in the right directory
   cd /Users/mabhila9/sahaaya_env/sahaaya-backend
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **"ModuleNotFoundError: No module named 'transformers'"**
   ```bash
   # Solution: Install missing packages
   pip install transformers torch
   ```

3. **"Port already in use"**
   ```bash
   # Solution: Use different port
   uvicorn app.main:app --reload --port 8001
   ```

4. **TTS Model Loading Errors**
   ```bash
   # Solution: This is expected - TTS needs model download
   # For now, just verify the function structure works
   ```

---

## **🎯 Testing Checklist**

Use this checklist to track your testing progress:

- [ ] ✅ Virtual environment activated
- [ ] ✅ All dependencies installed
- [ ] ✅ FastAPI server starts successfully
- [ ] ✅ Health check endpoint works (`GET /`)
- [ ] ✅ STT module imports without errors
- [ ] ✅ NLP module processes text correctly
- [ ] ✅ TTS module loads without import errors
- [ ] ✅ POST `/process` endpoint accepts requests
- [ ] ✅ API returns proper JSON responses
- [ ] ✅ Multi-language support functional
- [ ] ✅ Error handling works correctly

### **Success Criteria:**
Your system passes basic testing if you can:
1. Start the FastAPI server
2. Get successful responses from health check
3. Send POST requests to `/process` endpoint
4. Receive structured JSON responses
5. See evidence of multilingual processing

---

## **🚀 Next Steps After Testing**

Once basic testing passes:
1. **Document any issues found**
2. **Note which features work vs. need improvement**
3. **Plan Version 1.2 enhancements**
4. **Consider real audio file testing**
5. **Prepare for offline database features**

---

**Remember: This is Version 1.1 basic testing. Some advanced features (like real audio processing) might need additional setup, which is completely normal! The goal is to verify your basic system architecture is working correctly.** 🎉