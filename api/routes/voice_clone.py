"""
Voice Cloning Routes
Endpoints for voice cloning using VoxCPM2.
"""
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
from fastapi.responses import Response
import numpy as np
import soundfile as sf
import io
import logging
from api.models.voxcpm import voxcpm_model
from api.services.audio_service import audio_service
from api.services.file_service import file_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate")
async def generate_voice_clone(
    text: str = Form(..., min_length=1, max_length=500),
    reference_audio: UploadFile = File(...),
    cfg_value: float = Form(2.0, ge=0.0, le=10.0),
    inference_timesteps: int = Form(10, ge=1, le=100)
):
    """
    Generate speech from text using voice cloning with VoxCPM2.
    
    Args:
        text: Input text to synthesize (1-500 characters)
        reference_audio: Reference audio file for voice cloning
        cfg_value: Classifier-free guidance value (0.0-10.0)
        inference_timesteps: Number of inference steps (1-100)
        
    Returns:
        WAV audio file
    """
    temp_file_path = None
    try:
        logger.info(f"Generating voice clone for text: {text[:50]}...")
        
        # Validate file type
        if not reference_audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Read uploaded file
        file_content = await reference_audio.read()
        
        # Validate audio file
        if not audio_service.validate_audio_file(file_content):
            raise HTTPException(
                status_code=400,
                detail="Invalid audio file format"
            )
        
        # Create temporary file for reference audio
        temp_file_path = file_service.create_temp_file_from_upload(
            file_content, reference_audio.filename
        )
        
        # Get the VoxCPM model
        model = voxcpm_model.model
        
        # Generate audio with voice cloning
        wav = model.generate(
            text=text,
            reference_wav_path=temp_file_path,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
        )
        
        # Convert to WAV bytes
        wav_bytes = audio_service.save_wav_file(wav, model.tts_model.sample_rate)
        
        logger.info("Voice cloning completed successfully")
        
        # Return as WAV file
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=voice_clone_output.wav"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice cloning: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate voice clone: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path:
            file_service.delete_file(temp_file_path)