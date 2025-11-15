# 🧪 **Sahaaya Frontend Testing Guide**

## 🎯 **Complete Step-by-Step Testing Instructions**

### **Step 1: Start the Server**

```bash
# Navigate to the backend directory
cd /Users/mabhila9/sahaaya_env/sahaaya-backend

# Activate virtual environment if not already active
source /Users/mabhila9/sahaaya_env/bin/activate

# Start the test server
./start_frontend_test.sh
```

**OR manually:**

```bash
PYTHONPATH=/Users/mabhila9/sahaaya_env/sahaaya-backend /Users/mabhila9/sahaaya_env/bin/python -m uvicorn test_main:app --host 0.0.0.0 --port 8080
```

### **Step 2: Access the Frontend**

Open your web browser and navigate to:

#### **🎨 Main Frontend Application**
**URL**: http://localhost:8080/app

This opens the complete Sahaaya Universal Health interface with:
- Language selection (5 Indian languages)
- Voice & text input options
- Emergency protocols
- Real-time connectivity status
- Progressive Web App features

#### **📚 API Documentation** 
**URL**: http://localhost:8080/docs

Interactive API documentation where you can test all endpoints.

#### **🔌 API Root**
**URL**: http://localhost:8080/

JSON response showing system status and capabilities.

---

## 🧪 **Frontend Testing Scenarios**

### **Test 1: Basic Interface Loading**

1. **Open**: http://localhost:8080/app
2. **Check**:
   - ✅ Language dropdown appears
   - ✅ Emergency button is visible and prominent
   - ✅ Voice/Text input buttons are displayed
   - ✅ Status indicators show "Testing Mode"
   - ✅ Footer shows universal access message

### **Test 2: Language Selection**

1. **Click** language dropdown
2. **Select** different languages:
   - English
   - हिन्दी (Hindi) 
   - తెలుగు (Telugu)
   - தமிழ் (Tamil)
   - বাংলা (Bengali)
3. **Verify**:
   - ✅ Interface text changes language
   - ✅ Placeholders update
   - ✅ Button labels translate

### **Test 3: Text Input Health Queries**

1. **Click** "Text Input" button
2. **Enter** test queries in different languages:

**English Examples:**
```
I have fever and headache for 2 days
Chest pain and difficulty breathing
Stomach ache after eating
```

**Hindi Examples:**
```
मुझे सिरदर्द और बुखार है
पेट में दर्द हो रहा है
```

**Telugu Examples:**
```
నాకు జ్వరం మరియు తలనొప్పి ఉంది
కడుపు నొప్పి ఉంది
```

3. **Click** "Get Health Guidance"
4. **Verify**:
   - ✅ Loading indicator appears
   - ✅ Response section displays guidance
   - ✅ Severity level is shown
   - ✅ Local resources appear (if applicable)
   - ✅ Processing mode shows "offline_testing"

### **Test 4: Voice Input (Browser Dependent)**

1. **Click** "Voice Input" button
2. **Click** microphone button
3. **Allow** microphone permissions when prompted
4. **Speak** a health concern in your preferred language
5. **Verify**:
   - ✅ Recording status changes to "Listening..."
   - ✅ Speech is transcribed to text
   - ✅ Health guidance is provided based on speech

**Note**: Voice input requires microphone permissions and may not work in all browsers.

### **Test 5: Emergency Protocols**

1. **Click** the red "🚨 EMERGENCY" button
2. **Select** an emergency type:
   - Heart/Chest Pain
   - Breathing Problem  
   - Accident/Injury
   - Unconscious
   - Other Emergency
3. **Verify**:
   - ✅ Emergency modal opens
   - ✅ Immediate actions are displayed
   - ✅ Emergency contact numbers shown (108, 100)
   - ✅ Step-by-step guidance provided
   - ✅ Emergency contact buttons work

### **Test 6: Progressive Web App (PWA)**

#### **Desktop/Mobile Browser:**

1. **Open** http://localhost:8080/app in Chrome/Edge
2. **Look for** install prompt or menu option "Install Sahaaya"
3. **Click** install
4. **Verify**:
   - ✅ App installs as standalone application
   - ✅ App icon appears on desktop/home screen
   - ✅ Opens in app-like window (no browser UI)

#### **Mobile Testing:**

1. **Open** on mobile browser
2. **Check** responsive design works
3. **Test** touch interactions
4. **Try** "Add to Home Screen" option

### **Test 7: Offline Functionality**

1. **Disconnect** your internet connection
2. **Refresh** the page or open http://localhost:8080/app
3. **Test** health queries
4. **Verify**:
   - ✅ App still loads (cached by service worker)
   - ✅ Offline database provides responses
   - ✅ Status shows "Offline Mode"
   - ✅ Emergency protocols still work
   - ✅ Local resources are available

### **Test 8: Audio Response (Text-to-Speech)**

1. **Submit** a health query
2. **Click** the speaker button (🔊) in response section
3. **Verify**:
   - ✅ Audio response plays in selected language
   - ✅ Speaker icon changes during playback
   - ✅ Can pause/stop audio

### **Test 9: Consultation History**

1. **Submit** several health queries
2. **Click** "Consultation History" button
3. **Verify**:
   - ✅ Modal opens with past queries
   - ✅ History shows query text and responses
   - ✅ Timestamps are displayed
   - ✅ Can scroll through multiple entries

### **Test 10: API Integration Testing**

**Use the API documentation at** http://localhost:8080/docs

1. **Test** `/smart-process` endpoint:
```json
{
  "text": "I have fever and headache",
  "language": "en",
  "user_id": "test_user_123"
}
```

2. **Test** `/emergency-protocol` endpoint:
```json
{
  "emergency_type": "cardiac",
  "language": "en"
}
```

3. **Test** `/connectivity-status` endpoint (GET)

4. **Verify**:
   - ✅ All endpoints return proper responses
   - ✅ Error handling works correctly
   - ✅ Response formats match frontend expectations

---

## 🔍 **Common Issues & Solutions**

### **Issue**: Frontend doesn't load
**Solution**: 
- Check server is running on port 8080
- Verify http://localhost:8080/ returns JSON response
- Check browser console for errors

### **Issue**: Voice input not working
**Solution**:
- Grant microphone permissions
- Try different browser (Chrome/Edge work best)
- Use text input as fallback

### **Issue**: Language changes don't work
**Solution**:
- Refresh the page
- Check browser console for JavaScript errors
- Verify translations.js is loaded

### **Issue**: PWA install not showing
**Solution**:
- Use HTTPS in production (localhost is OK for testing)
- Check manifest.json is accessible
- Use Chrome/Edge browsers for better PWA support

### **Issue**: Offline mode not working
**Solution**:
- Check service worker registration in DevTools
- Verify caching is working
- Clear browser cache and reload

---

## 📊 **Expected Test Results**

### **✅ Successful Frontend Features:**

1. **Multilingual Interface**: 5 languages fully supported
2. **Responsive Design**: Works on mobile, tablet, desktop
3. **Voice Input**: Speech recognition in multiple languages
4. **Text Input**: Rich text input with multilingual support
5. **Health Guidance**: Offline database provides medical guidance
6. **Emergency System**: Complete emergency protocol system
7. **PWA Features**: Installable, offline-capable application
8. **Audio Output**: Text-to-speech in user's language
9. **History**: Persistent consultation history
10. **Real-time Status**: Connectivity and mode indicators

### **🎯 Success Criteria:**

- ✅ **Load Time**: Frontend loads in < 3 seconds
- ✅ **Responsiveness**: Works on all screen sizes
- ✅ **Accessibility**: Keyboard navigation and screen readers
- ✅ **Offline Capability**: Full functionality without internet
- ✅ **Error Handling**: Graceful error messages
- ✅ **Cross-browser**: Works in Chrome, Firefox, Safari, Edge
- ✅ **Mobile**: Touch-friendly interface
- ✅ **Performance**: Smooth animations and interactions

---

## 🎉 **Celebration Points**

When testing is complete, you'll have validated:

🌍 **Universal Access**: Urban & rural healthcare guidance
🗣️ **Multilingual**: 5 Indian languages supported  
📱 **Mobile-first**: Progressive Web App experience
🔄 **Offline-ready**: Complete functionality without internet
🚨 **Emergency-prepared**: Life-saving protocols accessible
🎯 **User-friendly**: Intuitive interface for all users

**Your Sahaaya Universal Health System is ready to serve users across India, from high-tech urban hospitals to remote rural villages!** 🏥🏘️