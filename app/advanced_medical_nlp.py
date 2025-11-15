"""
Advanced Medical NLP with External Knowledge Integration
This version shows how to integrate with medical databases and APIs
"""

import requests
from typing import Dict, List, Optional
import json
from datetime import datetime

class AdvancedMedicalNLP:
    def __init__(self):
        self.medical_apis = {
            # Example medical APIs (you would need actual API keys)
            "symptom_checker": "https://api.infermedica.com/v3",
            "drug_interactions": "https://api.fda.gov/drug",
            "medical_conditions": "https://api.nhs.uk/conditions"
        }
        
        # Enhanced medical knowledge with ICD-10 codes
        self.medical_conditions = {
            "fever": {
                "icd10": "R50.9",
                "name": "Fever",
                "severity_indicators": {
                    "mild": ["low fever", "slight temperature", "warm"],
                    "moderate": ["fever", "high temperature", "burning"],
                    "severe": ["high fever", "very hot", "burning up", "102", "39°C"]
                },
                "associated_symptoms": ["chills", "sweating", "fatigue"],
                "red_flags": ["difficulty breathing", "severe headache", "stiff neck"]
            },
            "respiratory": {
                "icd10": "J44.9",
                "name": "Respiratory symptoms",
                "severity_indicators": {
                    "mild": ["slight cough", "throat irritation"],
                    "moderate": ["persistent cough", "phlegm", "congestion"],
                    "severe": ["difficulty breathing", "shortness of breath", "wheezing"]
                },
                "red_flags": ["blood in cough", "severe breathing difficulty"]
            }
        }
    
    def analyze_symptom_severity(self, symptoms: List[str], user_text: str) -> Dict:
        """Advanced symptom severity analysis using medical knowledge"""
        severity_score = 0
        red_flags = []
        
        for symptom in symptoms:
            if symptom in self.medical_conditions:
                condition = self.medical_conditions[symptom]
                
                # Check severity indicators
                text_lower = user_text.lower()
                if any(indicator in text_lower for indicator in condition["severity_indicators"]["severe"]):
                    severity_score += 3
                elif any(indicator in text_lower for indicator in condition["severity_indicators"]["moderate"]):
                    severity_score += 2
                elif any(indicator in text_lower for indicator in condition["severity_indicators"]["mild"]):
                    severity_score += 1
                
                # Check for red flags
                for flag in condition.get("red_flags", []):
                    if flag in text_lower:
                        red_flags.append(flag)
                        severity_score += 5  # Red flags significantly increase severity
        
        # Determine overall severity
        if severity_score >= 5 or red_flags:
            return {"level": "high", "score": severity_score, "red_flags": red_flags}
        elif severity_score >= 3:
            return {"level": "medium", "score": severity_score, "red_flags": red_flags}
        else:
            return {"level": "low", "score": severity_score, "red_flags": red_flags}
    
    def get_medical_recommendations(self, symptoms: List[str], severity: Dict) -> Dict:
        """Generate evidence-based medical recommendations"""
        recommendations = {
            "immediate_actions": [],
            "home_care": [],
            "when_to_seek_help": [],
            "follow_up": []
        }
        
        # Red flag handling
        if severity["red_flags"]:
            recommendations["immediate_actions"].append(
                "🚨 URGENT: You have concerning symptoms. Seek immediate medical attention."
            )
            return recommendations
        
        # Severity-based recommendations
        if severity["level"] == "high":
            recommendations["immediate_actions"].extend([
                "Contact a healthcare provider today",
                "Monitor symptoms closely",
                "Have someone check on you regularly"
            ])
        
        # Symptom-specific recommendations
        for symptom in symptoms:
            if symptom == "fever":
                recommendations["home_care"].extend([
                    "Rest and avoid strenuous activity",
                    "Drink plenty of fluids (water, herbal tea)",
                    "Use paracetamol/acetaminophen for comfort (follow dosage instructions)",
                    "Use cool compresses if comfortable"
                ])
                recommendations["when_to_seek_help"].extend([
                    "Fever exceeds 103°F (39.4°C)",
                    "Fever persists beyond 3 days",
                    "Severe headache or neck stiffness develops"
                ])
            
            elif symptom == "cough":
                recommendations["home_care"].extend([
                    "Stay hydrated with warm liquids",
                    "Use honey to soothe throat (adults only)",
                    "Humidify the air you breathe",
                    "Avoid smoke and irritants"
                ])
                recommendations["when_to_seek_help"].extend([
                    "Cough produces blood",
                    "Severe difficulty breathing",
                    "Cough persists beyond 2 weeks"
                ])
        
        # General follow-up advice
        recommendations["follow_up"] = [
            "Keep a symptom diary",
            "Follow up with your primary care provider if symptoms persist",
            "Return to normal activities gradually as you feel better"
        ]
        
        return recommendations
    
    def generate_comprehensive_guidance(self, user_text: str, language: str = "en") -> Dict:
        """Generate comprehensive medical guidance with evidence-based recommendations"""
        
        # Use the existing symptom extraction (from previous implementation)
        from app.nlp import extract_symptoms
        
        symptoms = extract_symptoms(user_text)
        severity = self.analyze_symptom_severity(symptoms, user_text)
        recommendations = self.get_medical_recommendations(symptoms, severity)
        
        # Generate structured response
        response = {
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "detected_symptoms": symptoms,
                "severity_assessment": severity,
                "primary_concern": symptoms[0] if symptoms else "general_wellness"
            },
            "recommendations": recommendations,
            "guidance_summary": self._create_summary(symptoms, severity, recommendations),
            "disclaimers": [
                "This is AI-generated guidance for informational purposes only",
                "Not a substitute for professional medical diagnosis or treatment", 
                "Always consult healthcare providers for persistent or concerning symptoms",
                "In case of emergency, call your local emergency number immediately"
            ],
            "confidence": "high" if symptoms and severity["score"] > 1 else "medium",
            "language": language
        }
        
        return response
    
    def _create_summary(self, symptoms: List[str], severity: Dict, recommendations: Dict) -> str:
        """Create a concise summary of the guidance"""
        if severity["red_flags"]:
            return "⚠️ URGENT: You have concerning symptoms that require immediate medical attention. Please seek help right away."
        
        if not symptoms:
            return "I couldn't identify specific symptoms. Please provide more details about how you're feeling, or consult a healthcare professional."
        
        summary_parts = []
        
        # Opening
        if severity["level"] == "high":
            summary_parts.append("Your symptoms suggest a condition that needs medical attention.")
        elif severity["level"] == "medium":
            summary_parts.append("Your symptoms are concerning and should be monitored closely.")
        else:
            summary_parts.append("Your symptoms appear to be mild but still worth addressing.")
        
        # Key recommendations
        if recommendations["immediate_actions"]:
            summary_parts.append(f"Immediate action: {recommendations['immediate_actions'][0]}")
        
        if recommendations["home_care"]:
            summary_parts.append(f"For now: {', '.join(recommendations['home_care'][:2])}")
        
        # When to seek help
        if recommendations["when_to_seek_help"]:
            summary_parts.append(f"See a doctor if: {recommendations['when_to_seek_help'][0]}")
        
        return " ".join(summary_parts)

# Usage example function
def get_advanced_health_guidance(user_text: str, language: str = "en") -> Dict:
    """Enhanced health guidance using advanced medical NLP"""
    medical_nlp = AdvancedMedicalNLP()
    return medical_nlp.generate_comprehensive_guidance(user_text, language)