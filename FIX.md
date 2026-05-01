You are working on the VoxCPM WebUI project (Project ID: 38). Fix ALL issues listed below exactly as specified. Do not change anything not listed.

---

## FIX 1: dashboard/index.html — Add missing `name` attributes to all form inputs

In the TTS form, add name attributes:
- <textarea id="tts-text" → add name="tts_text"
- <input id="tts-cfg" → add name="tts_cfg"
- <input id="tts-steps" → add name="tts_steps"

In the voice-design form:
- <input id="voice-description" → add name="voice_description"
- <textarea id="voice-design-text" → add name="voice_design_text"
- <input id="voice-design-cfg" → add name="voice_design_cfg"
- <input id="voice-design-steps" → add name="voice_design_steps"

In the voice-clone form:
- <textarea id="clone-text" → add name="clone_text"
- <input id="reference-audio" → add name="reference_audio"
- <input id="clone-cfg" → add name="clone_cfg"
- <input id="clone-steps" → add name="clone_steps"

In the ultimate-clone form:
- <textarea id="ultimate-text" → add name="ultimate_text"
- <input id="prompt-audio" → add name="prompt_audio"
- <input id="prompt-text" → add name="prompt_text"
- <input id="reference-audio-ultimate" → add name="reference_audio_ultimate"

---

## FIX 2: dashboard/css/styles.css — Add missing `.hidden` utility class

Add this at the end of the file:

.hidden {
    display: none !important;
}

---

## FIX 3: dashboard/js/app.js — Fix broken showMessage function and make API URL configurable

Replace the entire showMessage function with:

function showMessage(message, type) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');

    if (type === 'success') {
        errorMessage.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
        errorMessage.style.borderColor = 'var(--success-color)';
        errorMessage.style.color = 'var(--success-color)';
        setTimeout(() => {
            errorMessage.classList.add('hidden');
            errorMessage.style.backgroundColor = '';
            errorMessage.style.borderColor = '';
            errorMessage.style.color = '';
        }, 3000);
    } else {
        errorMessage.style.backgroundColor = '';
        errorMessage.style.borderColor = '';
        errorMessage.style.color = '';
    }
}

Also replace:
    const api = new APIClient('http://localhost:8138');
With:
    const apiBaseURL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://' + window.location.hostname + ':8138'
        : window.location.protocol + '//' + window.location.hostname + ':8138';
    const api = new APIClient(apiBaseURL);

---

## FIX 4: dashboard/js/app.js — Fix clearResult to properly reset audio

Replace:
    function clearResult() {
        audioPlayer.src = '';
        downloadBtn.disabled = true;
        currentAudioBlob = null;
    }

With:
    function clearResult() {
        if (audioPlayer.src) {
            window.URL.revokeObjectURL(audioPlayer.src);
        }
        audioPlayer.src = '';
        audioPlayer.load();
        downloadBtn.disabled = true;
        currentAudioBlob = null;
        errorMessage.classList.add('hidden');
    }

---

## FIX 5: api/routes/voice_design.py — Remove unused temp_file_path variable

Remove this line entirely:
    temp_file_path = None

---

## FIX 6: api/routes/health.py — Fix model device detection to not crash if model has no .parameters()

Replace:
    "device": str(next(model.parameters()).device) if hasattr(model, 'parameters') else "unknown"

With:
    "device": str(next(iter(model.parameters())).device) if hasattr(model, 'parameters') and callable(model.parameters) else "unknown"

Apply this fix in both the health_check() and get_model_info() functions.

---

## FIX 7: api/models/voxcpm.py — Defer model loading to avoid crash on import

Replace:
    # Global instance
    voxcpm_model = VoxCPMModel()

With:
    # Global instance — model loads lazily on first property access
    voxcpm_model = VoxCPMModel.__new__(VoxCPMModel)
    VoxCPMModel._instance = voxcpm_model

And replace the __init__ method:
    def __init__(self):
        if self._model is None:
            self._load_model()

With:
    def __init__(self):
        pass  # Lazy loading — call load() explicitly or access .model property

And update the model property to trigger load on first access:
    @property
    def model(self) -> VoxCPM:
        """Get the loaded VoxCPM model, loading it if necessary."""
        if self._model is None:
            self._load_model()
        return self._model

And update is_loaded to not trigger a load:
    def is_loaded(self) -> bool:
        """Check if model is loaded without triggering a load."""
        return self._model is not None

---

## FIX 8: tests/test_tts.py — Fix patch paths to match where symbols are used in routes

Replace all occurrences of:
    patch('api.models.voxcpm.voxcpm_model')
With:
    patch('api.routes.tts.voxcpm_model')

Replace all occurrences of:
    patch('api.services.audio_service.audio_service')
With:
    patch('api.routes.tts.audio_service')

---

## FIX 9: tests/test_voice_clone.py — Fix patch paths

Replace all occurrences of:
    patch('api.models.voxcpm.voxcpm_model')
With:
    patch('api.routes.voice_clone.voxcpm_model')

Replace all occurrences of:
    patch('api.services.audio_service.audio_service')
With:
    patch('api.routes.voice_clone.audio_service')

Replace all occurrences of:
    patch('api.services.file_service.file_service')
With:
    patch('api.routes.voice_clone.file_service')

---

## FIX 10: tests/test_voice_clone.py — Fix validate_audio_file mock missing from test_voice_clone_success

In test_voice_clone_success, the mock_audio object needs validate_audio_file to return True. Add this line after mock_audio is set up:
    mock_audio.validate_audio_file.return_value = True

---

## FIX 11: requirements.txt — Add missing pytest dependency

Add at the end:
pytest>=7.0.0
httpx>=0.27.0

(httpx is required by FastAPI's TestClient)

---

## FIX 12: docker-compose.yml — Add GPU support section and HuggingFace cache env var

Replace the entire docker-compose.yml with:

services:
  voxcpm-webui:
    build: .
    ports:
      - "8038:8038"
      - "8138:8138"
    volumes:
      - ./models:/app/models
      - ./temp:/app/temp
    environment:
      - VOXCPM_MODEL_PATH=openbmb/VoxCPM2
      - HF_HOME=/app/models/huggingface
      - TRANSFORMERS_CACHE=/app/models/huggingface
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

---

After all fixes are applied, run:
    pytest tests/ -v

All tests should pass. Then start the backend with:
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8138 --reload

And the frontend with:
    python -m http.server 8038 --directory dashboard