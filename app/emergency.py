"""
Emergency Response System for Rural and Urban Healthcare
Comprehensive life-saving protocols and emergency management
"""
from typing import Dict, List, Optional, Tuple
import json
import time
from enum import Enum

class EmergencyLevel(Enum):
    """Emergency severity levels"""
    LIFE_THREATENING = "life_threatening"
    URGENT = "urgent" 
    MODERATE = "moderate"
    NON_URGENT = "non_urgent"

class EmergencyType(Enum):
    """Types of medical emergencies"""
    CARDIAC = "cardiac"
    RESPIRATORY = "respiratory"
    TRAUMA = "trauma"
    NEUROLOGICAL = "neurological"
    ALLERGIC_REACTION = "allergic_reaction"
    POISONING = "poisoning"
    BURNS = "burns"
    BLEEDING = "bleeding"
    CHOKING = "choking"
    UNCONSCIOUS = "unconscious"

class EmergencyResponseSystem:
    """
    Comprehensive emergency response system for universal healthcare access.
    Designed to work offline in rural areas and enhanced online in urban areas.
    """
    
    def __init__(self):
        self.emergency_keywords = self._load_emergency_keywords()
        self.vital_signs_ranges = self._load_vital_signs_ranges()
    
    def _load_emergency_keywords(self) -> Dict[str, List[str]]:
        """Load emergency detection keywords in multiple languages"""
        return {
            'cardiac': {
                'en': ['chest pain', 'heart attack', 'cardiac arrest', 'heart stopped', 'crushing chest pain'],
                'hi': ['छाती में दर्द', 'दिल का दौरा', 'हृदयाघात', 'सीने में दर्द'],
                'te': ['గుండె నొప్పి', 'గుండెపोटు', 'హృదయ స్తంభన'],
                'ta': ['மார்பு வலி', 'மாரடைப்பு', 'இதய நிறுத்தம்'],
                'bn': ['বুকে ব্যথা', 'হার্ট অ্যাটাক', 'হৃদরোগ']
            },
            'respiratory': {
                'en': ['cant breathe', 'difficulty breathing', 'choking', 'suffocating', 'gasping'],
                'hi': ['सांस नहीं ले सकता', 'सांस लेने में कठিनाई', 'दम घुट रहा है'],
                'te': ['ఊపిరి రాలేదు', 'ఊపిరాడక', 'ఉక్కిరిబిక్కిరి'],
                'ta': ['மூச்சு வரவில்லை', 'மூச்சுத் திணறல்', 'மூச்சுவிடுவதில் சிரமம்'],
                'bn': ['শ্বাস নিতে পারছি না', 'শ্বাসকষ্ট', 'দম বন্ধ']
            },
            'unconscious': {
                'en': ['unconscious', 'passed out', 'not responding', 'fainted', 'collapsed'],
                'hi': ['बेहोश', 'गिर गया', 'होश नहीं है', 'बेसुध'],
                'te': ['స్పృహ లేదు', 'అపస్మారక', 'పడిపోయాడు'],
                'ta': ['மயக்கம்', 'விழுந்துவிட்டார்', 'சுயநினைவில்லை'],
                'bn': ['অজ্ঞান', 'পড়ে গেছে', 'হুঁশ নেই']
            },
            'bleeding': {
                'en': ['severe bleeding', 'blood loss', 'hemorrhage', 'bleeding heavily'],
                'hi': ['अधिक खून निकलना', 'खून बह रहा है', 'रक्तस्राव'],
                'te': ['రక్తస్రావం', 'చాలా రక్తం రావడం'],
                'ta': ['அதிக இரத்தப்போக்கு', 'ரத்தம் வெளியேறுதல்'],
                'bn': ['অতিরিক্ত রক্তক্ষরণ', 'রক্ত পড়া']
            },
            'burns': {
                'en': ['severe burns', 'burned', 'fire accident', 'scalding'],
                'hi': ['जलना', 'आग लगना', 'झुलसना'],
                'te': ['కాలిపోవడం', 'కమ్మడం'],
                'ta': ['தீக்காயம்', 'வெந்துபோவது'],
                'bn': ['পুড়ে যাওয়া', 'আগুন লাগা']
            },
            'poisoning': {
                'en': ['poisoning', 'overdose', 'toxic', 'swallowed poison'],
                'hi': ['जहर', 'विषाक्तता', 'नशीली दवा'],
                'te': ['విషం', 'విషప్రయోగం'],
                'ta': ['நஞ்சு', 'விஷம்'],
                'bn': ['বিষ', 'বিষক্রিয়া']
            }
        }
    
    def _load_vital_signs_ranges(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """Load normal vital signs ranges for emergency assessment"""
        return {
            'heart_rate': {
                'infant': (100, 160),
                'toddler': (90, 150),
                'preschool': (80, 140),
                'school_age': (70, 120),
                'adult': (60, 100),
                'elderly': (60, 100)
            },
            'blood_pressure_systolic': {
                'infant': (70, 100),
                'toddler': (80, 110),
                'preschool': (90, 110),
                'school_age': (90, 120),
                'adult': (90, 140),
                'elderly': (90, 150)
            },
            'respiratory_rate': {
                'infant': (30, 60),
                'toddler': (24, 40),
                'preschool': (22, 34),
                'school_age': (18, 30),
                'adult': (12, 20),
                'elderly': (12, 20)
            }
        }
    
    def assess_emergency_level(self, symptoms_text: str, language: str = "en") -> Dict:
        """
        Assess emergency level based on symptoms description.
        Critical for rural areas where professional help might be far away.
        """
        symptoms_lower = symptoms_text.lower()
        
        # Check for life-threatening keywords
        life_threatening_found = []
        emergency_types = []
        
        for emergency_type, lang_keywords in self.emergency_keywords.items():
            if language in lang_keywords:
                keywords = lang_keywords[language]
                for keyword in keywords:
                    if keyword in symptoms_lower:
                        life_threatening_found.append(keyword)
                        emergency_types.append(emergency_type)
        
        # Determine emergency level
        if life_threatening_found:
            emergency_level = EmergencyLevel.LIFE_THREATENING
            priority = "IMMEDIATE"
            action_needed = "Call 108 immediately"
        elif any(word in symptoms_lower for word in ['severe', 'intense', 'extreme', 'unbearable']):
            emergency_level = EmergencyLevel.URGENT
            priority = "URGENT"
            action_needed = "Seek immediate medical attention"
        elif any(word in symptoms_lower for word in ['pain', 'fever', 'bleeding', 'vomiting']):
            emergency_level = EmergencyLevel.MODERATE
            priority = "MODERATE"
            action_needed = "See doctor within 24 hours"
        else:
            emergency_level = EmergencyLevel.NON_URGENT
            priority = "ROUTINE"
            action_needed = "Monitor symptoms, see doctor if worsens"
        
        return {
            'emergency_level': emergency_level.value,
            'priority': priority,
            'emergency_types': list(set(emergency_types)),
            'keywords_found': life_threatening_found,
            'action_needed': action_needed,
            'call_emergency': emergency_level in [EmergencyLevel.LIFE_THREATENING, EmergencyLevel.URGENT],
            'assessment_time': time.time()
        }
    
    def get_immediate_response_protocol(self, emergency_type: str, language: str = "en") -> Dict:
        """
        Get immediate response protocols for specific emergency types.
        Optimized for scenarios where professional help is not immediately available.
        """
        protocols = {
            'cardiac': {
                'en': {
                    'immediate_action': 'Call 108 immediately. Keep person sitting upright.',
                    'steps': [
                        'Call emergency services (108/102)',
                        'Give aspirin if person conscious and not allergic',
                        'Keep person calm and sitting upright',
                        'Loosen tight clothing around neck and chest',
                        'Monitor breathing and pulse',
                        'Be ready to perform CPR if needed',
                        'Do not leave person alone'
                    ],
                    'warning_signs': [
                        'Severe chest pain or pressure',
                        'Pain spreading to arm, jaw, or back', 
                        'Shortness of breath',
                        'Sweating',
                        'Nausea or vomiting'
                    ],
                    'do_not_do': [
                        'Give water if unconscious',
                        'Give medication except aspirin',
                        'Let person walk or exert themselves'
                    ]
                }
            },
            'respiratory': {
                'en': {
                    'immediate_action': 'If choking, perform Heimlich maneuver. If breathing difficulty, call 108.',
                    'steps': [
                        'Check if airway is blocked',
                        'If choking: perform back blows and abdominal thrusts',
                        'If asthma: help use rescue inhaler',
                        'Keep person in upright position',
                        'Loosen tight clothing',
                        'Call 108 if breathing does not improve',
                        'Monitor consciousness level'
                    ],
                    'warning_signs': [
                        'Blue lips or fingernails',
                        'Inability to speak',
                        'Weak or absent breathing',
                        'Loss of consciousness'
                    ]
                }
            },
            'unconscious': {
                'en': {
                    'immediate_action': 'Check responsiveness. Call 108. Check breathing.',
                    'steps': [
                        'Check if person responds to voice or touch',
                        'Call 108 immediately',
                        'Check for breathing',
                        'Place in recovery position if breathing',
                        'Start CPR if not breathing',
                        'Clear airway of obvious obstructions',
                        'Monitor until help arrives'
                    ],
                    'warning_signs': [
                        'No response to stimuli',
                        'Abnormal breathing',
                        'No pulse',
                        'Blue coloration'
                    ]
                }
            },
            'bleeding': {
                'en': {
                    'immediate_action': 'Apply direct pressure to wound. Elevate if possible.',
                    'steps': [
                        'Apply direct pressure with clean cloth',
                        'Elevate injured area above heart if possible',
                        'Do not remove object if embedded',
                        'Apply additional bandages over soaked ones',
                        'Check for signs of shock',
                        'Call 108 for severe bleeding',
                        'Keep person warm'
                    ],
                    'warning_signs': [
                        'Spurting blood',
                        'Blood soaking through bandages',
                        'Signs of shock (pale, weak pulse)',
                        'Bleeding from multiple sites'
                    ]
                }
            }
        }
        
        return protocols.get(emergency_type, {}).get(language, {
            'immediate_action': 'Medical emergency detected. Call 108 immediately.',
            'steps': ['Call emergency services', 'Stay with the person', 'Follow dispatcher instructions'],
            'warning_signs': ['Worsening condition'],
            'do_not_do': ['Move person unnecessarily']
        })
    
    def get_rural_emergency_guidance(self, emergency_assessment: Dict, location: Optional[str] = None) -> Dict:
        """
        Specialized emergency guidance for rural areas where help might be far away.
        Includes extended first aid and stabilization techniques.
        """
        guidance = {
            'immediate_priorities': [
                'Ensure scene safety',
                'Call 108 emergency services',
                'Provide basic life support',
                'Prepare for transport'
            ],
            'extended_care_instructions': [],
            'transport_considerations': [],
            'communication_plan': []
        }
        
        if emergency_assessment['emergency_level'] == 'life_threatening':
            guidance['extended_care_instructions'] = [
                'Maintain airway, breathing, circulation (ABC)',
                'Control severe bleeding with pressure',
                'Prevent shock - keep warm, legs elevated',
                'Monitor vital signs every 5 minutes',
                'Be prepared to perform CPR',
                'Keep detailed record of condition changes'
            ]
            
            guidance['transport_considerations'] = [
                'Request helicopter ambulance if available',
                'Prepare stable surface for transport',
                'Gather all medications patient is taking',
                'Assign someone to guide ambulance to location',
                'Clear path for emergency vehicle access'
            ]
            
        guidance['communication_plan'] = [
            'Designate one person to stay on phone with 108',
            'Send someone to meet ambulance at main road',
            'Contact local healthcare facility to prepare',
            'Notify family members',
            'Document all actions taken'
        ]
        
        # Add location-specific resources
        if location:
            guidance['local_resources'] = self._get_location_emergency_resources(location)
        
        return guidance
    
    def _get_location_emergency_resources(self, location: str) -> List[Dict]:
        """Get emergency resources specific to location"""
        # This would ideally connect to a database of local resources
        return [
            {
                'type': 'emergency_services',
                'contact': '108',
                'description': 'National emergency number',
                'availability': '24/7'
            },
            {
                'type': 'ambulance', 
                'contact': '102',
                'description': 'Ambulance services',
                'availability': '24/7'
            },
            {
                'type': 'local_hospital',
                'contact': 'Varies by district',
                'description': 'District government hospital',
                'note': 'Contact through 108 for fastest routing'
            }
        ]
    
    def get_emergency_contact_hierarchy(self) -> List[Dict]:
        """
        Get prioritized list of emergency contacts.
        Critical for rural areas with limited communication options.
        """
        regional_languages = 'Regional languages'
        
        contacts = [
            {
                'priority': 1,
                'service': 'Emergency Services',
                'number': '108',
                'description': 'National emergency helpline',
                'when_to_call': 'Life-threatening emergencies',
                'languages': ['Hindi', 'English', regional_languages]
            },
            {
                'priority': 2,
                'service': 'Ambulance',
                'number': '102', 
                'description': 'Free ambulance service',
                'when_to_call': 'Medical transport needed',
                'languages': ['Hindi', 'English', regional_languages]
            },
            {
                'priority': 3,
                'service': 'Fire Emergency',
                'number': '101',
                'description': 'Fire and rescue',
                'when_to_call': 'Fire, accident rescue',
                'languages': ['Hindi', 'English', regional_languages]
            },
            {
                'priority': 4,
                'service': 'Police',
                'number': '100',
                'description': 'Police emergency',
                'when_to_call': 'Crime, security emergency',
                'languages': ['Hindi', 'English', regional_languages]
            },
            {
                'priority': 5,
                'service': 'Disaster Management',
                'number': '1078',
                'description': 'Disaster response',
                'when_to_call': 'Natural disasters, major incidents',
                'languages': ['Hindi', 'English']
            }
        ]
        
        return contacts
    
    def assess_vital_signs(self, vital_signs: Dict, age_group: str = "adult") -> Dict:
        """
        Assess if vital signs indicate emergency situation.
        Helpful for rural healthcare workers with basic training.
        """
        assessment = {
            'normal': [],
            'concerning': [],
            'critical': [],
            'overall_status': 'unknown'
        }
        
        ranges = self.vital_signs_ranges
        
        # Check heart rate
        if 'heart_rate' in vital_signs:
            hr = vital_signs['heart_rate']
            normal_range = ranges['heart_rate'].get(age_group, ranges['heart_rate']['adult'])
            
            if hr < normal_range[0] * 0.6 or hr > normal_range[1] * 1.5:
                assessment['critical'].append(f'Heart rate {hr} is critically abnormal')
            elif hr < normal_range[0] or hr > normal_range[1]:
                assessment['concerning'].append(f'Heart rate {hr} is outside normal range')
            else:
                assessment['normal'].append(f'Heart rate {hr} is normal')
        
        # Determine overall status
        if assessment['critical']:
            assessment['overall_status'] = 'critical'
        elif assessment['concerning']:
            assessment['overall_status'] = 'concerning'
        elif assessment['normal']:
            assessment['overall_status'] = 'normal'
        
        return assessment

# Global emergency response system instance
emergency_system = EmergencyResponseSystem()