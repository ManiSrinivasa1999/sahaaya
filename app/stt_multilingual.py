import whisper

model = whisper.load_model("small")

# Supported languages for health guidance
SUPPORTED_LANGUAGES = {
    "te": "Telugu",
    "hi": "Hindi", 
    "en": "English",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
    "pa": "Punjabi"
}

def transcribe_audio(audio_path, language=None):
    """
    Transcribe audio to text with multilingual support
    
    Args:
        audio_path: Path to audio file
        language: Optional language code (te, hi, en, etc.)
    
    Returns:
        dict: Contains text, detected/used language, and confidence info
    """
    try:
        if language and language in SUPPORTED_LANGUAGES:
            # Use specified language
            result = model.transcribe(audio_path, language=language)
            detected_language = language
        else:
            # Auto-detect language
            result = model.transcribe(audio_path)
            detected_language = result["language"]
        
        # Check if detected language is supported
        if detected_language not in SUPPORTED_LANGUAGES:
            print(f"Warning: Detected language '{detected_language}' not in supported languages")
        
        return {
            "text": result["text"].strip(),
            "language": detected_language,
            "language_name": SUPPORTED_LANGUAGES.get(detected_language, "Unknown"),
            "segments": result.get("segments", []),
            "success": True
        }
    
    except Exception as e:
        return {
            "text": "",
            "language": "unknown",
            "language_name": "Unknown",
            "segments": [],
            "success": False,
            "error": str(e)
        }

def get_supported_languages():
    """Return list of supported languages"""
    return SUPPORTED_LANGUAGES

def transcribe_with_fallback(audio_path, preferred_languages=None):
    """
    Try transcription with multiple languages as fallback
    
    Args:
        audio_path: Path to audio file
        preferred_languages: List of language codes to try in order
    """
    if not preferred_languages:
        preferred_languages = ["te", "hi", "en"]  # Default fallback order
    
    # First try auto-detection
    result = transcribe_audio(audio_path)
    if result["success"] and result["text"]:
        return result
    
    # If auto-detection fails, try preferred languages
    for lang in preferred_languages:
        result = transcribe_audio(audio_path, language=lang)
        if result["success"] and result["text"]:
            return result
    
    # If all fails, return the last result with error info
    return result