"""
Audio Processing Service
Handles audio format conversion, validation, and preprocessing for VoxCPM.
"""
import io
import numpy as np
import soundfile as sf
from typing import Tuple, Union
import logging

logger = logging.getLogger(__name__)

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not available, some audio format support may be limited")

try:
    import resampy
    RESAMPY_AVAILABLE = True
except ImportError:
    RESAMPY_AVAILABLE = False
    logger.warning("resampy not available, audio resampling will be limited")


class AudioService:
    """Service for audio processing operations."""
    
    @staticmethod
    def validate_audio_file(file_content: bytes, max_size_mb: int = 10) -> bool:
        """
        Validate audio file size and format.
        
        Args:
            file_content: Raw file bytes
            max_size_mb: Maximum allowed file size in MB
            
        Returns:
            True if valid, False otherwise
        """
        # Check file size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > max_size_mb:
            return False
            
        # Try to load as audio file
        try:
            audio_io = io.BytesIO(file_content)
            # Try with soundfile first
            data, samplerate = sf.read(audio_io)
            return True
        except Exception as e:
            logger.debug(f"Soundfile validation failed: {e}")
            
            # Try with pydub as fallback if available
            if PYDUB_AVAILABLE:
                try:
                    audio_io = io.BytesIO(file_content)
                    AudioSegment.from_file(audio_io)
                    return True
                except Exception as e2:
                    logger.debug(f"Pydub validation failed: {e2}")
                    
        return False
    
    @staticmethod
    def load_audio_file(file_content: bytes) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return numpy array and sample rate.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        audio_io = io.BytesIO(file_content)
        
        # Try soundfile first
        try:
            data, samplerate = sf.read(audio_io)
            # Ensure mono audio
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            return data, samplerate
        except Exception as e:
            logger.debug(f"Soundfile loading failed: {e}")
            
            # Fallback to pydub if available
            if PYDUB_AVAILABLE:
                try:
                    audio_io = io.BytesIO(file_content)
                    audio_segment = AudioSegment.from_file(audio_io)
                    # Convert to mono and get raw data
                    audio_segment = audio_segment.set_channels(1)
                    raw_data = np.array(audio_segment.get_array_of_samples())
                    # Normalize based on sample width
                    if audio_segment.sample_width == 2:  # 16-bit
                        raw_data = raw_data.astype(np.float32) / 32768.0
                    elif audio_segment.sample_width == 4:  # 32-bit
                        raw_data = raw_data.astype(np.float32) / 2147483648.0
                    else:  # 8-bit
                        raw_data = (raw_data.astype(np.float32) - 128) / 128.0
                    return raw_data, audio_segment.frame_rate
                except Exception as e2:
                    logger.error(f"Pydub loading failed: {e2}")
                    raise ValueError(f"Could not load audio file: {e2}")
            else:
                raise ValueError("Could not load audio file with soundfile and pydub not available")
    
    @staticmethod
    def save_wav_file(audio_data: np.ndarray, sample_rate: int) -> bytes:
        """
        Save audio data as WAV file in memory.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of audio data
            
        Returns:
            WAV file as bytes
        """
        # Ensure audio data is in correct format
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
            
        # Clip to [-1, 1] range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()
    
    @staticmethod
    def resample_audio(audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio data to target sample rate.
        
        Args:
            audio_data: Input audio data
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio data
        """
        if orig_sr == target_sr:
            return audio_data
            
        # Use resampy if available for high quality resampling
        if RESAMPY_AVAILABLE:
            return resampy.resample(audio_data, orig_sr, target_sr)
        else:
            # Fallback to simple linear interpolation
            # Note: This is lower quality but avoids dependency issues
            if len(audio_data) == 0:
                return audio_data
                
            # Calculate resampling ratio
            ratio = target_sr / orig_sr
            new_length = int(len(audio_data) * ratio)
            
            # Create new indices
            old_indices = np.linspace(0, len(audio_data) - 1, len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_length)
            
            # Interpolate
            return np.interp(new_indices, old_indices, audio_data)


# Global instance
audio_service = AudioService()