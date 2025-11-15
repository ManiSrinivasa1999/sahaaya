"""
Comprehensive Offline Medical Database for Universal Urban/Rural Healthcare Access
Supports complete offline functionality for remote areas without internet connectivity
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import uuid

class OfflineHealthDatabase:
    """
    Comprehensive offline medical database designed for universal access.
    Works seamlessly in both urban (with internet) and rural (no internet) scenarios.
    """
    
    def __init__(self, db_path: str = "sahaaya_health.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize comprehensive medical database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Table 1: Medical Conditions Database
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    symptoms TEXT NOT NULL,  -- JSON list of symptoms
                    severity TEXT NOT NULL,  -- low, medium, high, emergency
                    category TEXT NOT NULL,  -- respiratory, digestive, cardiac, etc.
                    description TEXT NOT NULL,
                    home_treatment TEXT,
                    when_to_see_doctor TEXT NOT NULL,
                    emergency_signs TEXT,  -- JSON list of emergency symptoms
                    prevention TEXT,
                    common_age_groups TEXT,  -- JSON list
                    languages TEXT NOT NULL,  -- JSON dict with translations
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 2: Symptoms Database
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS symptoms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symptom TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity_indicator TEXT NOT NULL,
                    associated_conditions TEXT,  -- JSON list
                    red_flags TEXT,  -- JSON list of warning signs
                    languages TEXT NOT NULL,  -- JSON dict with translations
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 3: Emergency Protocols
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emergency_protocols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emergency_type TEXT NOT NULL,
                    immediate_action TEXT NOT NULL,
                    step_by_step_guide TEXT NOT NULL,  -- JSON list
                    what_not_to_do TEXT NOT NULL,  -- JSON list
                    call_emergency TEXT NOT NULL,
                    severity_assessment TEXT NOT NULL,
                    languages TEXT NOT NULL,  -- JSON dict
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 4: Local Healthcare Resources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS local_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_type TEXT NOT NULL,  -- hospital, clinic, pharmacy, emergency
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    contact TEXT,
                    services TEXT,  -- JSON list of available services
                    emergency_available BOOLEAN DEFAULT 0,
                    distance_km REAL,
                    estimated_cost TEXT,
                    languages_supported TEXT,  -- JSON list
                    availability TEXT,  -- 24/7, business hours, etc.
                    region TEXT NOT NULL,  -- for geographic filtering
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 5: Medication Database
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    generic_name TEXT,
                    category TEXT NOT NULL,
                    dosage_forms TEXT,  -- JSON list: tablet, syrup, injection
                    common_dosages TEXT,  -- JSON dict
                    indications TEXT NOT NULL,  -- what it treats
                    contraindications TEXT,  -- when not to use
                    side_effects TEXT,  -- JSON list
                    cost_range TEXT,
                    availability TEXT,  -- OTC, prescription, hospital-only
                    alternatives TEXT,  -- JSON list of alternatives
                    languages TEXT NOT NULL,  -- JSON dict
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 6: User Consultation History (for offline tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultations (
                    id TEXT PRIMARY KEY,  -- UUID
                    user_query TEXT NOT NULL,
                    detected_language TEXT,
                    symptoms_detected TEXT,  -- JSON list
                    severity_assessment TEXT,
                    guidance_provided TEXT NOT NULL,
                    emergency_flag BOOLEAN DEFAULT 0,
                    follow_up_needed BOOLEAN DEFAULT 0,
                    mode TEXT NOT NULL,  -- offline, online, hybrid
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            
            # Populate with comprehensive medical data
            self._populate_initial_data(cursor)
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise sqlite3.Error(f"Database initialization failed: {e}")
        finally:
            conn.close()
    
    def _populate_initial_data(self, cursor):
        """Populate database with comprehensive medical knowledge"""
        
        # Sample comprehensive medical conditions
        conditions_data = [
            # Respiratory Conditions
            {
                'name': 'Common Cold',
                'symptoms': json.dumps(['runny nose', 'sneezing', 'cough', 'sore throat', 'mild fever']),
                'severity': 'low',
                'category': 'respiratory',
                'description': 'Viral infection of the upper respiratory tract',
                'home_treatment': 'Rest, fluids, warm saltwater gargle, honey for cough',
                'when_to_see_doctor': 'If symptoms persist beyond 10 days or worsen',
                'emergency_signs': json.dumps(['difficulty breathing', 'high fever above 103°F', 'severe headache']),
                'prevention': 'Hand hygiene, avoid close contact with sick people',
                'common_age_groups': json.dumps(['all ages', 'more common in children']),
                'languages': json.dumps({
                    'en': 'Common Cold',
                    'hi': 'सामान्य सर्दी',
                    'te': 'సాధారణ జలుబు',
                    'ta': 'பொதுவான சளி',
                    'bn': 'সাধারণ সর্দি'
                })
            },
            {
                'name': 'Asthma Attack',
                'symptoms': json.dumps(['wheezing', 'shortness of breath', 'chest tightness', 'coughing']),
                'severity': 'high',
                'category': 'respiratory',
                'description': 'Acute breathing difficulty due to airway inflammation',
                'home_treatment': 'Use rescue inhaler, sit upright, stay calm',
                'when_to_see_doctor': 'If no improvement with rescue medication',
                'emergency_signs': json.dumps(['severe breathing difficulty', 'inability to speak', 'blue lips']),
                'prevention': 'Avoid triggers, take controller medications',
                'common_age_groups': json.dumps(['children', 'adults', 'elderly']),
                'languages': json.dumps({
                    'en': 'Asthma Attack',
                    'hi': 'दमा का दौरा',
                    'te': 'ఉబ్బస దాడి',
                    'ta': 'ஆஸ்துமா தாக்குதல்',
                    'bn': 'হাঁপানির আক্রমণ'
                })
            },
            
            # Cardiac Conditions
            {
                'name': 'Heart Attack',
                'symptoms': json.dumps(['chest pain', 'arm pain', 'shortness of breath', 'nausea', 'sweating']),
                'severity': 'emergency',
                'category': 'cardiac',
                'description': 'Blockage of blood flow to heart muscle',
                'home_treatment': 'CALL EMERGENCY IMMEDIATELY - Do not delay',
                'when_to_see_doctor': 'IMMEDIATE EMERGENCY CARE REQUIRED',
                'emergency_signs': json.dumps(['severe chest pain', 'shortness of breath', 'sweating', 'nausea']),
                'prevention': 'Healthy diet, exercise, no smoking, manage stress',
                'common_age_groups': json.dumps(['adults over 40', 'elderly']),
                'languages': json.dumps({
                    'en': 'Heart Attack',
                    'hi': 'दिल का दौरा',
                    'te': 'గుండెపోటు',
                    'ta': 'மாரடைப்பு',
                    'bn': 'হার্ট অ্যাটাক'
                })
            },
            
            # Digestive Conditions
            {
                'name': 'Food Poisoning',
                'symptoms': json.dumps(['nausea', 'vomiting', 'diarrhea', 'stomach cramps', 'fever']),
                'severity': 'medium',
                'category': 'digestive',
                'description': 'Illness from contaminated food or water',
                'home_treatment': 'Fluids, BRAT diet, rest, ORS solution',
                'when_to_see_doctor': 'If severe dehydration or symptoms persist 3+ days',
                'emergency_signs': json.dumps(['severe dehydration', 'blood in vomit', 'high fever', 'severe abdominal pain']),
                'prevention': 'Safe food handling, clean water, proper cooking',
                'common_age_groups': json.dumps(['all ages', 'higher risk in children and elderly']),
                'languages': json.dumps({
                    'en': 'Food Poisoning',
                    'hi': 'खाद्य विषाक्तता',
                    'te': 'ఆహార విషప్రయోగం',
                    'ta': 'உணவு விஷம்',
                    'bn': 'খাদ্য বিষক্রিয়া'
                })
            },
            
            # Neurological Conditions  
            {
                'name': 'Migraine Headache',
                'symptoms': json.dumps(['severe headache', 'nausea', 'light sensitivity', 'sound sensitivity']),
                'severity': 'medium',
                'category': 'neurological',
                'description': 'Intense headache often with sensory disturbances',
                'home_treatment': 'Dark room, rest, cold compress, hydration',
                'when_to_see_doctor': 'If sudden severe headache or pattern changes',
                'emergency_signs': json.dumps(['sudden severe headache', 'fever with headache', 'vision loss']),
                'prevention': 'Identify triggers, stress management, regular sleep',
                'common_age_groups': json.dumps(['adults 20-50', 'more common in women']),
                'languages': json.dumps({
                    'en': 'Migraine Headache',
                    'hi': 'माइग्रेन सिरदर्द',
                    'te': 'మైగ్రేన్ తలనొప్పి',
                    'ta': 'ஒற்றைத் தலைவலி',
                    'bn': 'মাইগ্রেন মাথাব্যথা'
                })
            }
        ]
        
        for condition in conditions_data:
            cursor.execute("""
                INSERT OR IGNORE INTO conditions 
                (name, symptoms, severity, category, description, home_treatment, 
                when_to_see_doctor, emergency_signs, prevention, common_age_groups, languages)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                condition['name'], condition['symptoms'], condition['severity'],
                condition['category'], condition['description'], condition['home_treatment'],
                condition['when_to_see_doctor'], condition['emergency_signs'], 
                condition['prevention'], condition['common_age_groups'], condition['languages']
            ))
        
        # Sample Emergency Protocols
        emergency_protocols = [
            {
                'emergency_type': 'Heart Attack',
                'immediate_action': 'Call 108 immediately. Keep person sitting upright.',
                'step_by_step_guide': json.dumps([
                    'Call emergency services (108/102)',
                    'Give aspirin if person conscious and not allergic',
                    'Keep person calm and sitting upright',
                    'Loosen tight clothing',
                    'Monitor breathing and pulse',
                    'Be ready to perform CPR if needed'
                ]),
                'what_not_to_do': json.dumps([
                    'Do not give water if unconscious',
                    'Do not leave person alone',
                    'Do not give medication except aspirin',
                    'Do not let person walk or exert'
                ]),
                'call_emergency': '108 (Emergency) / 102 (Ambulance)',
                'severity_assessment': 'Life-threatening - Act immediately',
                'languages': json.dumps({
                    'en': 'Heart Attack Emergency Protocol',
                    'hi': 'हृदयाघात आपातकालीन प्रोटोकॉल',
                    'te': 'గుండెపోటు అత్యవసర ప్రోటోకాల్',
                    'ta': 'இதய அத்யாவசிய நெறிமுறை',
                    'bn': 'হার্ট অ্যাটাক জরুরী প্রোটোকল'
                })
            },
            {
                'emergency_type': 'Choking',
                'immediate_action': 'If person can cough, encourage coughing. If not, perform Heimlich maneuver.',
                'step_by_step_guide': json.dumps([
                    'Ask "Are you choking?"',
                    'If yes and cannot speak, perform back blows',
                    'Stand behind person, lean them forward',
                    'Give 5 sharp back blows between shoulder blades',
                    'If unsuccessful, perform abdominal thrusts',
                    'Continue alternating until object clears or person unconscious'
                ]),
                'what_not_to_do': json.dumps([
                    'Do not hit back if person can cough',
                    'Do not use fingers to remove object blindly',
                    'Do not give abdominal thrusts to pregnant women'
                ]),
                'call_emergency': '108 if person becomes unconscious',
                'severity_assessment': 'Life-threatening if severe',
                'languages': json.dumps({
                    'en': 'Choking Emergency Protocol',
                    'hi': 'दम घुटने का आपातकालीन प्रोटोकॉल',
                    'te': 'ఉక్కిరిబిక్కిరి అత్యవసర ప్రోటోకాల్',
                    'ta': 'மூச்சுத்திணறல் அவசர நெறிமுறை',
                    'bn': 'শ্বাসরোধ জরুরী প্রোটোকল'
                })
            }
        ]
        
        for protocol in emergency_protocols:
            cursor.execute("""
                INSERT OR IGNORE INTO emergency_protocols
                (emergency_type, immediate_action, step_by_step_guide, what_not_to_do,
                call_emergency, severity_assessment, languages)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                protocol['emergency_type'], protocol['immediate_action'],
                protocol['step_by_step_guide'], protocol['what_not_to_do'],
                protocol['call_emergency'], protocol['severity_assessment'],
                protocol['languages']
            ))
        
        # Sample Local Resources (Templates that can be customized by location)
        local_resources = [
            {
                'resource_type': 'emergency',
                'name': 'Emergency Services',
                'location': 'Nationwide',
                'contact': '108',
                'services': json.dumps(['emergency medical care', 'ambulance', '24/7 response']),
                'emergency_available': True,
                'distance_km': 0,
                'estimated_cost': 'Government service - minimal cost',
                'languages_supported': json.dumps(['hi', 'en', 'regional languages']),
                'availability': '24/7',
                'region': 'all'
            },
            {
                'resource_type': 'hospital',
                'name': 'District Government Hospital',
                'location': 'District Headquarters',
                'contact': '102',
                'services': json.dumps(['general medicine', 'emergency care', 'surgery', 'maternity']),
                'emergency_available': True,
                'distance_km': 25,
                'estimated_cost': 'Government rates - affordable',
                'languages_supported': json.dumps(['local language', 'hindi', 'english']),
                'availability': '24/7 emergency, business hours for routine',
                'region': 'rural'
            },
            {
                'resource_type': 'pharmacy',
                'name': 'Local Pharmacy/Medical Store',
                'location': 'Village/Town Center',
                'contact': 'Local number varies',
                'services': json.dumps(['basic medications', 'first aid supplies', 'health advice']),
                'emergency_available': False,
                'distance_km': 5,
                'estimated_cost': 'Market rates',
                'languages_supported': json.dumps(['local language']),
                'availability': 'Business hours',
                'region': 'rural'
            }
        ]
        
        for resource in local_resources:
            cursor.execute("""
                INSERT OR IGNORE INTO local_resources
                (resource_type, name, location, contact, services, emergency_available,
                distance_km, estimated_cost, languages_supported, availability, region)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource['resource_type'], resource['name'], resource['location'],
                resource['contact'], resource['services'], resource['emergency_available'],
                resource['distance_km'], resource['estimated_cost'],
                resource['languages_supported'], resource['availability'], resource['region']
            ))

    def get_offline_health_guidance(self, user_query: str, language: str = "en") -> Dict:
        """
        Comprehensive offline health guidance based on symptoms and query
        Works entirely without internet connectivity
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract potential symptoms from query
            detected_symptoms = self._extract_symptoms_from_text(user_query.lower(), cursor)
            
            if not detected_symptoms:
                return self._get_general_health_advice(language)
            
            # Find matching conditions
            matching_conditions = self._find_matching_conditions(detected_symptoms, cursor)
            
            # Assess severity and check for emergencies
            severity_assessment = self._assess_severity(detected_symptoms, matching_conditions, cursor)
            
            # Check if emergency protocols needed
            emergency_info = None
            if severity_assessment['is_emergency']:
                emergency_info = self._get_emergency_protocols(severity_assessment['emergency_type'], cursor)
            
            # Get appropriate guidance
            guidance = self._generate_comprehensive_guidance(
                detected_symptoms, matching_conditions, severity_assessment, 
                emergency_info, language, cursor
            )
            
            # Log consultation for offline tracking
            self._log_consultation(user_query, detected_symptoms, guidance, severity_assessment, cursor)
            
            return guidance
            
        except Exception as e:
            return {
                "error": f"Offline guidance system error: {e}",
                "fallback_advice": "Please seek medical attention if symptoms persist or worsen.",
                "emergency_contact": "Call 108 for emergencies"
            }
        finally:
            conn.close()
    
    def _extract_symptoms_from_text(self, text: str, cursor) -> List[str]:
        """Extract symptoms mentioned in user query"""
        cursor.execute("SELECT symptom FROM symptoms")
        all_symptoms = [row[0].lower() for row in cursor.fetchall()]
        
        detected = []
        for symptom in all_symptoms:
            if symptom in text or any(word in text for word in symptom.split()):
                detected.append(symptom)
        
        return detected
    
    def _find_matching_conditions(self, symptoms: List[str], cursor) -> List[Dict]:
        """Find medical conditions that match detected symptoms"""
        matching_conditions = []
        
        cursor.execute("SELECT * FROM conditions")
        all_conditions = cursor.fetchall()
        
        for condition in all_conditions:
            condition_symptoms = json.loads(condition[2])  # symptoms column
            symptom_matches = sum(1 for symptom in symptoms 
                                if any(cs in symptom or symptom in cs 
                                      for cs in condition_symptoms))
            
            if symptom_matches > 0:
                matching_conditions.append({
                    'name': condition[1],
                    'symptoms': condition_symptoms,
                    'severity': condition[3],
                    'category': condition[4],
                    'description': condition[5],
                    'home_treatment': condition[6],
                    'when_to_see_doctor': condition[7],
                    'emergency_signs': json.loads(condition[8]),
                    'prevention': condition[9],
                    'match_score': symptom_matches / len(condition_symptoms)
                })
        
        # Sort by match score
        matching_conditions.sort(key=lambda x: x['match_score'], reverse=True)
        return matching_conditions[:3]  # Top 3 matches
    
    def _assess_severity(self, symptoms: List[str], conditions: List[Dict], cursor) -> Dict:
        """Assess severity of symptoms and check for emergency indicators"""
        max_severity = "low"
        emergency_flags = []
        emergency_type = None
        
        # Check against emergency protocols
        cursor.execute("SELECT emergency_type, immediate_action FROM emergency_protocols")
        emergency_protocols = cursor.fetchall()
        
        for protocol in emergency_protocols:
            emergency_keywords = protocol[0].lower().split()
            if any(keyword in ' '.join(symptoms) for keyword in emergency_keywords):
                emergency_flags.append(protocol[0])
                emergency_type = protocol[0]
        
        # Check condition severity
        for condition in conditions:
            if condition['severity'] == 'emergency':
                max_severity = 'emergency'
                emergency_type = condition['name']
            elif condition['severity'] == 'high' and max_severity != 'emergency':
                max_severity = 'high'
            elif condition['severity'] == 'medium' and max_severity not in ['high', 'emergency']:
                max_severity = 'medium'
        
        return {
            'severity': max_severity,
            'is_emergency': max_severity == 'emergency' or len(emergency_flags) > 0,
            'emergency_type': emergency_type,
            'emergency_flags': emergency_flags,
            'urgency': self._get_urgency_level(max_severity)
        }
    
    def _get_emergency_protocols(self, emergency_type: str, cursor) -> Optional[Dict]:
        """Get emergency protocols for specific emergency type"""
        cursor.execute(
            "SELECT * FROM emergency_protocols WHERE emergency_type = ?", 
            (emergency_type,)
        )
        protocol = cursor.fetchone()
        
        if protocol:
            return {
                'emergency_type': protocol[1],
                'immediate_action': protocol[2],
                'step_by_step_guide': json.loads(protocol[3]),
                'what_not_to_do': json.loads(protocol[4]),
                'call_emergency': protocol[5],
                'severity_assessment': protocol[6]
            }
        return {}
    
    def _generate_comprehensive_guidance(self, symptoms: List[str], conditions: List[Dict], 
                                       severity: Dict, emergency_info: Dict, 
                                       language: str, cursor) -> Dict:
        """Generate comprehensive health guidance"""
        
        if severity['is_emergency']:
            return self._generate_emergency_guidance(emergency_info, language)
        
        # Generate regular guidance
        primary_condition = conditions[0] if conditions else None
        
        guidance_text = ""
        if primary_condition:
            guidance_text = f"Based on your symptoms, you may have {primary_condition['name']}. "
            guidance_text += f"{primary_condition['description']} "
            
            if primary_condition['home_treatment']:
                guidance_text += f"Home care: {primary_condition['home_treatment']} "
            
            guidance_text += f"See a doctor if: {primary_condition['when_to_see_doctor']}"
        else:
            guidance_text = "Your symptoms require medical evaluation. Please monitor closely."
        
        # Get local resources
        local_resources = self._get_local_resources(cursor)
        
        return {
            'guidance': guidance_text,
            'detected_symptoms': symptoms,
            'possible_conditions': [c['name'] for c in conditions[:2]],
            'severity': severity['severity'],
            'urgency': severity['urgency'],
            'home_treatment': primary_condition['home_treatment'] if primary_condition else None,
            'when_to_see_doctor': primary_condition['when_to_see_doctor'] if primary_condition else "If symptoms persist or worsen",
            'prevention': primary_condition['prevention'] if primary_condition else None,
            'local_resources': local_resources,
            'emergency_contact': '108 (Emergency Services)',
            'mode': 'offline',
            'language': language
        }
    
    def _generate_emergency_guidance(self, emergency_info: Dict, language: str) -> Dict:
        """Generate emergency-specific guidance"""
        return {
            'guidance': f"⚠️ EMERGENCY: {emergency_info['immediate_action']}",
            'emergency': True,
            'emergency_type': emergency_info['emergency_type'],
            'immediate_action': emergency_info['immediate_action'],
            'step_by_step': emergency_info['step_by_step_guide'],
            'what_not_to_do': emergency_info['what_not_to_do'],
            'emergency_contact': emergency_info['call_emergency'],
            'severity': 'emergency',
            'urgency': 'immediate',
            'mode': 'offline_emergency',
            'language': language
        }
    
    def _get_local_resources(self, cursor) -> List[Dict]:
        """Get local healthcare resources"""
        cursor.execute("""
            SELECT resource_type, name, location, contact, services, 
                   emergency_available, distance_km, availability
            FROM local_resources 
            ORDER BY emergency_available DESC, distance_km ASC
            LIMIT 5
        """)
        
        resources = []
        for row in cursor.fetchall():
            resources.append({
                'type': row[0],
                'name': row[1],
                'location': row[2],
                'contact': row[3],
                'services': json.loads(row[4]) if row[4] else [],
                'emergency_available': bool(row[5]),
                'distance': f"{row[6]} km" if row[6] else "Unknown",
                'availability': row[7]
            })
        
        return resources
    
    def _get_urgency_level(self, severity: str) -> str:
        """Convert severity to urgency level"""
        urgency_map = {
            'emergency': 'immediate',
            'high': 'urgent',
            'medium': 'monitor closely',
            'low': 'routine care'
        }
        return urgency_map.get(severity, 'monitor')
    
    def _get_general_health_advice(self, language: str) -> Dict:
        """Provide general health advice when no specific symptoms detected"""
        return {
            'guidance': 'For general health concerns, monitor symptoms and seek medical advice if needed.',
            'general_advice': [
                'Stay hydrated',
                'Get adequate rest', 
                'Maintain good hygiene',
                'Monitor symptoms',
                'Seek medical help if symptoms worsen'
            ],
            'emergency_contact': '108 (Emergency Services)',
            'mode': 'offline_general',
            'language': language
        }
    
    def _log_consultation(self, query: str, symptoms: List[str], guidance: Dict, 
                         severity: Dict, cursor):
        """Log consultation for offline tracking"""
        consultation_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO consultations 
            (id, user_query, detected_language, symptoms_detected, 
             severity_assessment, guidance_provided, emergency_flag, mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            consultation_id, query, guidance.get('language', 'unknown'),
            json.dumps(symptoms), severity['severity'],
            json.dumps(guidance), severity['is_emergency'], 'offline'
        ))
    
    def get_emergency_contacts(self, region: str = "all") -> List[Dict]:
        """Get emergency contact information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT name, contact, services, availability 
                FROM local_resources 
                WHERE emergency_available = 1 AND (region = ? OR region = 'all')
                ORDER BY resource_type
            """, (region,))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'name': row[0],
                    'contact': row[1],
                    'services': json.loads(row[2]) if row[2] else [],
                    'availability': row[3]
                })
            
            return contacts
        finally:
            conn.close()

# Initialize global database instance
db = OfflineHealthDatabase()

# Legacy function for backward compatibility
def get_local_guidance(symptom: str) -> str:
    """Legacy function - use db.get_offline_health_guidance() instead"""
    result = db.get_offline_health_guidance(symptom)
    return result.get('guidance', 'No guidance available')

# Additional helper functions for the main application
def init_db():
    """Initialize the database - called from main app"""
    global db
    db = OfflineHealthDatabase()
    return True

def get_user_profile(user_id: str) -> Dict:
    """Placeholder for user profile functionality"""
    return {"user_id": user_id, "profile": "basic_user"}