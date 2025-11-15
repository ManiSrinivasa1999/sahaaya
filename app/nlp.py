from transformers import pipeline
import re
from typing import Dict, List, Tuple
import json

# Enhanced Medical symptom patterns with multilingual support
MEDICAL_KNOWLEDGE_BASE = {
    # Fever-related symptoms
    "fever": {
        "keywords": [
            # English
            "fever", "temperature", "hot", "burning", "chills", "shivering", "feverish", "high temp",
            # Hindi
            "बुखार", "तापमान", "गर्मी", "ठंड लगना", "कंपकंपी",
            # Telugu  
            "జ్వరం", "వేడిమి", "చలిమి", "వణుకు",
            # Tamil
            "காய்ச்சல்", "சூடு", "குளிர்",
            # Bengali
            "জ্বর", "গরম", "কাঁপুনি"
        ],
        "advice": "Monitor your temperature. Rest, drink fluids, take paracetamol if needed. See a doctor if fever exceeds 102°F (39°C) or persists beyond 3 days.",
        "severity": "medium",
        "urgency": "monitor"
    },
    
    # Respiratory symptoms
    "cough": {
        "keywords": [
            # English
            "cough", "coughing", "throat", "phlegm", "mucus", "chest congestion", "sore throat", "throat pain",
            # Hindi
            "खांसी", "गला", "कफ", "गले में दर्द", "सांस की तकलीफ",
            # Telugu
            "దగ్గు", "కఫం", "గొంతు", "గొంతునొప్పి",
            # Tamil
            "இருமல்", "தொண்டை", "கபம்", "தொண்டை வலி",
            # Bengali
            "কাশি", "গলা", "কফ", "গলা ব্যথা"
        ],
        "advice": "Stay hydrated, use honey for soothing, avoid cold drinks. See a doctor if cough persists beyond 2 weeks or if there's blood.",
        "severity": "low",
        "urgency": "routine"
    },
    
    # Pain symptoms  
    "headache": {
        "keywords": [
            # English
            "headache", "head pain", "migraine", "head hurts", "skull pain", "head ache", "brain pain",
            # Hindi
            "सिरदर्द", "सिर में दर्द", "माथे में दर्द", "दिमाग में दर्द",
            # Telugu
            "తలనొప్పి", "తల నొప్పి", "మెదడు నొప్పి",
            # Tamil
            "தலைவலி", "தலை வலி", "மூளை வலி",
            # Bengali
            "মাথাব্যথা", "মাথা ব্যথা", "মস্তিষ্ক ব্যথা"
        ],
        "advice": "Rest in a dark room, stay hydrated, avoid loud noises. Take mild painkillers if needed. Seek immediate help for sudden severe headaches.",
        "severity": "medium",
        "urgency": "monitor"
    },
    
    # Digestive symptoms
    "stomach": {
        "keywords": [
            # English
            "stomach", "nausea", "vomiting", "diarrhea", "abdominal", "belly", "digestion", "stomach pain", "stomach ache", "tummy", "gut",
            # Hindi
            "पेट", "पेट में दर्द", "उल्टी", "दस्त", "पेट की समस्या", "गैस", "एसिडिटी",
            # Telugu
            "కడుపు", "కడుపు నొప్पి", "వాంతులు", "విరేచనలు", "జీర్ణకోశం",
            # Tamil
            "வயிறு", "வயிற்று வலி", "வாந்தி", "வயிற்றுப்போக்கு",
            # Bengali
            "পেট", "পেট ব্যথা", "বমি", "ডায়রিয়া", "হজমের সমস্যা"
        ],
        "advice": "Eat light foods, stay hydrated with ORS. Avoid dairy and spicy foods. See a doctor if symptoms persist beyond 48 hours.",
        "severity": "medium", 
        "urgency": "monitor"
    },
    
    # Emergency symptoms
    "emergency": {
        "keywords": [
            # English
            "chest pain", "difficulty breathing", "unconscious", "severe bleeding", "heart attack", "stroke", "can't breathe", "severe pain", "emergency",
            # Hindi
            "सीने में दर्द", "सांस लेने में तकलीफ", "बेहोश", "दिल का दौरा", "गंभीर दर्द", "आपातकाल",
            # Telugu
            "ఛాతీ నొప్పి", "ఊపిరి ఆడక", "మూర్ఛ", "గుండె దబ్బ", "తీవ్ర నొప్పి",
            # Tamil
            "மார்பு வலி", "மூச்சு திணறல்", "மூர்ச்சை", "மாரடைப்பு", "கடுமையான வலி",
            # Bengali
            "বুকে ব্যথা", "শ্বাসকষ্ট", "অজ্ঞান", "হার্ট অ্যাটাক", "তীব্র ব্যথা"
        ],
        "advice": "⚠️ EMERGENCY: Seek immediate medical attention. Call emergency services or go to the nearest hospital immediately.",
        "severity": "high",
        "urgency": "emergency"
    },
    
    # General wellness
    "wellness": {
        "keywords": [
            # English
            "tired", "fatigue", "weakness", "energy", "sleep", "stress", "exhausted", "weak", "sleepy",
            # Hindi
            "थकान", "कमजोरी", "नींद", "तनाव", "थका हुआ",
            # Telugu
            "అలసట", "బలహీనత", "నిద్రలేమి", "ఒత్తిడి", "అలిసిపోవు",
            # Tamil
            "களைப்பு", "பலவীனம்", "தூக்கமின்மை", "மன அழுத்தம்",
            # Bengali
            "ক্লান্তি", "দুর্বলতা", "ঘুমের সমস্যা", "চাপ", "অবসাদ"
        ],
        "advice": "Ensure adequate sleep (7-8 hours), maintain regular exercise, eat balanced meals. Consider stress management techniques.",
        "severity": "low",
        "urgency": "routine"
    },
    
    # Body pain symptoms
    "body_pain": {
        "keywords": [
            # English
            "body pain", "joint pain", "muscle pain", "back pain", "neck pain", "shoulder pain", "leg pain", "arm pain", "aches", "sore",
            # Hindi
            "शरीर में दर्द", "जोड़ों में दर्द", "मांसपेशियों में दर्द", "पीठ में दर्द", "गर्दन में दर्द",
            # Telugu
            "శరీర నొప్పి", "కీళ్ళ నొప్పి", "వీపు నొప్పి", "మెడ నొప్పి",
            # Tamil
            "உடல் வலி", "மூட்டு வலி", "தசை வலி", "முதுகு வலி",
            # Bengali
            "শরীর ব্যথা", "গাঁট ব্যথা", "পেশী ব্যথা", "পিঠ ব্যথা"
        ],
        "advice": "Apply warm compress, gentle stretching, rest the affected area. Take mild painkillers if needed. See a doctor if pain is severe or persistent.",
        "severity": "medium",
        "urgency": "routine"
    },
    
    # Skin issues
    "skin": {
        "keywords": [
            # English
            "rash", "itching", "skin", "allergy", "red spots", "swelling", "inflammation", "eczema", "burn",
            # Hindi
            "खुजली", "चकत्ते", "त्वचा", "एलर्जी", "लाल दाग", "सूजन",
            # Telugu
            "దురద", "చర్మం", "అలెర్జీ", "ఎర్రటి మచ్చలు", "వాపు",
            # Tamil
            "அரிப்பு", "தோல்", "ஒவ்வாமை", "சிவப்பு புள்ளிகள்", "வீக்கம்",
            # Bengali
            "চুলকানি", "চর্মরোগ", "অ্যালার্জি", "লাল দাগ", "ফোলা"
        ],
        "advice": "Keep the area clean and dry, avoid scratching, use mild soap. Apply cold compress for itching. See a doctor if symptoms worsen or persist.",
        "severity": "low",
        "urgency": "routine"
    }
}

# Enhanced Language-specific responses
LANGUAGE_RESPONSES = {
    "te": {  # Telugu
        "emergency": "⚠️ అత్యవసరం: వెంటనే వైద్య సహాయం పొందండి. 108 కు కాల్ చేయండి లేదా సమీపంలోని ఆసుపత్రికి వెళ్లండి.",
        "fever": "మీ ఉష్ణోగ్రతను పర్యవేక్షించండి. విశ్రాంతి తీసుకోండి, ద్రవాలు తాగండి, అవసరమైతే పారాసిటమాల్ తీసుకోండి. జ్వరం 102°F (39°C) మించినా లేదా 3 రోజులకు మించి ఉంటే వైద్యుడిని చూడండి.",
        "headache": "చీకటి గదిలో విశ్రాంతి తీసుకోండి, నీరు తాగండి, బిగ్గరగా శబ్దాలను నివారించండి. అవసరమైతే తేలికపాటి నొప్పి మందులు తీసుకోండి. అకస్మాత్తుగా తీవ్రమైన తలనొప్పికి వెంటనే సహాయం పొందండి.",
        "cough": "హైడ్రేట్ అయి ఉండండి, గొంతు మృదువుగా ఉండేందుకు తేనె వాడండి, చల్లని పానీయాలను నివారించండి. దగ్గు 2 వారాలకు మించి కొనసాగితే లేదా రక్తం వస్తుంటే వైద్యుడిని చూడండి.",
        "stomach": "తేలికపాటి ఆహారం తీసుకోండి, ORS తో హైడ్రేట్ అయి ఉండండి. పాల ఉత్పాదాలు మరియు మసాలా ఆహారాన్ని నివారించండి. లక్షణాలు 48 గంటలకు మించి ఉంటే వైద్యుడిని చూడండి.",
        "body_pain": "వెచ్చని కంప్రెస్ వేయండి, మెల్లిగా స్ట్రెచ్ చేయండి, ప్రభావిత ప్రాంతానికి విశ్రాంతి ఇవ్వండి. అవసరమైతే తేలికపాటి నొప్పి మందులు తీసుకోండి.",
        "skin": "ప్రాంతాన్ని శుభ్రంగా మరియు పొడిగా ఉంచండి, గోక్కోవడం నివారించండి, తేలికపాటి సబ్బును వాడండి. దురదకు చల్లని కంప్రెస్ వేయండి.",
        "wellness": "తగినంత నిద్ర తీసుకోండి (7-8 గంటలు), క్రమ వ్యాయామం చేయండి, సమతుల్య ఆహారం తీసుకోండి. ఒత్తిడి నిర్వహణ పద్ధతులను పరిగణించండి.",
        "see_doctor": "వైద్యుడిని సంప్రదించండి।",
        "rest_advice": "విశ్రాంతి తీసుకోండి మరియు నీరు తాగండి।",
        "disclaimer": "💡 ఇది సాధారణ మార్గదర్శకత్వం మాత్రమే. సరైన నిర్ధారణ మరియు చికిత్స కోసం ఎల్లప్పుడూ ఆరోగ్య నిపుణులను సంప్రదించండి।"
    },
    "hi": {  # Hindi
        "emergency": "⚠️ आपातकाल: तुरंत चिकित्सा सहायता लें। 108 पर कॉल करें या निकटतम अस्पताल जाएं।",
        "fever": "अपना तापमान मॉनिटर करें। आराम करें, तरल पदार्थ पिएं, जरूरत पड़ने पर पैरासिटामोल लें। यदि बुखार 102°F (39°C) से अधिक हो या 3 दिन से अधिक रहे तो डॉक्टर को दिखाएं।",
        "headache": "अंधेरे कमरे में आराम करें, पानी पिएं, तेज आवाज से बचें। जरूरत पड़ने पर हल्की दर्द निवारक दवा लें। अचानक तेज सिरदर्द के लिए तुरंत मदद लें।",
        "cough": "हाइड्रेटेड रहें, गले को आराम देने के लिए शहद का उपयोग करें, ठंडे पेय से बचें। खांसी 2 सप्ताह से अधिक रहे या खून आए तो डॉक्टर को दिखाएं।",
        "stomach": "हल्का खाना खाएं, ORS से हाइड्रेटेड रहें। डेयरी और मसालेदार भोजन से बचें। लक्षण 48 घंटे से अधिक रहें तो डॉक्टर को दिखाएं।",
        "body_pain": "गर्म सिकाई करें, धीरे से स्ट्रेचिंग करें, प्रभावित क्षेत्र को आराम दें। जरूरत पड़ने पर हल्की दर्द निवारक दवा लें।",
        "skin": "क्षेत्र को साफ और सूखा रखें, खुजली न करें, हल्का साबुन उपयोग करें। खुजली के लिए ठंडी सिकाई करें।",
        "wellness": "पर्याप्त नींद लें (7-8 घंटे), नियमित व्यायाम करें, संतुलित आहार लें। तनाव प्रबंधन तकनीकों पर विचार करें।",
        "see_doctor": "डॉक्टर से सलाह लें।",
        "rest_advice": "आराम करें और पानी पिएं।",
        "disclaimer": "💡 यह केवल सामान्य मार्गदर्शन है। उचित निदान और उपचार के लिए हमेशा स्वास्थ्य पेशेवरों से सलाह लें।"
    },
    "ta": {  # Tamil
        "emergency": "⚠️ அவசரம்: உடனடியாக மருத்துவ உதவி பெறுங்கள். 108 க்கு அழைக்கவும் அல்லது அருகிலுள்ள மருத்துவமனைக்குச் செல்லவும்।",
        "fever": "உங்கள் வெப்பநிலையை கண்காணிக்கவும். ஓய்வு எடுங்கள், திரவங்களை அருந்துங்கள், தேவைப்பட்டால் பாராசிட்டமால் எடுங்கள்।",
        "headache": "இருண்ட அறையில் ஓய்வு எடுங்கள், தண்ணீர் அருந்துங்கள், சத்தம் தவிர்க்கவும்।",
        "cough": "நீரேற்றமாக இருங்கள், தொண்டைக்கு தேன் பயன்படுத்துங்கள், குளிர் பானங்களை தவிர்க்கவும்।",
        "stomach": "இலகுவான உணவு சாப்பிடுங்கள், ORS உடன் நீரேற்றமாக இருங்கள்।",
        "body_pain": "சூடான ஒத்தடம் கொடுங்கள், மெதுவாக நீட்டுங்கள், பாதிக்கப்பட்ட பகுதிக்கு ஓய்வு கொடுங்கள்।",
        "skin": "பகுதியை சுத்தமாகவும் உலர்ந்ததாகவும் வைத்துக் கொள்ளுங்கள், அரிப்பை தவிர்க்கவும்।",
        "wellness": "போதுமான தூக்கம் எடுங்கள் (7-8 மணி நேரம்), வழக்கமான உடற்பயிற்சி செய்யுங்கள்।",
        "disclaimer": "💡 இது பொதுவான வழிகாட்டுதல் மட்டுமே। சரியான நோய் கண்டறிதல் மற்றும் சிகிச்சைக்கு எப்போதும் சுகாதார நிபுணர்களை அணுகவும்।"
    },
    "bn": {  # Bengali
        "emergency": "⚠️ জরুরি: অবিলম্বে চিকিৎসা সহায়তা নিন। ১০৮ এ কল করুন বা নিকটস্থ হাসপাতালে যান।",
        "fever": "আপনার তাপমাত্রা পর্যবেক্ষণ করুন। বিশ্রাম নিন, তরল পান করুন, প্রয়োজনে প্যারাসিটামল নিন।",
        "headache": "অন্ধকার ঘরে বিশ্রাম নিন, পানি পান করুন, উচ্চ শব্দ এড়িয়ে চলুন।",
        "cough": "হাইড্রেটেড থাকুন, গলা প্রশমিত করতে মধু ব্যবহার করুন, ঠান্ডা পানীয় এড়িয়ে চলুন।",
        "stomach": "হালকা খাবার খান, ORS দিয়ে হাইড্রেটেড থাকুন।",
        "body_pain": "গরম সেঁক দিন, আলতো করে স্ট্রেচিং করুন, আক্রান্ত অংশে বিশ্রাম দিন।",
        "skin": "এলাকাটি পরিষ্কার ও শুকনো রাখুন, চুলকানো এড়িয়ে চলুন।",
        "wellness": "পর্যাপ্ত ঘুম নিন (৭-৮ ঘন্টা), নিয়মিত ব্যায়াম করুন।",
        "disclaimer": "💡 এটি শুধুমাত্র সাধারণ নির্দেশনা। সঠিক নির্ণয় ও চিকিৎসার জন্য সবসময় স্বাস্থ্য পেশাদারদের পরামর্শ নিন।"
    },
    "en": {  # English
        "emergency": "⚠️ EMERGENCY: Seek immediate medical attention. Call 108 or go to the nearest hospital.",
        "fever": "Monitor your temperature. Rest, drink fluids, take paracetamol if needed. See a doctor if fever exceeds 102°F (39°C) or persists beyond 3 days.",
        "headache": "Rest in a dark room, stay hydrated, avoid loud noises. Take mild painkillers if needed. Seek immediate help for sudden severe headaches.",
        "cough": "Stay hydrated, use honey for soothing, avoid cold drinks. See a doctor if cough persists beyond 2 weeks or if there's blood.",
        "stomach": "Eat light foods, stay hydrated with ORS. Avoid dairy and spicy foods. See a doctor if symptoms persist beyond 48 hours.",
        "body_pain": "Apply warm compress, gentle stretching, rest the affected area. Take mild painkillers if needed.",
        "skin": "Keep the area clean and dry, avoid scratching, use mild soap. Apply cold compress for itching.",
        "wellness": "Ensure adequate sleep (7-8 hours), maintain regular exercise, eat balanced meals. Consider stress management techniques.",
        "disclaimer": "💡 This is general guidance only. Always consult healthcare professionals for proper diagnosis and treatment."
    }
}

def detect_language(text: str) -> str:
    """Detect language from input text based on script and keywords"""
    # Check for Devanagari script (Hindi)
    if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
        return "hi"
    
    # Check for Telugu script
    if any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):
        return "te"
    
    # Check for Tamil script
    if any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):
        return "ta"
    
    # Check for Bengali script
    if any(ord(char) >= 0x0980 and ord(char) <= 0x09FF for char in text):
        return "bn"
    
    # Default to English
    return "en"

# Initialize better medical AI model (if available)
try:
    # Try to use a medical-specific model or better general model
    # nlp = pipeline("text2text-generation", model="google/flan-t5-base")
    # Disable AI model for testing - use rule-based system only
    nlp = None
    use_advanced_ai = False
except Exception:
    # Fallback to rule-based system only
    nlp = None
    use_advanced_ai = False

def extract_symptoms(text: str) -> List[str]:
    """Extract medical symptoms from user text using pattern matching"""
    text_lower = text.lower()
    detected_symptoms = []
    
    for condition, data in MEDICAL_KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in text_lower:
                detected_symptoms.append(condition)
                break
    
    return list(set(detected_symptoms))  # Remove duplicates

def get_severity_level(symptoms: List[str]) -> Tuple[str, str]:
    """Determine overall severity and urgency based on detected symptoms"""
    severity_levels = {"low": 1, "medium": 2, "high": 3}
    urgency_levels = {"routine": 1, "monitor": 2, "emergency": 3}
    
    max_severity = "low"
    max_urgency = "routine"
    
    for symptom in symptoms:
        if symptom in MEDICAL_KNOWLEDGE_BASE:
            severity = MEDICAL_KNOWLEDGE_BASE[symptom]["severity"]
            urgency = MEDICAL_KNOWLEDGE_BASE[symptom]["urgency"]
            
            if severity_levels[severity] > severity_levels[max_severity]:
                max_severity = severity
            if urgency_levels[urgency] > urgency_levels[max_urgency]:
                max_urgency = urgency
    
    return max_severity, max_urgency

def get_severity_message(severity: str, language: str) -> str:
    """Get severity-based message in appropriate language"""
    messages = {
        "high": {
            "hi": "⚠️ यह चिंताजनक लगता है। कृपया तुरंत डॉक्टर को दिखाएं।",
            "te": "⚠️ ఇది ఆందోళనకరంగా అనిపిస్తోంది. దయచేసి వెంటనే వైద్యుడిని చూడండి।",
            "ta": "⚠️ இது கவலையளிக்கிறது. தயவுசெய்து உடனடியாக மருத்துவரைப் பார்க்கவும்।",
            "bn": "⚠️ এটি উদ্বেগজনক মনে হচ্ছে। অনুগ্রহ করে অবিলম্বে ডাক্তার দেখান।",
            "en": "⚠️ This seems concerning. Please see a doctor immediately."
        },
        "medium": {
            "hi": "अपने लक्षणों की बारीकी से निगरानी करें। यदि वे बिगड़ें या बने रहें तो डॉक्टर को दिखाएं।",
            "te": "మీ లక్షణాలను దగ్గరగా పర్యవేక్షించండి. అవి దిగజారితే లేదా కొనసాగితే వైద్యుడిని చూడండి।",
            "ta": "உங்கள் அறிகுறிகளை உன்னிப்பாகக் கண்காணிக்கவும். அவை மோசமாகினால் மருத்துவரைப் பார்க்கவும்।",
            "bn": "আপনার উপসর্গগুলি নিবিড়ভাবে পর্যবেক্ষণ করুন। তারা খারাপ হলে ডাক্তার দেখান।",
            "en": "Monitor your symptoms closely. See a doctor if they worsen or persist."
        },
        "low": {
            "hi": "ये आम तौर पर हल्के लक्षण हैं। देखभाल करें और आराम करें।",
            "te": "ఇవి సాధారణంగా తేలికపాటి లక్షణాలు. జాగ్రత్తగా ఉండండి మరియు విశ్రాంతి తీసుకోండి।",
            "ta": "இவை பொதுவாக லேசான அறிகுறிகள். கவனமாக இருங்கள் மற்றும் ஓய்வு எடுங்கள்।",
            "bn": "এগুলি সাধারণত হালকা উপসর্গ। যত্ন নিন এবং বিশ্রাম নিন।",
            "en": "These are generally mild symptoms. Take care and rest."
        }
    }
    return messages.get(severity, {}).get(language, messages.get(severity, {}).get("en", ""))

def generate_personalized_advice(symptoms: List[str], severity: str, urgency: str, language: str = "en") -> str:
    """Generate comprehensive medical advice based on symptoms and context"""
    if not symptoms:
        disclaimer = LANGUAGE_RESPONSES.get(language, {}).get("disclaimer", 
            "💡 This is general guidance only. Always consult healthcare professionals for proper diagnosis and treatment.")
        return f"I couldn't identify specific symptoms. Please describe your health concern in more detail. {disclaimer}"
    
    advice_parts = []
    
    # Emergency check first
    if urgency == "emergency":
        return LANGUAGE_RESPONSES.get(language, {}).get("emergency", 
               MEDICAL_KNOWLEDGE_BASE["emergency"]["advice"])
    
    # Get language-specific advice for detected symptoms
    for symptom in symptoms:
        if symptom in MEDICAL_KNOWLEDGE_BASE:
            symptom_advice = LANGUAGE_RESPONSES.get(language, {}).get(symptom)
            if symptom_advice:
                advice_parts.append(symptom_advice)
            else:
                # Fallback to English advice
                advice_parts.append(MEDICAL_KNOWLEDGE_BASE[symptom]["advice"])
    
    # Add severity-based message
    severity_msg = get_severity_message(severity, language)
    if severity_msg:
        advice_parts.append(severity_msg)
    
    # Add disclaimer in appropriate language
    disclaimer = LANGUAGE_RESPONSES.get(language, {}).get("disclaimer", 
        "💡 This is general guidance only. Always consult healthcare professionals for proper diagnosis and treatment.")
    advice_parts.append(disclaimer)
    
    return " ".join(advice_parts)

def get_ai_enhanced_response(user_text: str, detected_symptoms: List[str]) -> str:
    """Use AI to enhance the response with more natural language"""
    if not use_advanced_ai:
        return ""
    
    try:
        # Create a medical-focused prompt
        prompt = f"As a helpful health assistant, provide safe medical advice for someone with these symptoms: {', '.join(detected_symptoms)}. User said: '{user_text}'. Give brief, safe advice and recommend seeing a doctor when appropriate."
        
        response = nlp(prompt, max_length=150, min_length=50, do_sample=True, temperature=0.7)
        if isinstance(response, list) and len(response) > 0:
            return response[0].get('generated_text', '').replace(prompt, '').strip()
    except Exception:
        pass
    
    return ""

def get_health_guidance(user_text: str, language: str = "en") -> Dict:
    """
    Enhanced health guidance with medical accuracy
    
    Args:
        user_text: User's description of symptoms
        language: Language code for response (te, hi, en, etc.) - auto-detected if not provided
    
    Returns:
        Dict with guidance, symptoms, severity, and metadata
    """
    # Auto-detect language if not explicitly set or if set to "en" but text contains non-English
    if language == "en" or language is None:
        detected_lang = detect_language(user_text)
        if detected_lang != "en":
            language = detected_lang
    
    # Extract symptoms using pattern matching
    detected_symptoms = extract_symptoms(user_text)
    
    # Determine severity and urgency
    severity, urgency = get_severity_level(detected_symptoms)
    
    # Generate rule-based advice
    rule_based_advice = generate_personalized_advice(detected_symptoms, severity, urgency, language)
    
    # Try to enhance with AI if available
    ai_advice = get_ai_enhanced_response(user_text, detected_symptoms)
    
    # Combine responses intelligently
    if ai_advice and len(ai_advice.strip()) > 20:  # Use AI if it generated substantial response
        final_advice = ai_advice + "\n\n" + "💡 Always consult healthcare professionals for proper diagnosis."
    else:
        final_advice = rule_based_advice
    
    return {
        "guidance": final_advice,
        "detected_symptoms": detected_symptoms,
        "severity": severity,
        "urgency": urgency,
        "language": language,
        "confidence": "high" if detected_symptoms else "low",
        "disclaimer": "This is general guidance only, not a medical diagnosis."
    }