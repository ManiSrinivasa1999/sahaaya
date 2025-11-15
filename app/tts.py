from TTS.api import TTS
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, List
import json

# Custom exceptions for better error handling
class TTSModelError(Exception):
    """Raised when TTS model fails to load or initialize"""
    pass

class TTSGenerationError(Exception):
    """Raised when TTS generation fails"""
    pass

# Language-specific TTS model configuration
MULTILINGUAL_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

TTS_MODELS = {
    "en": "tts_models/en/ljspeech/tacotron2-DDC",  # English
    "hi": "tts_models/hi/male/tacotron2",  # Hindi
    "te": MULTILINGUAL_MODEL,  # Telugu (multilingual model)
    "ta": MULTILINGUAL_MODEL,  # Tamil
    "bn": MULTILINGUAL_MODEL,  # Bengali
    "default": MULTILINGUAL_MODEL  # Fallback multilingual
}

# Voice settings for different languages
VOICE_CONFIG = {
    "en": {"speaker": "ljspeech", "speed": 1.0, "emotion": "neutral"},
    "hi": {"speaker": "male", "speed": 0.9, "emotion": "calm"},
    "te": {"speaker": "female", "speed": 0.85, "emotion": "gentle"},
    "ta": {"speaker": "female", "speed": 0.85, "emotion": "gentle"},
    "bn": {"speaker": "female", "speed": 0.9, "emotion": "calm"},
    "default": {"speaker": "female", "speed": 1.0, "emotion": "neutral"}
}

# Initialize TTS models (lazy loading)
tts_models = {}
output_dir = "audio_responses"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def initialize_tts_model(language: str) -> TTS:
    """Initialize TTS model for specific language with error handling"""
    global tts_models
    
    if language in tts_models:
        return tts_models[language]
    
    try:
        # Try language-specific model first
        if language in TTS_MODELS:
            model_name = TTS_MODELS[language]
        else:
            model_name = TTS_MODELS["default"]
        
        print(f"Loading TTS model for {language}: {model_name}")
        tts_model = TTS(model_name=model_name)
        tts_models[language] = tts_model
        return tts_model
        
    except Exception as e:
        print(f"Failed to load TTS model for {language}: {str(e)}")
        # Fallback to default model
        try:
            if "default" not in tts_models:
                print("Loading fallback TTS model...")
                tts_models["default"] = TTS(model_name=TTS_MODELS["default"])
            return tts_models["default"]
        except Exception as fallback_error:
            print(f"Critical: Failed to load any TTS model: {str(fallback_error)}")
            raise TTSModelError("TTS system unavailable")

def generate_unique_filename(language: str, prefix: str = "response") -> str:
    """Generate unique filename for audio files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{prefix}_{language}_{timestamp}_{unique_id}.wav"
    return os.path.join(output_dir, filename)

def clean_text_for_tts(text: str, language: str) -> str:
    """Clean and prepare text for better TTS pronunciation"""
    # Remove special characters that might confuse TTS
    cleaned_text = text.replace("⚠️", "Warning: ")
    cleaned_text = cleaned_text.replace("💡", "Note: ")
    cleaned_text = cleaned_text.replace("🚨", "Urgent: ")
    
    # Language-specific text cleaning
    if language == "hi":
        # Replace English medical terms with Hindi equivalents
        cleaned_text = cleaned_text.replace("doctor", "डॉक्टर")
        cleaned_text = cleaned_text.replace("hospital", "अस्पताल")
    elif language == "te":
        # Replace English terms with Telugu equivalents
        cleaned_text = cleaned_text.replace("doctor", "వైద్యుడు")
        cleaned_text = cleaned_text.replace("hospital", "ఆసుపత्री")
    
    # Remove excessive newlines and spaces
    cleaned_text = " ".join(cleaned_text.split())
    
    return cleaned_text

def generate_audio(text: str, language: str = "en", voice_options: Optional[Dict] = None) -> Dict:
    """
    Enhanced text-to-speech generation with multilingual support
    
    Args:
        text: Text to convert to speech
        language: Language code (en, hi, te, ta, etc.)
        voice_options: Optional voice customization (speed, speaker, etc.)
    
    Returns:
        Dict with audio file path, metadata, and status
    """
    try:
        # Input validation
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Empty text provided",
                "audio_file": None,
                "metadata": {}
            }
        
        # Clean text for better pronunciation
        cleaned_text = clean_text_for_tts(text, language)
        
        # Initialize TTS model for the language
        tts_model = initialize_tts_model(language)
        
        # Generate unique filename
        audio_filename = generate_unique_filename(language)
        
        # Get voice configuration
        voice_config = VOICE_CONFIG.get(language, VOICE_CONFIG["default"]).copy()
        if voice_options:
            voice_config.update(voice_options)
        
        print(f"Generating audio for language: {language}")
        print(f"Text preview: {cleaned_text[:50]}...")
        
        # Generate speech
        if hasattr(tts_model, 'tts_to_file'):
            # For models that support direct file output
            tts_model.tts_to_file(
                text=cleaned_text,
                file_path=audio_filename,
                speed=voice_config.get("speed", 1.0)
            )
        else:
            # Alternative method for different model types
            audio_data = tts_model.tts(text=cleaned_text)
            # Save audio data to file (implementation depends on model output format)
            with open(audio_filename, 'wb') as f:
                f.write(audio_data)
        
        # Verify file was created successfully
        if not os.path.exists(audio_filename):
            raise TTSGenerationError("Audio file was not generated")
        
        file_size = os.path.getsize(audio_filename)
        if file_size == 0:
            raise TTSGenerationError("Generated audio file is empty")
        
        return {
            "success": True,
            "audio_file": audio_filename,
            "metadata": {
                "language": language,
                "model_used": TTS_MODELS.get(language, TTS_MODELS["default"]),
                "voice_config": voice_config,
                "text_length": len(text),
                "cleaned_text_length": len(cleaned_text),
                "file_size_bytes": file_size,
                "generation_time": datetime.now().isoformat(),
                "audio_duration_estimate": len(cleaned_text) / 10  # Rough estimate: 10 chars per second
            },
            "error": None
        }
        
    except Exception as e:
        error_msg = f"TTS generation failed: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "audio_file": None,
            "metadata": {
                "language": language,
                "attempted_text_length": len(text) if text else 0,
                "error_time": datetime.now().isoformat()
            }
        }

def generate_multilingual_audio(text: str, language: str = "en", include_fallbacks: bool = True) -> Dict:
    """
    Generate audio with automatic fallback to English if target language fails
    
    Args:
        text: Text to convert to speech
        language: Primary language to try
        include_fallbacks: Whether to try fallback languages
    
    Returns:
        Dict with audio file info and attempt details
    """
    attempts = []
    
    # Try primary language first
    result = generate_audio(text, language)
    attempts.append({"language": language, "success": result["success"], "error": result.get("error")})
    
    if result["success"]:
        result["attempts"] = attempts
        return result
    
    # Try fallbacks if enabled
    if include_fallbacks:
        fallback_languages = ["en", "default"] if language != "en" else ["default"]
        
        for fallback_lang in fallback_languages:
            if fallback_lang != language:  # Don't retry the same language
                fallback_result = generate_audio(text, fallback_lang)
                attempts.append({
                    "language": fallback_lang, 
                    "success": fallback_result["success"], 
                    "error": fallback_result.get("error")
                })
                
                if fallback_result["success"]:
                    fallback_result["attempts"] = attempts
                    fallback_result["metadata"]["fallback_used"] = True
                    fallback_result["metadata"]["original_language"] = language
                    return fallback_result
    
    # If all attempts failed
    return {
        "success": False,
        "error": "All TTS generation attempts failed",
        "audio_file": None,
        "attempts": attempts,
        "metadata": {"total_attempts": len(attempts)}
    }

def get_available_languages() -> List[str]:
    """Get list of supported TTS languages"""
    return list(TTS_MODELS.keys())

def cleanup_old_audio_files(max_age_hours: int = 24):
    """Clean up old audio files to save disk space"""
    try:
        current_time = datetime.now()
        removed_count = 0
        
        for filename in os.listdir(output_dir):
            if filename.endswith('.wav'):
                file_path = os.path.join(output_dir, filename)
                file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_age.total_seconds() > max_age_hours * 3600:
                    os.remove(file_path)
                    removed_count += 1
        
        print(f"Cleaned up {removed_count} old audio files")
        return removed_count
        
    except Exception as e:
        print(f"Error during audio cleanup: {str(e)}")
        return 0

# Enhanced function for backward compatibility
def generate_audio_simple(text: str) -> str:
    """Simple function for backward compatibility - returns just the file path"""
    result = generate_audio(text, "en")
    return result["audio_file"] if result["success"] else None