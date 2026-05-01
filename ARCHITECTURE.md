# VoxCPM WebUI Architecture

**Project ID:** 38  
**Author:** Inventions4All - github:TWeb79

## System Overview

VoxCPM WebUI is a client-server application that provides a web interface and REST API for VoxCPM2, a multilingual text-to-speech and voice cloning model.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Browser                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Dashboard │  │  API Client │  │   Audio Recorder        │ │
│  │  (HTML/CSS) │  │  (JavaScript)│  │   (MediaRecorder API)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Server (8038)                      │
│                   Python HTTP Server (dashboard/)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │ API Calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (8138)                         │
│                      FastAPI Application                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Routes                             │  │
│  │  ┌─────────┐ ┌─────────────┐ ┌────────────┐ ┌─────────┐ │  │
│  │  │   TTS   │ │Voice Design │ │Voice Clone │ │Ultimate │ │  │
│  │  │  Route  │ │   Route     │ │   Route    │ │ Clone   │ │  │
│  │  └────┬────┘ └──────┬──────┘ └─────┬──────┘ └────┬────┘ │  │
│  └───────┼─────────────┼───────────────┼─────────────┼──────┘  │
│          │             │               │             │          │
│          └─────────────┴───────┬───────┴─────────────┘          │
│                                │                                │
│  ┌─────────────────────────────┼────────────────────────────┐  │
│  │                    Service Layer                          │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐  │  │
│  │  │  Audio Service  │  │      File Service            │  │  │
│  │  │  - Validation    │  │      - Temp file handling    │  │  │
│  │  │  - Format conv.  │  │      - Cleanup               │  │  │
│  │  │  - WAV export    │  │                              │  │  │
│  │  └─────────────────┘  └─────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                │                                │
│  ┌─────────────────────────────┼────────────────────────────┐  │
│  │                   Model Layer                             │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │              VoxCPM Model (Singleton)               │ │  │
│  │  │              - Text-to-Speech                       │ │  │
│  │  │              - Voice Design                         │ │  │
│  │  │              - Voice Cloning                        │ │  │
│  │  │              - Ultimate Cloning                     │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Frontend Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| Dashboard | `dashboard/index.html` | Main UI structure with tabbed interface |
| Styles | `dashboard/css/styles.css` | Visual styling using CSS variables |
| Responsive | `dashboard/css/responsive.css` | Mobile-responsive design |
| App Logic | `dashboard/js/app.js` | UI state management, form handling |
| API Client | `dashboard/js/api-client.js` | HTTP communication with backend |
| Audio Recorder | `dashboard/js/audio-recorder.js` | Microphone recording via MediaRecorder API |

### Backend Layer

| Component | File | Responsibility |
|-----------|------|----------------|
| Main App | `api/main.py` | FastAPI application setup, CORS, routing |
| TTS Route | `api/routes/tts.py` | Text-to-speech generation endpoint |
| Voice Design Route | `api/routes/voice_design.py` | Voice design generation endpoint |
| Voice Clone Route | `api/routes/voice_clone.py` | Voice cloning endpoint |
| Ultimate Clone Route | `api/routes/ultimate_clone.py` | Ultimate cloning endpoint |
| Health Route | `api/routes/health.py` | Health check and model status |
| VoxCPM Model | `api/models/voxcpm.py` | Singleton model wrapper |
| Audio Service | `api/services/audio_service.py` | Audio validation, format conversion |
| File Service | `api/services/file_service.py` | Temporary file management |

## Data Flow

### Text-to-Speech Flow

```
User Input → Form Submit → API Client → POST /api/v1/tts/generate
    → VoxCPM Model.generate() → Audio Service.save_wav_file()
    → HTTP Response (WAV) → Audio Player → User
```

### Voice Cloning Flow

```
User selects audio file → Form Submit → API Client → POST /api/v1/voice-clone/generate
    → File Service.create_temp_file_from_upload() → VoxCPM Model.generate()
    → Audio Service.save_wav_file() → HTTP Response (WAV) → Audio Player
    → File Service.delete_file() (cleanup)
```

## API Design

### Request/Response Pattern

All generation endpoints follow the same pattern:

**Request:** `multipart/form-data`
- Text parameters as form fields
- Audio files as file uploads

**Response:** `audio/wav`
- Binary WAV file with Content-Disposition header

### Error Handling

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Model Management

The VoxCPM model uses a singleton pattern to ensure:
- Only one model instance in memory
- Lazy loading on first access
- GPU utilization when available

```python
# Singleton pattern ensures single model instance
voxcpm_model = VoxCPMModel()  # Loaded once at import
```

## Security Considerations

1. **Input Validation:** All API inputs are validated using FastAPI's built-in validators
2. **File Type Restrictions:** Only audio files are accepted for upload
3. **File Size Limits:** Maximum 10MB per uploaded file
4. **CORS Configuration:** Configured for cross-origin requests
5. **Temporary File Cleanup:** Automatic cleanup of uploaded files after processing

## External Dependencies

| Dependency | Purpose | Version |
|------------|---------|---------|
| fastapi | Web framework | >=0.115.0 |
| uvicorn | ASGI server | >=0.29.0 |
| voxcpm | TTS model | >=1.0.3 |
| soundfile | Audio I/O | >=0.12.1 |
| numpy | Numerical operations | >=1.24.0 |
| pydub | Audio format support | >=0.25.1 |
| resampy | Audio resampling | >=0.4.2 |

## Deployment Architecture

### Docker Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Python HTTP Server (8038)                          │   │
│  │  Serves static files from /app/dashboard            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Uvicorn ASGI Server (8138)                         │   │
│  │  Runs FastAPI application                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VoxCPM Model                                       │   │
│  │  Downloaded from HuggingFace on first run           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| ./models | /app/models | Model cache |
| ./temp | /app/temp | Temporary files |

## Testing Strategy

### Unit Tests

- `tests/test_tts.py`: TTS endpoint tests with mocked model
- `tests/test_voice_clone.py`: Voice cloning tests with mocked services

### Test Coverage Goals

- Backend API routes: >80% coverage
- Service layer: Full coverage
- Model layer: Integration tests only (requires model)

## Performance Considerations

1. **Model Loading:** Lazy-loaded on first API request
2. **GPU Acceleration:** Automatically uses CUDA when available
3. **Temporary Files:** Cleaned up immediately after processing
4. **Memory Management:** Single model instance prevents duplication