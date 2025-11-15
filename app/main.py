from fastapi import FastAPI
#from app.stt import transcribe_audio
from app.stt_multilingual import transcribe_audio
from app.nlp import get_health_guidance
#from app.tts import generate_audio
from app.tts import generate_multilingual_audio
from typing import Optional

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Sahaaya Backend is running"}


@app.post("/process")
def process_query(audio_file: str, language: Optional[str] = None):
    """
    Process audio query with optional language specification
    
    Args:
        audio_file: Path to audio file
        language: Optional language code (te, hi, en, etc.). If not provided, auto-detects
    """
    # Transcribe audio with multilingual support
    transcription_result = transcribe_audio(audio_file, language)
    
    if not transcription_result.get("success", True):
        return {"error": "Failed to transcribe audio", "details": transcription_result.get("error")}
    
    text = transcription_result["text"] if isinstance(transcription_result, dict) else transcription_result
    detected_language = transcription_result.get("language", "unknown") if isinstance(transcription_result, dict) else "unknown"
    
    # Get enhanced health guidance with language support
    guidance_result = get_health_guidance(text, detected_language)
    
    # Generate audio response with multilingual support
    guidance_text = guidance_result["guidance"] if isinstance(guidance_result, dict) else guidance_result
    audio_result = generate_multilingual_audio(guidance_text, detected_language)
    
    return {
        "input_text": text,
        "detected_language": detected_language,
        "guidance": guidance_result,
        "audio": audio_result
    }


