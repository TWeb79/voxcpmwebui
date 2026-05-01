"""
Unit tests for TTS functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    with patch('api.routes.tts.voxcpm_model') as mock_model:
        mock_model.is_loaded.return_value = True
        mock_model.model.tts_model.sample_rate = 24000
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] == True


def test_health_check_model_not_loaded():
    """Test health check when model is not loaded."""
    with patch('api.routes.tts.voxcpm_model') as mock_model:
        mock_model.is_loaded.return_value = False
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["model_loaded"] == False


def test_generate_tts_success():
    """Test successful TTS generation."""
    with patch('api.routes.tts.voxcpm_model') as mock_model, \
         patch('api.routes.tts.audio_service') as mock_audio:
        
        # Mock the VoxCPM model
        mock_instance = Mock()
        mock_instance.generate.return_value = [0.1, 0.2, 0.3]  # Fake audio data
        mock_instance.tts_model.sample_rate = 24000
        mock_model.model = mock_instance
        
        # Mock audio service
        mock_audio.save_wav_file.return_value = b"fake wav data"
        
        response = client.post(
            "/api/v1/tts/generate",
            data={
                "text": "Hello world",
                "cfg_value": 2.0,
                "inference_timesteps": 10
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"fake wav data"


def test_generate_tts_empty_text():
    """Test TTS generation with empty text."""
    response = client.post(
        "/api/v1/tts/generate",
        data={
            "text": "",  # Empty text
            "cfg_value": 2.0,
            "inference_timesteps": 10
        }
    )
    
    # Should return 422 Unprocessable Entity due to validation
    assert response.status_code == 422


def test_generate_tts_invalid_cfg():
    """Test TTS generation with invalid CFG value."""
    response = client.post(
        "/api/v1/tts/generate",
        data={
            "text": "Hello world",
            "cfg_value": 15.0,  # Too high
            "inference_timesteps": 10
        }
    )
    
    # Should return 422 Unprocessable Entity due to validation
    assert response.status_code == 422