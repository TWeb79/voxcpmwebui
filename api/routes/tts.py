"""
Text-to-Speech Routes
Endpoints for text-to-speech generation using VoxCPM2.
"""
from fastapi import APIRouter, HTTPException, Form
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
async def generate_tts(
    text: str = Form(..., min_length=1, max_length=500),
    cfg_value: float = Form(2.0, ge=0.0, le=10.0),
    inference_timesteps: int = Form(10, ge=1, le=100)
):
    """
    Generate speech from text using VoxCPM2.
    
    Args:
        text: Input text to synthesize (1-500 characters)
        cfg_value: Classifier-free guidance value (0.0-10.0)
        inference_timesteps: Number of inference steps (1-100)
        
    Returns:
        WAV audio file
    """
    try:
        logger.info(f"Generating TTS for text: {text[:50]}...")
        
        # Get the VoxCPM model
        model = voxcpm_model.model
        
        # Generate audio
        wav = model.generate(
            text=text,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
        )
        
        # Convert to WAV bytes
        wav_bytes = audio_service.save_wav_file(wav, model.tts_model.sample_rate)
        
        logger.info("TTS generation completed successfully")
        
        # Return as WAV file
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=tts_output.wav"}
        )
        
    except Exception as e:
        logger.error(f"Error in TTS generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )