# VoxCPM WebUI Tests Configuration
"""
Pytest configuration and fixtures for VoxCPM WebUI tests.
"""
import pytest
import tempfile
import os
from api.services.file_service import FileService
from api.services.audio_service import AudioService


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def file_service(temp_dir):
    """Create a FileService instance for testing."""
    return FileService(temp_dir)


@pytest.fixture
def audio_service():
    """Create an AudioService instance for testing."""
    return AudioService()


@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing."""
    import numpy as np
    # Generate 1 second of sine wave at 440Hz
    sample_rate = 16000
    duration = 1.0
    frequency = 440.0
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    # Normalize to [-1, 1]
    audio_data = audio_data.astype(np.float32)
    return audio_data, sample_rate