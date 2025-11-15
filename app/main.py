"""
Sahaaya Universal Health Guidance System - Version 1.2
Intelligent online/offline switching for universal urban/rural healthcare access
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import os

# Import enhanced modules
# Temporarily commenting out imports that require model downloads for testing
# from app.stt_multilingual import transcribe_audio
# from app.nlp import get_health_guidance  
# from app.tts import generate_multilingual_audio
from app.db import db, init_db
# Temporarily commenting out connectivity module due to import dependencies
# from app.connectivity import (
#     connectivity_manager, 
#     check_internet_connectivity, 
#     get_connection_status, 
#     get_system_mode,
#     get_mode_recommendation
# )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI with enhanced metadata
app = FastAPI(
    title="Sahaaya Universal Health Guidance System",
    description="Intelligent health guidance with automatic online/offline switching for urban and rural areas",
    version="1.2.0"
)

# Mount static files for frontend
frontend_directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_directory):
    app.mount("/static", StaticFiles(directory=frontend_directory), name="static")
    
    # Serve frontend at root
    @app.get("/app")
    async def serve_frontend():
        """Serve the frontend application"""
        return FileResponse(os.path.join(frontend_directory, "index.html"))
    
    @app.get("/manifest.json")
    async def serve_manifest():
        """Serve PWA manifest"""
        return FileResponse(os.path.join(frontend_directory, "manifest.json"))
    
    @app.get("/sw.js")
    async def serve_service_worker():
        """Serve service worker"""
        return FileResponse(os.path.join(frontend_directory, "sw.js"))

# Pydantic models for request/response
class HealthQuery(BaseModel):
    text: str
    language: Optional[str] = "en"
    location: Optional[str] = None
    user_id: Optional[str] = None

class AudioQuery(BaseModel):
    audio_file: str
    language: Optional[str] = None
    location: Optional[str] = None
    user_id: Optional[str] = None

class EmergencyQuery(BaseModel):
    emergency_type: str
    location: Optional[str] = None
    language: Optional[str] = "en"

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup"""
    try:
        init_db()
        logger.info("✅ Sahaaya Universal Health System started successfully")
        logger.info("🌍 Supporting both urban (online) and rural (offline) access")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.get("/")
def home():
    """Enhanced home endpoint with system status"""
    connectivity = get_connection_status()
    
    return {
        "message": "Sahaaya Universal Health Guidance System - Version 1.2",
        "status": "operational",
        "connectivity": {
            "internet_available": connectivity["internet_available"],
            "recommended_mode": connectivity["recommendation"]["mode"]
        },
        "capabilities": {
            "urban_support": True,
            "rural_support": True,
            "emergency_protocols": True,
            "multilingual": True,
            "offline_database": True
        },
        "supported_languages": ["en", "hi", "te", "ta", "bn"],
        "version": "1.2.0"
    }

@app.get("/connectivity-status")
def get_connectivity_status():
    """Get detailed connectivity status and system capabilities"""
    connectivity_info = connectivity_manager.get_system_mode_info()
    
    return {
        "connectivity": connectivity_info["connectivity_status"],
        "recommended_mode": connectivity_info["recommended_mode"],
        "system_capabilities": connectivity_info["system_capabilities"],
        "universal_access": True,
        "mode_descriptions": {
            "hybrid": "AI-enhanced processing with offline backup (Urban areas)",
            "offline": "Complete offline functionality (Rural areas)",
            "online": "Full AI capabilities with real-time data"
        }
    }

@app.post("/smart-process")
def smart_process_query(query: HealthQuery, background_tasks: BackgroundTasks):
    """
    Intelligent processing that automatically chooses best mode based on connectivity.
    Works seamlessly in urban (online) and rural (offline) environments.
    """
    try:
        # Get current connectivity and mode recommendation
        connectivity = get_connection_status()
        is_online = connectivity["internet_available"]
        recommended_mode = connectivity["recommendation"]["mode"]
        
        logger.info(f"Processing query in {recommended_mode} mode (online: {is_online})")
        
        if recommended_mode == "hybrid" and is_online:
            # Urban scenario: AI + offline enhancement
            return process_hybrid_mode(query)
        elif recommended_mode == "offline" or not is_online:
            # Rural scenario: Complete offline functionality
            return process_offline_mode(query)
        else:
            # Fallback: Pure offline mode
            return process_offline_mode(query)
            
    except Exception as e:
        logger.error(f"Smart processing error: {e}")
        # Fallback to offline mode on any error
        return process_offline_mode(query)

@app.post("/offline-guidance")
def get_offline_guidance(query: HealthQuery):
    """
    Complete offline health guidance using local database.
    Designed specifically for rural areas without internet connectivity.
    """
    try:
        # Use offline database for guidance
        guidance = db.get_offline_health_guidance(query.text, query.language)
        
        # Add metadata for rural context
        guidance.update({
            "processing_mode": "offline",
            "internet_required": False,
            "suitable_for": ["rural", "remote", "emergency"],
            "data_source": "local_database",
            "timestamp": connectivity_manager.last_check_time
        })
        
        return guidance
        
    except Exception as e:
        logger.error(f"Offline guidance error: {e}")
        raise HTTPException(status_code=500, detail=f"Offline guidance failed: {e}")

@app.post("/emergency-protocol")
def get_emergency_protocol(emergency: EmergencyQuery):
    """
    Emergency response protocols for critical situations.
    Works entirely offline for rural emergency scenarios.
    """
    try:
        # Get emergency protocols from offline database
        emergency_contacts = db.get_emergency_contacts(emergency.location or "all")
        
        # Get specific emergency guidance
        if emergency.emergency_type:
            guidance = db.get_offline_health_guidance(
                f"emergency {emergency.emergency_type}", 
                emergency.language
            )
        else:
            guidance = {
                "guidance": "Call emergency services immediately",
                "emergency_contact": "108 (Emergency Services)",
                "immediate_action": "Assess situation and call for help"
            }
        
        return {
            "emergency_guidance": guidance,
            "emergency_contacts": emergency_contacts,
            "immediate_actions": [
                "Ensure scene safety",
                "Call emergency services (108)",
                "Provide basic first aid if trained",
                "Stay with the person",
                "Follow dispatcher instructions"
            ],
            "processing_mode": "offline_emergency",
            "language": emergency.language
        }
        
    except Exception as e:
        logger.error(f"Emergency protocol error: {e}")
        # Return basic emergency info even if database fails
        return {
            "emergency_guidance": {
                "guidance": "Call emergency services immediately",
                "emergency_contact": "108",
                "immediate_action": "Get professional help now"
            },
            "emergency_contacts": [
                {"name": "Emergency Services", "contact": "108", "availability": "24/7"}
            ]
        }

@app.post("/process")
def process_audio_query(query: AudioQuery):
    """
    Enhanced audio processing with intelligent mode selection.
    Legacy endpoint with new universal access capabilities.
    """
    try:
        # Check connectivity for mode selection
        is_online = check_internet_connectivity()
        
        # Transcribe audio (works with or without internet based on available models)
        try:
            transcription_result = transcribe_audio(query.audio_file, query.language)
            
            if not transcription_result.get("success", True):
                return {"error": "Audio transcription failed", "details": transcription_result.get("error")}
                
            text = transcription_result["text"] if isinstance(transcription_result, dict) else transcription_result
            detected_language = transcription_result.get("language", "unknown") if isinstance(transcription_result, dict) else "unknown"
            
        except Exception as audio_error:
            logger.warning(f"Audio transcription failed: {audio_error}")
            # Fallback for rural areas: ask for text input
            return {
                "error": "Audio processing unavailable",
                "message": "Please use text input for health guidance",
                "fallback_endpoint": "/smart-process",
                "audio_error": str(audio_error)
            }
        
        # Process the transcribed text
        health_query = HealthQuery(text=text, language=detected_language, location=query.location)
        guidance_result = smart_process_query(health_query, BackgroundTasks())
        
        # Try to generate audio response (if possible)
        try:
            if is_online:
                guidance_text = guidance_result.get("guidance", "")
                audio_result = generate_multilingual_audio(guidance_text, detected_language)
            else:
                audio_result = {"message": "Audio generation requires internet connectivity"}
        except Exception as tts_error:
            logger.warning(f"Audio generation failed: {tts_error}")
            audio_result = {"error": "Audio response unavailable", "details": str(tts_error)}
        
        return {
            "input_text": text,
            "detected_language": detected_language,
            "guidance": guidance_result,
            "audio": audio_result,
            "processing_mode": "hybrid" if is_online else "offline"
        }
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {e}")

def process_hybrid_mode(query: HealthQuery) -> Dict:
    """
    Process query in hybrid mode (urban areas with internet).
    Uses AI enhancement with offline database backup.
    """
    try:
        # Try AI-enhanced processing first
        ai_guidance = get_health_guidance(query.text, query.language)
        
        # Enhance with offline database information
        offline_guidance = db.get_offline_health_guidance(query.text, query.language)
        
        # Combine AI and offline insights
        combined_guidance = {
            "guidance": ai_guidance.get("guidance", offline_guidance.get("guidance", "")),
            "ai_analysis": ai_guidance,
            "offline_enhancement": {
                "local_resources": offline_guidance.get("local_resources", []),
                "emergency_protocols": offline_guidance.get("emergency_contact", "108"),
                "severity_assessment": offline_guidance.get("severity", "unknown")
            },
            "processing_mode": "hybrid_ai_offline",
            "internet_available": True,
            "confidence": "high",
            "data_sources": ["ai_analysis", "local_database"],
            "suitable_for": ["urban", "hospitals", "telemedicine"]
        }
        
        return combined_guidance
        
    except Exception as e:
        logger.warning(f"Hybrid mode failed, falling back to offline: {e}")
        # Fallback to offline mode
        return process_offline_mode(query)

def process_offline_mode(query: HealthQuery) -> Dict:
    """
    Process query in complete offline mode (rural areas without internet).
    Uses comprehensive local database for health guidance.
    """
    try:
        # Use offline database exclusively
        guidance = db.get_offline_health_guidance(query.text, query.language)
        
        # Add rural-specific enhancements
        guidance.update({
            "processing_mode": "offline",
            "internet_required": False,
            "rural_optimized": True,
            "local_emergency_info": db.get_emergency_contacts(),
            "offline_capabilities": [
                "symptom_analysis",
                "emergency_protocols", 
                "local_resources",
                "medication_info",
                "preventive_care_advice"
            ]
        })
        
        return guidance
        
    except Exception as e:
        logger.error(f"Offline processing error: {e}")
        # Ultra-basic fallback
        return {
            "guidance": "Unable to process query. Please seek medical attention if symptoms persist.",
            "emergency_contact": "108",
            "processing_mode": "basic_fallback",
            "error": str(e)
        }

@app.get("/health")
def health_check():
    """System health check endpoint"""
    try:
        # Test database connectivity
        db_status = "operational"
        try:
            db.get_emergency_contacts()
        except Exception:
            db_status = "error"
        
        # Test connectivity manager
        connectivity_status = get_connection_status()
        
        return {
            "status": "healthy",
            "database": db_status,
            "connectivity_manager": "operational",
            "current_mode": get_system_mode(),
            "internet_available": connectivity_status["internet_available"],
            "version": "1.2.0"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "version": "1.2.0"
        }


