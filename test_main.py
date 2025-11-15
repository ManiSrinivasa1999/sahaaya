"""
Sahaaya Universal Health Guidance System - Version 1.2 (Testing Mode)
Simplified version for testing frontend with offline database
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import os

# Import offline database and NLP for testing
from app.db import OfflineHealthDatabase
from app.nlp import get_health_guidance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI with enhanced metadata
app = FastAPI(
    title="Sahaaya Universal Health Guidance System (Testing Mode)",
    description="Testing version with offline database and frontend",
    version="1.2.0-test"
)

# Initialize offline database
offline_db = OfflineHealthDatabase()

# Mount static files for frontend
frontend_directory = os.path.join(os.path.dirname(__file__), "frontend")
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

class EmergencyQuery(BaseModel):
    emergency_type: str
    location: Optional[str] = None
    language: Optional[str] = "en"

@app.get("/")
def home():
    """Enhanced home endpoint with system status"""
    return {
        "message": "Sahaaya Universal Health Guidance System - Version 1.2 (Testing Mode)",
        "status": "operational",
        "connectivity": {
            "internet_available": True,
            "recommended_mode": "offline_testing"
        },
        "capabilities": {
            "urban_support": True,
            "rural_support": True,
            "emergency_protocols": True,
            "multilingual": True,
            "offline_database": True
        },
        "supported_languages": ["en", "hi", "te", "ta", "bn"],
        "version": "1.2.0-test",
        "note": "Testing mode - using offline database only"
    }

@app.get("/connectivity-status")
def get_connectivity_status():
    """Get simulated connectivity status for testing"""
    return {
        "connectivity": {
            "internet_available": True,
            "confidence": 0.8,
            "test_mode": True
        },
        "recommended_mode": "offline_testing",
        "system_capabilities": {
            "offline_database": True,
            "emergency_protocols": True,
            "multilingual_support": True
        },
        "universal_access": True,
        "mode_descriptions": {
            "offline_testing": "Testing mode with offline database",
            "offline": "Complete offline functionality (Rural areas)"
        }
    }

@app.post("/smart-process")
def smart_process_query(query: HealthQuery, background_tasks: BackgroundTasks):
    """
    Testing version - uses rule-based NLP for better responses
    """
    try:
        logger.info(f"Processing query in testing mode: {query.text[:50]}...")
        
        # Use the NLP module for intelligent health guidance
        guidance = get_health_guidance(query.text, query.language or "en")
        
        # Add testing metadata
        guidance.update({
            "processing_mode": "nlp_testing",
            "internet_required": False,
            "test_mode": True,
            "note": "Using rule-based NLP for testing",
            "user_id": query.user_id
        })
        
        return guidance
        
    except Exception as e:
        logger.error(f"Smart processing error: {e}")
        return {
            "guidance": "Unable to process query in testing mode. Please check your input and try again.",
            "processing_mode": "error_fallback",
            "error": str(e),
            "detected_symptoms": [],
            "severity": "unknown",
            "urgency": "routine"
        }

@app.post("/offline-guidance")
def get_offline_guidance(query: HealthQuery):
    """
    Complete offline health guidance using local database.
    """
    try:
        # Use offline database for guidance
        guidance = offline_db.get_offline_health_guidance(query.text, query.language or "en")
        
        # Add metadata for testing
        guidance.update({
            "processing_mode": "offline",
            "internet_required": False,
            "suitable_for": ["rural", "remote", "emergency", "testing"],
            "data_source": "local_database"
        })
        
        return guidance
        
    except Exception as e:
        logger.error(f"Offline guidance error: {e}")
        return {
            "guidance": "Basic offline functionality available. For symptoms, please consult a healthcare provider.",
            "processing_mode": "basic_fallback",
            "error": str(e)
        }

@app.post("/emergency-protocol")
def get_emergency_protocol(emergency: EmergencyQuery):
    """
    Emergency response protocols for critical situations.
    """
    try:
        # Get emergency protocols from offline database
        emergency_contacts = offline_db.get_emergency_contacts()
        
        # Get specific emergency guidance
        emergency_text = f"emergency {emergency.emergency_type}"
        guidance = offline_db.get_offline_health_guidance(
            emergency_text, 
            emergency.language or "en"
        )
        
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
                "guidance": "Call emergency services immediately: 108 for medical emergencies.",
                "emergency_contact": "108",
                "immediate_action": "Get professional help now"
            },
            "emergency_contacts": [
                {"name": "Emergency Services", "contact": "108", "availability": "24/7"},
                {"name": "Police", "contact": "100", "availability": "24/7"}
            ]
        }

@app.get("/health")
def health_check():
    """System health check endpoint"""
    try:
        # Test database connectivity
        db_status = "operational"
        try:
            offline_db.get_emergency_contacts()
        except Exception:
            db_status = "error"
        
        return {
            "status": "healthy",
            "database": db_status,
            "mode": "testing",
            "version": "1.2.0-test",
            "offline_database": "operational"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "version": "1.2.0-test"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)