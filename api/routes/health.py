"""
Health Check Routes
Endpoints for checking service health and model status.
"""
from fastapi import APIRouter
from api.models.voxcpm import voxcpm_model
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service status and model information
    """
    try:
        model_loaded = voxcpm_model.is_loaded()
        
        if model_loaded:
            model = voxcpm_model.model
            return {
                "status": "healthy",
                "model_loaded": True,
                "model_info": {
                    "sample_rate": model.tts_model.sample_rate,
                    "device": str(next(model.parameters()).device) if hasattr(model, 'parameters') else "unknown"
                }
            }
        else:
            return {
                "status": "unhealthy",
                "model_loaded": False,
                "detail": "Model not loaded"
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "detail": str(e)
        }

@router.get("/model-info")
async def get_model_info():
    """
    Get detailed model information.
    
    Returns:
        Model configuration and status
    """
    try:
        if not voxcpm_model.is_loaded():
            return {
                "status": "unhealthy",
                "model_loaded": False
            }
            
        model = voxcpm_model.model
        return {
            "status": "healthy",
            "model_loaded": True,
            "model_info": {
                "sample_rate": model.tts_model.sample_rate,
                "vocab_size": getattr(model.tts_model, 'vocab_size', 'unknown'),
                "device": str(next(model.parameters()).device) if hasattr(model, 'parameters') else "unknown"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "detail": str(e)
        }