"""
Voice Design Routes
Endpoints for voice design using VoxCPM2.
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
async def generate_voice_design(
    voice_description: str = Form(..., min_length=1, max_length=200),
    text: str = Form(..., min_length=1, max_length=500),
    cfg_value: float = Form(2.0, ge=0.0, le=10.0),
    inference_timesteps: int = Form(10, ge=1, le=100)
):
    """
    Generate speech from text using voice design with VoxCPM2.
    
    Args:
        voice_description: Description of the voice to create (e.g., "A young woman with a gentle voice")
        text: Input text to synthesize (1-500 characters)
        cfg_value: Classifier-free guidance value (0.0-10.0)
        inference_timesteps: Number of inference steps (1-100)
        
    Returns:
        WAV audio file
    """
    temp_file_path = None
    try:
        logger.info(f"Generating voice design for description: {voice_description[:50]}...")
        
        # Format text for voice design: put description in parentheses at start
        formatted_text = f"({voice_description}){text}"
        
        # Get the VoxCPM model
        model = voxcpm_model.model
        
        # Generate audio with voice design
        wav = model.generate(
            text=formatted_text,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
        )
        
        # Convert to WAV bytes
        wav_bytes = audio_service.save_wav_file(wav, model.tts_model.sample_rate)
        
        logger.info("Voice design generation completed successfully")
        
        # Return as WAV file
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=voice_design_output.wav"}
        )
        
    except Exception as e:
        logger.error(f"Error in voice design generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate voice design: {str(e)}"
        )