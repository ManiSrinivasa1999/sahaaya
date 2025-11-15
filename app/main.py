from fastapi import FastAPI, HTTPException
#from app.stt import transcribe_audio
from app.stt_multilingual import transcribe_audio
from app.nlp import get_health_guidance
#from app.tts import generate_audio
from app.tts import generate_multilingual_audio
from app.db import get_offline_health_guidance, offline_db
from typing import Optional, Dict
import logging
import requests
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sahaaya Health Guidance API",
    description="Universal AI-powered health guidance system with intelligent online/offline support for urban and rural communities",
    version="2.0.0"
)

# Internet connectivity checker
def check_internet_connectivity(timeout: int = 5) -> bool:
    """
    Check if internet is available by testing connectivity to reliable servers
    
    Args:
        timeout: Maximum time to wait for connection
    
    Returns:
        bool: True if internet is available, False otherwise
    """
    test_urls = [
        "https://8.8.8.8",  # Google DNS
        "https://1.1.1.1",  # Cloudflare DNS  
        "https://www.google.com",
        "https://httpbin.org/get"  # Simple HTTP test
    ]
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=timeout)
            if response.status_code < 400:
                logger.info("Internet connectivity confirmed")
                return True
        except requests.RequestException:
            continue
    
    logger.warning("No internet connectivity detected")
    return False

def get_system_mode() -> Dict:
    """
    Determine the optimal system operating mode based on connectivity and capabilities
    
    Returns:
        Dict with mode information and capabilities
    """
    internet_available = check_internet_connectivity()
    
    mode_info = {
        "internet_available": internet_available,
        "recommended_mode": "hybrid" if internet_available else "offline",
        "ai_capabilities": internet_available,
        "offline_capabilities": True,
        "emergency_protocols": True,
        "local_resources": True,
        "multilingual_support": True
    }
    
    if internet_available:
        mode_info.update({
            "features": [
                "AI-enhanced medical analysis",
                "Real-time medical databases",
                "Advanced symptom analysis", 
                "Latest medical guidelines",
                "Offline database enhancement"
            ],
            "suitable_for": ["Urban areas", "Rural areas with internet", "Telemedicine", "Hospitals"]
        })
    else:
        mode_info.update({
            "features": [
                "Comprehensive offline medical database",
                "Emergency response protocols",
                "Local health resource directory", 
                "Essential medication information",
                "Multi-language support"
            ],
            "suitable_for": ["Rural areas", "Remote locations", "Emergency situations", "Network outages"]
        })
    
    return mode_info

def get_intelligent_health_guidance(user_text: str, detected_language: str = "en", 
                                  location: str = None, force_mode: str = None) -> Dict:
    """
    Intelligent health guidance that automatically chooses best available method
    
    Args:
        user_text: User's symptom description
        detected_language: Language detected from speech
        location: User's location for local resources
        force_mode: Override automatic mode selection ("online", "offline", "hybrid")
    
    Returns:
        Comprehensive health guidance with source information
    """
    system_mode = get_system_mode()
    
    # Determine processing mode
    if force_mode:
        processing_mode = force_mode
    elif system_mode["internet_available"]:
        processing_mode = "hybrid"  # Best of both worlds
    else:
        processing_mode = "offline"
    
    logger.info(f"Processing mode: {processing_mode}, Internet: {system_mode['internet_available']}")
    
    guidance_result = None
    error_info = None
    
    try:
        if processing_mode in ["online", "hybrid"]:
            # Try AI-enhanced analysis first
            try:
                logger.info(f"Attempting AI analysis for: {user_text[:50]}...")
                ai_start_time = time.time()
                
                guidance_result = get_health_guidance(user_text, detected_language)
                ai_processing_time = time.time() - ai_start_time
                
                if guidance_result:
                    guidance_result["processing_info"] = {
                        "source": "ai_enhanced",
                        "processing_time": ai_processing_time,
                        "internet_required": True,
                        "confidence": "high"
                    }
                    
                    # Enhance with offline context (hybrid approach)
                    if processing_mode == "hybrid":
                        offline_context = get_offline_health_guidance(user_text, detected_language, location)
                        
                        # Merge offline enhancements
                        if offline_context.get("local_health_resources"):
                            guidance_result["local_health_resources"] = offline_context["local_health_resources"]
                        if offline_context.get("emergency_protocol"):
                            guidance_result["emergency_protocol"] = offline_context["emergency_protocol"]
                        if offline_context.get("home_remedies"):
                            guidance_result["home_remedies"] = offline_context["home_remedies"]
                        
                        guidance_result["processing_info"]["enhanced_with"] = "offline_database"
                        guidance_result["processing_info"]["source"] = "hybrid_ai_offline"
                    
                    logger.info(f"AI guidance successful in {ai_processing_time:.2f}s")
                
            except Exception as ai_error:
                logger.warning(f"AI guidance failed: {ai_error}")
                error_info = {"ai_error": str(ai_error)}
                guidance_result = None
        
        # Fallback to offline database (or primary for offline mode)
        if guidance_result is None or processing_mode == "offline":
            logger.info(f"Using offline database for: {user_text[:50]}...")
            offline_start_time = time.time()
            
            guidance_result = get_offline_health_guidance(user_text, detected_language, location)
            offline_processing_time = time.time() - offline_start_time
            
            if guidance_result:
                guidance_result["processing_info"] = {
                    "source": "offline_database",
                    "processing_time": offline_processing_time,
                    "internet_required": False,
                    "confidence": "high" if guidance_result.get("detected_symptoms") else "medium"
                }
                
                if error_info:
                    guidance_result["processing_info"]["fallback_reason"] = error_info
                
                logger.info(f"Offline guidance successful in {offline_processing_time:.2f}s")
        
        # Final validation and enhancement
        if guidance_result:
            guidance_result.update({
                "system_mode": system_mode,
                "processing_mode": processing_mode,
                "universal_access": True,
                "suitable_for": ["urban", "rural", "remote"],
                "timestamp": time.time()
            })
            
            # Add connectivity status
            if not system_mode["internet_available"]:
                guidance_result["offline_notice"] = "Operating in offline mode. All essential medical guidance available locally."
            
            return guidance_result
        
        # If everything fails, provide emergency fallback
        raise RuntimeError("All guidance systems failed")
        
    except Exception as e:
        logger.error(f"Critical error in guidance system: {e}")
        
        # Emergency fallback with basic offline protocols
        return {
            "guidance": "System error occurred. For medical emergencies, call 108 immediately. Consult nearest healthcare facility.",
            "detected_symptoms": [],
            "severity": "unknown",
            "urgency": "consult_doctor",
            "processing_info": {
                "source": "emergency_fallback",
                "error": str(e),
                "internet_required": False
            },
            "emergency_contacts": {
                "national": "108",
                "police": "100", 
                "fire": "101"
            },
            "system_mode": system_mode,
            "universal_access": True
        }


@app.get("/")
def home():
    """Health check endpoint with system capabilities"""
    try:
        # Check system status
        system_mode = get_system_mode()
        db_status = offline_db.get_usage_statistics()
        
        return {
            "message": "Sahaaya Universal Health Guidance System",
            "version": "2.0.0",
            "system_status": "operational",
            "connectivity": system_mode,
            "features": {
                "universal_access": True,
                "intelligent_mode_switching": True,
                "multilingual_stt": ["Telugu", "Hindi", "English", "Tamil", "Bengali"],
                "ai_medical_nlp": system_mode["internet_available"],
                "offline_medical_database": True,
                "emergency_protocols": True,
                "local_health_resources": True,
                "multilingual_tts": True
            },
            "suitable_environments": {
                "urban_areas": "Full AI + offline capabilities",
                "rural_with_internet": "Hybrid AI + local resources", 
                "rural_without_internet": "Comprehensive offline database",
                "emergency_situations": "Always available protocols"
            },
            "database_statistics": {
                "total_interactions": db_status.get("total_interactions", 0),
                "languages_supported": db_status.get("language_distribution", {}),
                "database_status": db_status.get("database_status", "operational")
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "message": "Sahaaya Health Guidance System", 
            "status": "partial",
            "error": "Some features may be limited"
        }


@app.post("/process")
def process_health_query(audio_file: str, language: Optional[str] = None, 
                        location: Optional[str] = None, force_mode: Optional[str] = None):
    """
    Universal health guidance processor with intelligent online/offline switching
    
    Args:
        audio_file: Path to audio file containing user's health query
        language: Optional language specification (auto-detected if not provided)
        location: Optional user location for local health resource recommendations
        force_mode: Optional mode override ("online", "offline", "hybrid")
    
    Returns:
        Comprehensive health guidance optimized for user's connectivity and location
    """
    try:
        # Step 1: Audio Processing
        transcription_result = _process_audio_input(audio_file, language)
        if "error" in transcription_result:
            return transcription_result
        
        user_text = transcription_result["text"]
        detected_language = transcription_result["language"]
        
        # Step 2: Intelligent Health Guidance 
        guidance_result = get_intelligent_health_guidance(
            user_text, detected_language, location, force_mode
        )
        
        # Step 3: Audio Response Generation
        audio_result = _generate_audio_response(guidance_result, detected_language)
        
        # Step 4: Compile Final Response
        return _compile_final_response(
            transcription_result, guidance_result, audio_result, location
        )
        
    except Exception as e:
        logger.error(f"Critical error in process_health_query: {e}")
        return _emergency_fallback_response(str(e))

def _process_audio_input(audio_file: str, language: Optional[str]) -> Dict:
    """Process audio input and handle transcription errors"""
    try:
        transcription_result = transcribe_audio(audio_file, language)
        
        if not transcription_result.get("success", True):
            return {
                "error": "Audio transcription failed",
                "details": transcription_result.get("error"),
                "suggestion": "Please check audio quality or try again"
            }
        
        return {
            "text": transcription_result["text"] if isinstance(transcription_result, dict) else transcription_result,
            "language": transcription_result.get("language", "unknown") if isinstance(transcription_result, dict) else "unknown",
            "confidence": transcription_result.get("confidence", "medium") if isinstance(transcription_result, dict) else "medium"
        }
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        return {"error": f"Audio processing failed: {str(e)}"}

def _generate_audio_response(guidance_result: Dict, language: str) -> Dict:
    """Generate audio response with fallback handling"""
    try:
        guidance_text = guidance_result.get("guidance", "")
        if not guidance_text:
            return {"error": "No guidance text to convert to audio"}
        
        audio_result = generate_multilingual_audio(
            guidance_text, language, include_fallbacks=True
        )
        
        return audio_result
        
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        return {"error": f"Audio generation failed: {str(e)}"}

def _compile_final_response(transcription: Dict, guidance: Dict, audio: Dict, location: str) -> Dict:
    """Compile comprehensive final response"""
    system_mode = guidance.get("system_mode", {})
    processing_info = guidance.get("processing_info", {})
    
    response = {
        "input_text": transcription["text"],
        "detected_language": transcription["language"],
        "guidance": guidance,
        "audio": audio,
        "system_info": {
            "processing_mode": processing_info.get("source", "unknown"),
            "internet_available": system_mode.get("internet_available", False),
            "processing_time": processing_info.get("processing_time", 0),
            "universal_access": True
        }
    }
    
    # Add location context if provided
    if location:
        response["location_context"] = {
            "user_location": location,
            "local_resources_included": bool(guidance.get("local_health_resources")),
            "emergency_protocols_localized": bool(guidance.get("emergency_protocol"))
        }
    
    # Add mode-specific information
    if system_mode.get("internet_available"):
        response["features"] = {
            "ai_analysis": processing_info.get("source") in ["ai_enhanced", "hybrid_ai_offline"],
            "real_time_data": True,
            "offline_enhancement": processing_info.get("enhanced_with") == "offline_database",
            "suitable_for": ["urban", "rural_with_internet", "hospitals", "telemedicine"]
        }
    else:
        response["features"] = {
            "offline_database": True,
            "emergency_protocols": True,
            "local_resources": True,
            "no_internet_required": True,
            "suitable_for": ["rural", "remote", "emergency", "network_outages"]
        }
    
    return response

def _emergency_fallback_response(error_message: str) -> Dict:
    """Emergency fallback when all systems fail"""
    return {
        "error": "System temporarily unavailable",
        "emergency_guidance": {
            "en": "For medical emergencies, call 108 immediately. Consult nearest healthcare facility.",
            "hi": "चिकित्सा आपातकाल के लिए तुरंत 108 कॉल करें। निकटतम स्वास्थ्य सुविधा से संपर्क करें।",
            "te": "వైద్య అత్యవసర పరిస్థితుల కోసం వెంటనే 108కి కాల్ చేయండి। సమీప వైద్య సౌకర్యాన్ని సంప్రదించండి।"
        },
        "emergency_contacts": {
            "national_emergency": "108",
            "police": "100",
            "fire": "101",
            "women_helpline": "1091",
            "child_helpline": "1098"
        },
        "system_info": {
            "mode": "emergency_fallback",
            "error": error_message,
            "universal_access": True
        }
    }

@app.get("/connectivity-status")
def check_connectivity_status():
    """Check current system connectivity and capabilities"""
    try:
        system_mode = get_system_mode()
        return {
            "connectivity_check": system_mode,
            "automatic_switching": {
                "enabled": True,
                "online_mode": {
                    "description": "AI-enhanced analysis with offline database enhancement",
                    "features": ["Advanced symptom analysis", "Real-time medical data", "Local resource integration"],
                    "suitable_for": ["Urban areas", "Rural with internet", "Hospitals"]
                },
                "offline_mode": {
                    "description": "Comprehensive offline medical database",
                    "features": ["Essential medical knowledge", "Emergency protocols", "Local resources", "Medication info"],
                    "suitable_for": ["Rural areas", "Remote locations", "Network outages"]
                },
                "hybrid_mode": {
                    "description": "Best of both AI and offline capabilities",
                    "features": ["AI analysis enhanced with local context", "Fallback protection", "Universal coverage"],
                    "suitable_for": ["All environments", "Variable connectivity", "Maximum reliability"]
                }
            },
            "intelligent_features": {
                "automatic_internet_detection": True,
                "seamless_mode_switching": True,
                "no_user_intervention_required": True,
                "universal_accessibility": True
            }
        }
    except Exception as e:
        logger.error(f"Connectivity status error: {e}")
        return {"error": "Connectivity status check failed"}

@app.post("/smart-process")
def smart_health_guidance(user_text: str, language: str = "en", location: Optional[str] = None):
    """
    Text-based health guidance with intelligent online/offline processing
    Automatically detects connectivity and uses best available method
    """
    try:
        guidance_result = get_intelligent_health_guidance(user_text, language, location)
        
        return {
            "user_input": user_text,
            "language": language,
            "guidance": guidance_result,
            "intelligent_processing": True,
            "universal_access": True,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Smart guidance error: {e}")
        return _emergency_fallback_response(str(e))
    }

@app.post("/offline-guidance")
def get_offline_guidance_only(user_text: str, language: str = "en", location: Optional[str] = None):
    """
    Get health guidance using only offline database (for rural areas without internet)
    
    Args:
        user_text: User's description of symptoms in text form
        language: Language code (te, hi, en, etc.)
        location: Optional location for local health resources
    """
    try:
        guidance_result = get_offline_health_guidance(user_text, language, location)
        
        return {
            "guidance": guidance_result,
            "mode": "offline_only",
            "internet_required": False,
            "timestamp": offline_db.get_usage_statistics().get("timestamp"),
            "disclaimer": "This guidance is from offline database. Consult healthcare professionals when possible."
        }
        
    except Exception as e:
        logger.error(f"Offline guidance error: {e}")
        return {
            "error": "Offline guidance unavailable",
            "emergency_advice": "Consult nearest healthcare facility or call 108 for emergencies",
            "mode": "error_fallback"
        }

@app.get("/emergency-protocols")
def get_emergency_protocols(language: str = "en"):
    """Get emergency medical protocols in specified language"""
    try:
        protocols = []
        emergency_conditions = ['heart_attack', 'stroke', 'severe_breathing_difficulty']
        
        for condition in emergency_conditions:
            protocol = offline_db.get_emergency_protocol(condition, language)
            if protocol:
                protocols.append(protocol)
        
        return {
            "emergency_protocols": protocols,
            "language": language,
            "emergency_contacts": {
                "national": "108",
                "police": "100", 
                "fire": "101",
                "women_helpline": "1091",
                "child_helpline": "1098"
            }
        }
        
    except Exception as e:
        logger.error(f"Emergency protocols error: {e}")
        return {"error": "Emergency protocols unavailable"}

@app.get("/local-health-resources")
def get_local_resources(resource_type: Optional[str] = None, emergency_only: bool = False):
    """Get local health resources and facilities"""
    try:
        resources = offline_db.get_local_health_resources(resource_type, emergency_only)
        return {
            "local_health_resources": resources,
            "total_resources": len(resources),
            "resource_type_filter": resource_type,
            "emergency_only": emergency_only
        }
        
    except Exception as e:
        logger.error(f"Local resources error: {e}")
        return {"error": "Local resources unavailable"}

@app.get("/medication-info/{medication_name}")
def get_medication_information(medication_name: str, language: str = "en"):
    """Get information about specific medications"""
    try:
        med_info = offline_db.get_medication_info(medication_name, language)
        
        if med_info:
            return {
                "medication_info": med_info,
                "language": language,
                "availability": "offline_database"
            }
        else:
            return {
                "error": f"Medication '{medication_name}' not found in database",
                "suggestion": "Consult pharmacist or healthcare provider"
            }
            
    except Exception as e:
        logger.error(f"Medication info error: {e}")
        return {"error": "Medication information unavailable"}

@app.get("/system-status")
def get_system_status():
    """Get comprehensive system status and statistics"""
    try:
        db_stats = offline_db.get_usage_statistics()
        
        return {
            "system_status": "operational",
            "database_statistics": db_stats,
            "features": {
                "multilingual_stt": True,
                "ai_medical_nlp": True, 
                "multilingual_tts": True,
                "offline_database": True,
                "emergency_protocols": True,
                "local_resources": True
            },
            "supported_languages": ["en", "hi", "te", "ta", "bn"],
            "offline_capabilities": {
                "symptom_analysis": True,
                "emergency_guidance": True,
                "medication_info": True,
                "local_resources": True,
                "user_interaction_logging": True
            }
        }
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {
            "system_status": "partial",
            "error": "Some features may be limited"
        }


