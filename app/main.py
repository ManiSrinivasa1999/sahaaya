"""
Sahaaya Universal Health Guidance System - Version 1.2
Intelligent online/offline switching for universal urban/rural healthcare access
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import logging
import os

from app.db import db, init_db
from app.connectivity import (
    ConnectivityManager,
    get_connection_status
)

# -------------------------------------------------------
# 1) Create APP FIRST — Required for CORS
# -------------------------------------------------------
app = FastAPI(
    title="Sahaaya Universal Health Guidance System",
    description="Intelligent health guidance with automatic online/offline switching for urban and rural areas",
    version="1.2.0"
)

# -------------------------------------------------------
# 2) CORS — GitHub Pages main domain only
# -------------------------------------------------------
origins = [
    "https://manisrinivasa1999.github.io",
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Connectivity Manager
# -------------------------------------------------------
connectivity_manager = ConnectivityManager()

# -------------------------------------------------------
# Stub Functions
# -------------------------------------------------------
def get_health_guidance(text: str, language: str = "en") -> Dict:
    try:
        from app.nlp import get_health_guidance as nlp_guidance
        return nlp_guidance(text, language)
    except Exception:
        return db.get_offline_health_guidance(text, language)

def transcribe_audio(audio_file: str, language: Optional[str] = None) -> Dict:
    return {"error": "Audio transcription unavailable", "success": False}

def generate_multilingual_audio(text: str, language: str = "en") -> Dict:
    return {"error": "TTS unavailable", "success": False}

# -------------------------------------------------------
# Logging
# -------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Frontend Static Serving (fixed path)
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_directory = os.path.join(BASE_DIR, "..", "frontend")

if os.path.exists(frontend_directory):
    app.mount("/static", StaticFiles(directory=frontend_directory), name="static")

    @app.get("/app")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_directory, "index.html"))

    @app.get("/manifest.json")
    async def serve_manifest():
        return FileResponse(os.path.join(frontend_directory, "manifest.json"))

    @app.get("/sw.js")
    async def serve_service_worker():
        return FileResponse(os.path.join(frontend_directory, "sw.js"))

# -------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------
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

# -------------------------------------------------------
# Startup Event
# -------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
        logger.info("Sahaaya system started")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

# -------------------------------------------------------
# Routes
# -------------------------------------------------------
@app.get("/")
def home():
    try:
        connectivity = get_connection_status()
    except:
        connectivity = {"internet_available": False, "recommendation": {"mode": "offline"}}

    return {
        "message": "Sahaaya Universal Health Guidance System - Version 1.2",
        "status": "operational",
        "connectivity": connectivity
    }


@app.get("/connectivity-status")
def get_status():
    try:
        return get_connection_status()
    except:
        return {"internet_available": False, "recommended_mode": "offline"}


@app.post("/smart-process")
def smart_process_query(query: HealthQuery, background_tasks: BackgroundTasks):
    try:
        connectivity = get_connection_status()
        is_online = connectivity.get("internet_available", False)

        if is_online:
            return process_online_mode(query)
        else:
            return process_offline_mode(query)
    except:
        return process_offline_mode(query)


@app.post("/offline-guidance")
def offline_guidance(query: HealthQuery):
    try:
        guidance = db.get_offline_health_guidance(query.text, query.language)
        guidance.update({"processing_mode": "offline"})
        return guidance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emergency-protocol")
def emergency_protocol(emergency: EmergencyQuery):
    try:
        contacts = db.get_emergency_contacts(emergency.location or "all")

        guidance = db.get_offline_health_guidance(
            f"emergency {emergency.emergency_type}", emergency.language
        )

        return {
            "emergency_guidance": guidance,
            "emergency_contacts": contacts,
            "processing_mode": "offline_emergency"
        }
    except:
        return {
            "emergency_guidance": {"guidance": "Call 108 immediately"},
            "emergency_contacts": [{"name": "Emergency", "contact": "108"}]
        }


@app.post("/process")
def process_audio(query: AudioQuery):
    return {
        "error": "Audio processing unavailable in this version",
        "fallback": "Use /smart-process with text input"
    }

# -------------------------------------------------------
# Processing Modes
# -------------------------------------------------------
def process_online_mode(query: HealthQuery) -> Dict:
    try:
        ai = get_health_guidance(query.text, query.language)
        ai.update({"processing_mode": "online"})
        return ai
    except:
        return process_offline_mode(query)

def process_offline_mode(query: HealthQuery) -> Dict:
    try:
        g = db.get_offline_health_guidance(query.text, query.language)
        g.update({"processing_mode": "offline"})
        return g
    except:
        return {
            "guidance": "Unable to process query",
            "emergency_contact": "108",
            "processing_mode": "fallback"
        }


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.2.0"}
