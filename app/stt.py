import whisper

model = whisper.load_model("small")

def transcribe_audio(audio_path, language=None):
    """
    Transcribe audio to text with multilingual support
    
    Args:
        audio_path: Path to audio file
        language: Optional language code (if None, auto-detects)
    """
    if language:
        # Use specified language
        result = model.transcribe(audio_path, language=language)
    else:
        # Auto-detect language
        result = model.transcribe(audio_path)
    
    return {
        "text": result["text"],
        "language": result["language"],
        "confidence": result.get("segments", [{}])[0].get("no_speech_prob", 0) if result.get("segments") else 0
    }