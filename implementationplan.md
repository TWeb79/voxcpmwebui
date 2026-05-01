# VoxCPM WebUI Implementation Plan

## Project Overview
Build a modern, professional web interface for VoxCPM2 that allows users to:
1. Enter text or record voice input
2. Generate audio from text prompts
3. Clone voices from reference audio
4. Provide an API layer for programmatic access

## Technical Specifications
- Project ID: 38
- Web Dashboard Port: 8038
- FastAPI Service Port: 8138
- Technologies: FastAPI (backend), HTML/CSS/JavaScript (frontend), Docker (containerization)

## Architecture
```
Frontend (8038) <-> Backend API (8138) <-> VoxCPM2 Model
```

### Backend Structure (FastAPI)
```
api/
  ├── routes/
  │   ├── tts.py          # Text-to-speech endpoints
  │   ├── voice_clone.py  # Voice cloning endpoints
  │   └── health.py       # Health check endpoints
  ├── models/
  │   └── voxcpm.py       # VoxCPM model wrapper
  ├── services/
  │   ├── audio_service.py # Audio processing utilities
  │   └── file_service.py  # File handling utilities
  └── main.py             # FastAPI application entry point
```

### Frontend Structure
```
dashboard/
  ├── index.html          # Main page
  ├── css/
  │   ├── styles.css      # Main stylesheet
  │   └── responsive.css  # Responsive design
  ├── js/
  │   ├── app.js          # Main application logic
  │   ├── audio-recorder.js # Voice recording functionality
  │   └── api-client.js   # API communication layer
  └── assets/
      ├── icons/          # UI icons
      └── images/         # Background/logo images
```

## API Endpoints
### Text-to-Speech
- POST `/api/v1/tts/generate`
  - Parameters: text (string), cfg_value (float, default 2.0), inference_timesteps (int, default 10)
  - Returns: WAV audio file

### Voice Design
- POST `/api/v1/voice-design/generate`
  - Parameters: voice_description (string), text (string), cfg_value (float), inference_timesteps (int)
  - Returns: WAV audio file

### Voice Cloning
- POST `/api/v1/voice-clone/generate`
  - Parameters: text (string), reference_audio (file), cfg_value (float), inference_timesteps (int)
  - Returns: WAV audio file

### Ultimate Cloning
- POST `/api/v1/ultimate-clone/generate`
  - Parameters: text (string), prompt_audio (file), prompt_text (string), reference_audio (file, optional)
  - Returns: WAV audio file

### Health Check
- GET `/api/v1/health`
  - Returns: service status

## Implementation Steps
1. Set up project structure following coding rules
2. Create FastAPI application with VoxCPM2 integration
3. Implement API endpoints for TTS, voice design, and cloning
4. Create frontend interface with recording capabilities
5. Containerize application with Docker
6. Add comprehensive tests
7. Update documentation (README.md, ARCHITECTURE.md)

### Detailed Implementation Tasks

#### Backend Development
- Create `api/models/voxcpm.py`: VoxCPM model wrapper with singleton pattern
- Create `api/services/audio_service.py`: Audio processing utilities (format conversion, validation)
- Create `api/services/file_service.py`: File handling (temporary storage, cleanup)
- Create `api/routes/tts.py`: Text-to-speech endpoint implementations
- Create `api/routes/voice_clone.py`: Voice cloning endpoint implementations
- Create `api/routes/health.py`: Health check and model status endpoints
- Create `api/main.py`: FastAPI application setup with middleware and routing

#### Frontend Development
- Create `dashboard/index.html`: Main UI layout with semantic HTML
- Create `dashboard/css/styles.css`: Modern, professional styling with CSS variables
- Create `dashboard/css/responsive.css`: Mobile-responsive design
- Create `dashboard/js/app.js`: Main application state management and UI logic
- Create `dashboard/js/audio-recorder.js`: Voice recording using MediaRecorder API
- Create `dashboard/js/api-client.js`: Wrapper for API communication with error handling

#### DevOps & Deployment
- Create `Dockerfile`: Multi-stage Docker build for production
- Create `docker-compose.yml`: Service orchestration for development
- Create `.dockerignore`: Docker build optimization
- Create `nginx.conf`: Reverse proxy configuration (if needed)

#### Testing
- Create `tests/test_tts.py`: Unit tests for TTS functionality
- Create `tests/test_voice_clone.py`: Unit tests for voice cloning
- Create `tests/test_integration.py`: Integration tests for API endpoints
- Create `tests/conftest.py`: Pytest configuration and fixtures

#### Documentation
- Update `README.md`: Setup instructions, usage examples, API reference
- Create `ARCHITECTURE.md`: System design, data flow, component relationships
- Add inline docstrings to all Python modules following standards
- Add JSDoc comments to JavaScript modules

## Dependencies
- fastapi>=0.115.0
- uvicorn[standard]>=0.29.0
- voxcpm>=1.0.3
- python-multipart>=0.0.9
- soundfile>=0.12.1
- numpy>=1.24.0
- pytest>=7.0.0 (for testing)

## Docker Configuration
- Multi-stage build: Builder stage for dependencies, runtime stage for execution
- Expose ports 8038 (frontend) and 8138 (backend)
- Health check endpoint at `/api/v1/health`
- Volume mounting for model caching to avoid re-downloads
- Non-root user for security
- Includes Dockerfile and docker-compose.yml for containerized deployment

## Security Considerations
- Input validation and sanitization for all API parameters
- File upload restrictions: Only accept audio files (wav, mp3, etc.)
- File size limits for uploads (e.g., 10MB max)
- Rate limiting for API endpoints to prevent abuse
- CORS configuration: Restrict to trusted origins in production
- Secure temporary file handling with automatic cleanup
- No logging of sensitive data (audio content, etc.)

## Testing Strategy
- Unit tests: Test individual functions and classes with mocks
- Integration tests: Test API endpoints with real VoxCPM model (small footprint)
- End-to-end tests: Simulate user interactions with the web interface
- Load testing: Verify performance under concurrent requests (using locust or similar)
- Test coverage: Aim for >80% line coverage for backend code

## Documentation Requirements
- README.md with:
  - Project overview and features
  - Prerequisites and installation instructions
  - Quick start guide (Docker and manual)
  - API reference with examples
  - Troubleshooting FAQ
- ARCHITECTURE.md detailing:
  - System architecture diagram (text-based)
  - Data flow for each operation type
  - Component responsibilities
  - External dependencies
  - Deployment architecture
- API documentation:
  - Auto-generated from FastAPI (Swagger UI at `/docs`)
  - Additional examples and usage guides
- Inline code comments following standards:
  - Docstrings for all public functions and classes
  - Comments explaining non-obvious logic
  - TODO comments only for tracked technical debt