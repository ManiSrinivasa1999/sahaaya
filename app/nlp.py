from transformers import pipeline
import re
from typing import Dict, List, Tuple
import json

# Medical symptom patterns and responses
MEDICAL_KNOWLEDGE_BASE = {
    # Fever-related symptoms
    "fever": {
        "keywords": ["fever", "temperature", "hot", "burning", "chills", "shivering"],
        "advice": "Monitor your temperature. Rest, drink fluids, take paracetamol if needed. See a doctor if fever exceeds 102°F (39°C) or persists beyond 3 days.",
        "severity": "medium",
        "urgency": "monitor"
},
    
    # Respiratory symptoms
    "cough": {
        "keywords": ["cough", "coughing", "throat", "phlegm", "mucus", "chest congestion"],
        "advice": "Stay hydrated, use honey for soothing, avoid cold drinks. See a doctor if cough persists beyond 2 weeks or if there's blood.",
        "severity": "low",
        "urgency": "routine"
    },
    
    # Pain symptoms
    "headache": {
        "keywords": ["headache", "head pain", "migraine", "head hurts", "skull pain"],
        "advice": "Rest in a dark room, stay hydrated, avoid loud noises. Take mild painkillers if needed. Seek immediate help for sudden severe headaches.",
        "severity": "medium",
        "urgency": "monitor"
    },
    
    # Digestive symptoms
    "stomach": {
        "keywords": ["stomach", "nausea", "vomiting", "diarrhea", "abdominal", "belly", "digestion"],
        "advice": "Eat light foods, stay hydrated with ORS. Avoid dairy and spicy foods. See a doctor if symptoms persist beyond 48 hours.",
        "severity": "medium",
        "urgency": "monitor"
    },
    
    # Emergency symptoms
    "emergency": {
        "keywords": ["chest pain", "difficulty breathing", "unconscious", "severe bleeding", "heart attack", "stroke"],
        "advice": "⚠️ EMERGENCY: Seek immediate medical attention. Call emergency services or go to the nearest hospital immediately.",
        "severity": "high",
        "urgency": "emergency"
    },
    
    # General wellness
    "wellness": {
        "keywords": ["tired", "fatigue", "weakness", "energy", "sleep", "stress"],
        "advice": "Ensure adequate sleep (7-8 hours), maintain regular exercise, eat balanced meals. Consider stress management techniques.",
        "severity": "low",
        "urgency": "routine"
    }
}

# Language-specific responses
LANGUAGE_RESPONSES = {
    "te": {  # Telugu
        "emergency": "⚠️ అత్యవసరం: వెంటనే వైద్య సహాయం పొందండి।",
        "see_doctor": "వైద్యుడిని సంప్రదించండి।",
        "rest_advice": "విశ్రాంతి తీసుకోండి మరియు నీరు తాగండి।"
    },
    "hi": {  # Hindi
        "emergency": "⚠️ आपातकाल: तुरंत चिकित्सा सहायता लें।",
        "see_doctor": "डॉक्टर से सलाह लें।",
        "rest_advice": "आराम करें और पानी पिएं।"
    },
    "en": {  # English
        "emergency": "⚠️ EMERGENCY: Seek immediate medical attention.",
        "see_doctor": "Consult a doctor.",
        "rest_advice": "Rest and drink plenty of water."
    }
}

# Initialize better medical AI model (if available)
try:
    # Try to use a medical-specific model or better general model
    nlp = pipeline("text2text-generation", model="google/flan-t5-base")
    use_advanced_ai = True
except Exception:
    # Fallback to GPT-2 if medical model not available
    nlp = pipeline("text-generation", model="gpt2")
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

def generate_personalized_advice(symptoms: List[str], severity: str, urgency: str, language: str = "en") -> str:
    """Generate comprehensive medical advice based on symptoms and context"""
    if not symptoms:
        return "I couldn't identify specific symptoms. Please describe your health concern in more detail, or consult a healthcare professional."
    
    advice_parts = []
    
    # Emergency check first
    if urgency == "emergency":
        if language in LANGUAGE_RESPONSES:
            return LANGUAGE_RESPONSES[language]["emergency"]
        return MEDICAL_KNOWLEDGE_BASE["emergency"]["advice"]
    
    # Compile advice from detected symptoms
    for symptom in symptoms:
        if symptom in MEDICAL_KNOWLEDGE_BASE:
            advice_parts.append(MEDICAL_KNOWLEDGE_BASE[symptom]["advice"])
    
    # Add general recommendations based on severity
    if severity == "high":
        advice_parts.append("⚠️ This seems concerning. Please see a doctor immediately.")
    elif severity == "medium":
        advice_parts.append("Monitor your symptoms closely. See a doctor if they worsen or persist.")
    else:
        advice_parts.append("These are generally mild symptoms. Take care and rest.")
    
    # Add disclaimer
    advice_parts.append("\n💡 This is general guidance only. Always consult healthcare professionals for proper diagnosis and treatment.")
    
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
        language: Language code for response (te, hi, en, etc.)
    
    Returns:
        Dict with guidance, symptoms, severity, and metadata
    """
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