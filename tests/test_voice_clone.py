"""
Unit tests for voice cloning functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_voice_clone_success():
    """Test successful voice cloning."""
    with patch('api.models.voxcpm.voxcpm_model') as mock_model, \
         patch('api.services.audio_service.audio_service') as mock_audio, \
         patch('api.services.file_service.file_service') as mock_file:
        
        # Mock the VoxCPM model
        mock_instance = Mock()
        mock_instance.generate.return_value = [0.1, 0.2, 0.3]  # Fake audio data
        mock_instance.tts_model.sample_rate = 24000
        mock_model.model = mock_instance
        
        # Mock audio service
        mock_audio.save_wav_file.return_value = b"fake wav data"
        
        # Mock file service
        mock_file.create_temp_file_from_upload.return_value = "/tmp/fake_file.wav"
        mock_file.delete_file.return_value = True
        
        # Create a fake file content
        fake_file_content = b"fake audio content"
        
        response = client.post(
            "/api/v1/voice-clone/generate",
            data={
                "text": "Hello world",
                "cfg_value": 2.0,
                "inference_timesteps": 10
            },
            files={
                "reference_audio": ("test.wav", fake_file_content, "audio/wav")
            }
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"fake wav data"
        
        # Verify file service was called
        mock_file.create_temp_file_from_upload.assert_called_once()
        mock_file.delete_file.assert_called_once()


def test_voice_clone_no_file():
    """Test voice cloning without file."""
    response = client.post(
        "/api/v1/voice-clone/generate",
        data={
            "text": "Hello world",
            "cfg_value": 2.0,
            "inference_timesteps": 10
        }
    )
    
    # Should return 422 Unprocessable Entity due to missing file
    assert response.status_code == 422


def test_voice_clone_invalid_file_type():
    """Test voice cloning with invalid file type."""
    fake_file_content = b"not an audio file"
    
    response = client.post(
        "/api/v1/voice-clone/generate",
        data={
            "text": "Hello world",
            "cfg_value": 2.0,
            "inference_timesteps": 10
        },
        files={
            "reference_audio": ("test.txt", fake_file_content, "text/plain")
        }
    )
    
    # Should return 400 Bad Request due to invalid file type
    assert response.status_code == 400