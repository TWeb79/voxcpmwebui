"""
VoxCPM Model Wrapper
Singleton wrapper for VoxCPM2 model to ensure efficient loading and usage.
"""
import os
import torch
from voxcpm import VoxCPM
from typing import Optional


class VoxCPMModel:
    """Singleton class for VoxCPM2 model management."""
    _instance: Optional['VoxCPMModel'] = None
    _model: Optional[VoxCPM] = None
    
    def __new__(cls) -> 'VoxCPMModel':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass  # Lazy loading — call load() explicitly or access .model property
    
    def _load_model(self) -> None:
        """Load the VoxCPM2 model."""
        try:
            # Check if we're in a Docker container or local environment
            model_path = os.getenv("VOXCPM_MODEL_PATH", "openbmb/VoxCPM2")
            
            self._model = VoxCPM.from_pretrained(
                model_path,
                load_denoiser=False,
            )
            # Move to GPU if available
            if torch.cuda.is_available():
                self._model = self._model.to("cuda")
        except Exception as e:
            raise RuntimeError(f"Failed to load VoxCPM model: {str(e)}")
    
    @property
    def model(self) -> VoxCPM:
        """Get the loaded VoxCPM model, loading it if necessary."""
        if self._model is None:
            self._load_model()
        return self._model
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None


# Global instance — model loads lazily on first property access
voxcpm_model = VoxCPMModel.__new__(VoxCPMModel)
VoxCPMModel._instance = voxcpm_model