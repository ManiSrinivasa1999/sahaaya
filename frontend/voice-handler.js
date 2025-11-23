/**
 * Voice Input Handler for Sahaaya
 * Supports multiple Indian languages with Web Speech API
 */

class VoiceHandler {
  constructor() {
    this.recognition = null;
    this.isRecording = false;
    this.currentLanguage = "en";
    this.speechSynthesis = window.speechSynthesis;

    // Language mappings for Web Speech API
    this.languageMappings = {
      en: "en-IN",
      hi: "hi-IN",
      te: "te-IN",
      ta: "ta-IN",
      bn: "bn-IN",
    };

    this.init();
  }

  init() {
    // Check if Speech Recognition is supported
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.setupRecognition();
    } else {
      console.warn("Speech Recognition not supported in this browser");
      this.showFallbackMessage();
    }
  }

  setupRecognition() {
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 3;

    this.recognition.onstart = () => {
      this.onRecordingStart();
    };

    this.recognition.onresult = (event) => {
      this.onRecognitionResult(event);
    };

    this.recognition.onerror = (event) => {
      this.onRecognitionError(event);
    };

    this.recognition.onend = () => {
      this.onRecordingEnd();
    };
  }

  startRecording(language = "en") {
    if (!this.recognition) {
      this.showFallbackMessage();
      return;
    }

    if (this.isRecording) {
      this.stopRecording();
      return;
    }

    this.currentLanguage = language;
    this.recognition.lang = this.languageMappings[language] || "en-IN";

    try {
      this.recognition.start();
      this.isRecording = true;
    } catch (error) {
      console.error("Error starting recognition:", error);
      this.onRecognitionError({ error: "not-allowed" });
    }
  }

  stopRecording() {
    if (this.recognition && this.isRecording) {
      this.recognition.stop();
      this.isRecording = false;
    }
  }

  onRecordingStart() {
    console.log("Recording started");
    const recordBtn = document.getElementById("record-btn");
    const recordingText = document.getElementById("recording-text");

    recordBtn.classList.add("recording");
    recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
    recordingText.textContent = this.getTranslation(
      "listening",
      this.currentLanguage
    );

    // Add visual feedback
    this.addRecordingAnimation();
  }

  onRecognitionResult(event) {
    let finalTranscript = "";
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    // Show interim results
    if (interimTranscript) {
      this.showInterimResult(interimTranscript);
    }

    // Process final result
    if (finalTranscript) {
      this.processFinalResult(finalTranscript);
    }
  }

  onRecognitionError(event) {
    console.error("Recognition error:", event.error);
    this.stopRecording();

    let errorMessage = "Voice recognition failed. ";

    switch (event.error) {
      case "no-speech":
        errorMessage += "No speech detected. Please try again.";
        break;
      case "audio-capture":
        errorMessage += "Microphone not accessible.";
        break;
      case "not-allowed":
        errorMessage += "Microphone permission denied.";
        this.showPermissionHelp();
        break;
      case "network":
        errorMessage += "Network error. Switching to text input.";
        this.switchToTextInput();
        break;
      default:
        errorMessage += "Please try again or use text input.";
    }

    this.showError(errorMessage);
  }

  onRecordingEnd() {
    console.log("Recording ended");
    this.isRecording = false;

    const recordBtn = document.getElementById("record-btn");
    const recordingText = document.getElementById("recording-text");

    recordBtn.classList.remove("recording");
    recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    recordingText.textContent = this.getTranslation(
      "tap-to-speak",
      this.currentLanguage
    );

    this.removeRecordingAnimation();
  }

  showInterimResult(text) {
    const transcriptionText = document.getElementById("transcription-text");
    const voiceFeedback = document.getElementById("voice-feedback");

    if (transcriptionText) {
      transcriptionText.textContent = text;
      transcriptionText.style.opacity = "0.7";
      transcriptionText.style.fontStyle = "italic";
      voiceFeedback.classList.remove("hidden");
    }
  }

  processFinalResult(text) {
    console.log("Final transcription:", text);

    const transcriptionText = document.getElementById("transcription-text");
    const voiceFeedback = document.getElementById("voice-feedback");

    if (transcriptionText) {
      transcriptionText.textContent = text;
      transcriptionText.style.opacity = "1";
      transcriptionText.style.fontStyle = "normal";
      voiceFeedback.classList.remove("hidden");
    }

    // Process the health query
    this.processHealthQuery(text);
  }

  async processHealthQuery(text) {
    try {
      // Show loading
      window.app.showLoading();

      // Send to backend
      const response = await fetch("https://sahaaya-ruvy.onrender.com/smart-process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          language: this.currentLanguage,
          user_id: window.app.getUserId(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Hide loading and show response
      window.app.hideLoading();
      window.app.showResponse(result);

      // Speak the response if enabled
      this.speakResponse(result.guidance || result.message);
    } catch (error) {
      console.error("Error processing query:", error);
      window.app.hideLoading();
      window.app.showError(
        "Failed to process your query. Please try again or use text input."
      );
    }
  }

  speakResponse(text, language = null) {
    if (!this.speechSynthesis || !text) return;

    // Cancel any ongoing speech
    this.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang =
      this.languageMappings[language || this.currentLanguage] || "en-IN";
    utterance.rate = 0.9;
    utterance.pitch = 1;

    // Try to find a voice for the language
    const voices = this.speechSynthesis.getVoices();
    const languageVoice = voices.find((voice) =>
      voice.lang.startsWith(utterance.lang.substring(0, 2))
    );

    if (languageVoice) {
      utterance.voice = languageVoice;
    }

    utterance.onstart = () => {
      console.log("Speech started");
      this.highlightSpeakButton(true);
    };

    utterance.onend = () => {
      console.log("Speech ended");
      this.highlightSpeakButton(false);
    };

    utterance.onerror = (event) => {
      console.error("Speech error:", event);
      this.highlightSpeakButton(false);
    };

    this.speechSynthesis.speak(utterance);
  }

  highlightSpeakButton(speaking) {
    const speakBtn = document.getElementById("speak-response-btn");
    if (speakBtn) {
      if (speaking) {
        speakBtn.classList.add("speaking");
        speakBtn.innerHTML = '<i class="fas fa-volume-down"></i>';
      } else {
        speakBtn.classList.remove("speaking");
        speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
      }
    }
  }

  addRecordingAnimation() {
    // Create visual feedback for recording
    const recordBtn = document.getElementById("record-btn");

    // Add pulsing animation
    const pulseDiv = document.createElement("div");
    pulseDiv.className = "recording-pulse";
    pulseDiv.style.cssText = `
            position: absolute;
            top: -10px;
            left: -10px;
            right: -10px;
            bottom: -10px;
            border: 3px solid rgba(220, 38, 38, 0.5);
            border-radius: 50%;
            animation: pulse-ring 1s ease-out infinite;
            pointer-events: none;
        `;

    recordBtn.style.position = "relative";
    recordBtn.appendChild(pulseDiv);

    // Add CSS animation if not exists
    if (!document.getElementById("pulse-animation-style")) {
      const style = document.createElement("style");
      style.id = "pulse-animation-style";
      style.textContent = `
                @keyframes pulse-ring {
                    0% { transform: scale(1); opacity: 1; }
                    100% { transform: scale(1.3); opacity: 0; }
                }
            `;
      document.head.appendChild(style);
    }
  }

  removeRecordingAnimation() {
    const recordBtn = document.getElementById("record-btn");
    const pulseDiv = recordBtn.querySelector(".recording-pulse");
    if (pulseDiv) {
      pulseDiv.remove();
    }
  }

  showFallbackMessage() {
    const voiceSection = document.getElementById("voice-section");
    const fallbackDiv = document.createElement("div");
    fallbackDiv.className = "voice-fallback";
    fallbackDiv.innerHTML = `
            <div class="fallback-content">
                <i class="fas fa-microphone-slash"></i>
                <h3>Voice input not supported</h3>
                <p>Your browser doesn't support voice recognition. Please use text input instead.</p>
                <button onclick="window.app.switchToTextInput()" class="fallback-btn">
                    <i class="fas fa-keyboard"></i> Switch to Text Input
                </button>
            </div>
        `;

    voiceSection.appendChild(fallbackDiv);
  }

  showPermissionHelp() {
    const helpDiv = document.createElement("div");
    helpDiv.className = "permission-help";
    helpDiv.innerHTML = `
            <div class="help-content">
                <i class="fas fa-info-circle"></i>
                <h4>Microphone Permission Needed</h4>
                <ol>
                    <li>Click the microphone icon in your browser's address bar</li>
                    <li>Allow microphone access</li>
                    <li>Refresh the page</li>
                </ol>
                <button onclick="this.parentElement.parentElement.remove()" class="close-help-btn">Got it</button>
            </div>
        `;

    document.body.appendChild(helpDiv);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (helpDiv.parentElement) {
        helpDiv.remove();
      }
    }, 10000);
  }

  switchToTextInput() {
    if (window.app) {
      window.app.switchToTextInput();
    }
  }

  showError(message) {
    if (window.app) {
      window.app.showError(message);
    }
  }

  getTranslation(key, language) {
    const translations = {
      listening: {
        en: "Listening... speak now",
        hi: "सुन रहा हूँ... अब बोलें",
        te: "వింటున్నాను... ఇప్పుడు మాట్లాడండి",
        ta: "கேட்டுக்கொண்டிருக்கிறேன்... இப்போது பேசுங்கள்",
        bn: "শুনছি... এখন বলুন",
      },
      "tap-to-speak": {
        en: "Tap to speak in your language",
        hi: "अपनी भाषा में बोलने के लिए टैप करें",
        te: "మీ భాషలో మాట్లాడటానికి ట్యాప్ చేయండి",
        ta: "உங்கள் மொழியில் பேச தட்டவும்",
        bn: "আপনার ভাষায় কথা বলতে ট্যাপ করুন",
      },
    };

    return translations[key]?.[language] || translations[key]?.["en"] || key;
  }
}

// Initialize voice handler
window.voiceHandler = new VoiceHandler();
