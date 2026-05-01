# VoxCPM WebUI

**Project ID:** 38  
**Author:** Inventions4All - github:TWeb79

## Overview

VoxCPM WebUI is a modern, professional web interface for VoxCPM2 that enables multilingual speech generation and voice cloning. The application provides both a web dashboard and a REST API for programmatic access.

## Features

- **Text-to-Speech (TTS):** Convert text to natural speech in multiple languages
- **Voice Design:** Create unique voices using text descriptions
- **Voice Cloning:** Clone voices from reference audio files
- **Ultimate Cloning:** Advanced voice cloning with prompt audio and text

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend Dashboard | 8038 | Web UI served via Python HTTP server |
| Backend API | 8138 | FastAPI REST API |

## Architecture

```
Frontend (8038) <-> Backend API (8138) <-> VoxCPM2 Model
```

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- VoxCPM2 model (downloaded automatically on first run)

## Installation

### Option 1: Docker (Recommended)

```bash
# Build and start the container
docker-compose build
docker-compose up -d
docker-compose logs -f

# Run in background with models cached
docker-compose up -d


```

The application will be available at:
- Dashboard: http://localhost:8038
- API Documentation: http://localhost:8138/docs

### Option 2: Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend API
python -m uvicorn api.main:app --host 0.0.0.0 --port 8138

# In a separate terminal, start the frontend
python -m http.server 8038 --directory dashboard
```

## API Endpoints

### Health Check

```bash
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_info": {
    "sample_rate": 24000,
    "device": "cuda"
  }
}
```

### Text-to-Speech

```bash
POST /api/v1/tts/generate
Content-Type: multipart/form-data

Parameters:
- text: string (required, 1-500 characters)
- cfg_value: float (default: 2.0, range: 0.0-10.0)
- inference_timesteps: int (default: 10, range: 1-100)

Response: WAV audio file
```

### Voice Design

```bash
POST /api/v1/voice-design/generate
Content-Type: multipart/form-data

Parameters:
- voice_description: string (required, 1-200 characters)
- text: string (required, 1-500 characters)
- cfg_value: float (default: 2.0)
- inference_timesteps: int (default: 10)

Response: WAV audio file
```

### Voice Cloning

```bash
POST /api/v1/voice-clone/generate
Content-Type: multipart/form-data

Parameters:
- text: string (required, 1-500 characters)
- reference_audio: file (required, audio file)
- cfg_value: float (default: 2.0)
- inference_timesteps: int (default: 10)

Response: WAV audio file
```

### Ultimate Cloning

```bash
POST /api/v1/ultimate-clone/generate
Content-Type: multipart/form-data

Parameters:
- text: string (required, 1-500 characters)
- prompt_audio: file (optional)
- prompt_text: string (optional)
- reference_audio: file (optional)

Response: WAV audio file
```

## API Examples

### Using curl

```bash
# TTS Generation
curl -X POST "http://localhost:8138/api/v1/tts/generate" \
  -F "text=Hello, this is a test." \
  -F "cfg_value=2.0" \
  -F "inference_timesteps=10" \
  --output output.wav

# Voice Cloning
curl -X POST "http://localhost:8138/api/v1/voice-clone/generate" \
  -F "text=Hello, this is a test." \
  -F "reference_audio=@reference.wav" \
  --output output.wav
```

### Using Python

```python
import requests

# TTS Generation
response = requests.post(
    "http://localhost:8138/api/v1/tts/generate",
    data={"text": "Hello, this is a test."}
)
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| VOXCPM_MODEL_PATH | openbmb/VoxCPM2 | HuggingFace model path |

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=api --cov-report=html
```

## Project Structure

```
.
├── api/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── voxcpm.py        # VoxCPM model wrapper
│   ├── routes/
│   │   ├── tts.py           # TTS endpoints
│   │   ├── voice_clone.py   # Voice cloning endpoints
│   │   ├── voice_design.py  # Voice design endpoints
│   │   ├── ultimate_clone.py # Ultimate cloning endpoints
│   │   └── health.py        # Health check endpoints
│   └── services/
│       ├── audio_service.py # Audio processing
│       └── file_service.py  # File handling
├── dashboard/
│   ├── index.html           # Main UI
│   ├── css/
│   │   ├── styles.css       # Main styles
│   │   └── responsive.css   # Responsive design
│   └── js/
│       ├── app.js           # Main application logic
│       ├── api-client.js    # API communication
│       └── audio-recorder.js # Voice recording
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_tts.py          # TTS tests
│   └── test_voice_clone.py  # Voice cloning tests
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### Model fails to download
Ensure you have internet access and HuggingFace credentials if required:
```bash
huggingface-cli login
```

### Audio playback issues
- Supported formats: WAV, MP3, and other common audio formats
- Maximum file size: 10MB

### Docker memory issues
Increase Docker memory allocation to at least 4GB for model loading.

## License

This project uses the VoxCPM2 model which is subject to its respective license terms.