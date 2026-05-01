"""
Ultimate Cloning Routes
Endpoints for ultimate voice cloning using VoxCPM2.
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
async def generate_ultimate_clone(
    text: str = Form(..., min_length=1, max_length=500),
    prompt_audio: UploadFile = File(None),
    prompt_text: str = Form(None),
    reference_audio: UploadFile = File(None)
):
    """
    Generate speech from text using ultimate voice cloning with VoxCPM2.
    
    Args:
        text: Input text to synthesize (1-500 characters)
        prompt_audio: Prompt audio file for ultimate cloning (optional)
        prompt_text: Transcript of the prompt audio (optional)
        reference_audio: Reference audio file for voice cloning (optional)
        
    Returns:
        WAV audio file
    """
    prompt_audio_path = None
    reference_audio_path = None
    try:
        logger.info(f"Generating ultimate clone for text: {text[:50]}...")
        
        # Get the VoxCPM model
        model = voxcpm_model.model
        
        # Handle prompt audio if provided
        if prompt_audio and prompt_audio.filename:
            # Validate file type
            if not prompt_audio.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=400,
                    detail="Prompt audio must be an audio file"
                )
            
            # Read uploaded file
            prompt_content = await prompt_audio.read()
            
            # Validate audio file
            if not audio_service.validate_audio_file(prompt_content):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid prompt audio file format"
                )
            
            # Create temporary file for prompt audio
            prompt_audio_path = file_service.create_temp_file_from_upload(
                prompt_content, prompt_audio.filename
            )
        
        # Handle reference audio if provided
        if reference_audio and reference_audio.filename:
            # Validate file type
            if not reference_audio.content_type.startswith('audio/'):
                raise HTTPException(
                    status_code=400,
                    detail="Reference audio must be an audio file"
                )
            
            # Read uploaded file
            reference_content = await reference_audio.read()
            
            # Validate audio file
            if not audio_service.validate_audio_file(reference_content):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid reference audio file format"
                )
            
            # Create temporary file for reference audio
            reference_audio_path = file_service.create_temp_file_from_upload(
                reference_content, reference_audio.filename
            )
        
        # Validate that at least prompt_audio and prompt_text are provided for ultimate cloning
        if not prompt_audio_path and not prompt_text:
            raise HTTPException(
                status_code=400,
                detail="Either prompt audio or prompt text must be provided for ultimate cloning"
            )
        
        # Generate audio with ultimate cloning
        wav = model.generate(
            text=text,
            prompt_wav_path=prompt_audio_path,
            prompt_text=prompt_text,
            reference_wav_path=reference_audio_path,
        )
        
        # Convert to WAV bytes
        wav_bytes = audio_service.save_wav_file(wav, model.tts_model.sample_rate)
        
        logger.info("Ultimate cloning completed successfully")
        
        # Return as WAV file
        return Response(
            content=wav_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=ultimate_clone_output.wav"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ultimate cloning: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate ultimate clone: {str(e)}"
        )
    finally:
        # Clean up temporary files
        if prompt_audio_path:
            file_service.delete_file(prompt_audio_path)
        if reference_audio_path:
            file_service.delete_file(reference_audio_path)