"""
File Service
Handles temporary file storage, cleanup, and file operations.
"""
import os
import tempfile
import uuid
from typing import BinaryIO, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileService:
    """Service for file handling operations."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize file service.
        
        Args:
            temp_dir: Directory for temporary files. If None, uses system temp.
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileService initialized with temp directory: {self.temp_dir}")
    
    def create_temp_file(self, content: bytes, suffix: str = "") -> str:
        """
        Create a temporary file with the given content.
        
        Args:
            content: File content as bytes
            suffix: File extension (e.g., '.wav')
            
        Returns:
            Path to the created temporary file
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{suffix}"
        filepath = self.temp_dir / filename
        
        # Write content to file
        with open(filepath, "wb") as f:
            f.write(content)
            
        logger.debug(f"Created temporary file: {filepath}")
        return str(filepath)
    
    def create_temp_file_from_upload(self, file_content: bytes, 
                                   original_filename: str) -> str:
        """
        Create a temporary file from uploaded content.
        
        Args:
            file_content: File content as bytes
            original_filename: Original filename to extract extension
            
        Returns:
            Path to the created temporary file
        """
        # Extract file extension
        _, ext = os.path.splitext(original_filename)
        return self.create_temp_file(file_content, ext)
    
    def read_file(self, filepath: str) -> bytes:
        """
        Read file content as bytes.
        
        Args:
            filepath: Path to file
            
        Returns:
            File content as bytes
        """
        with open(filepath, "rb") as f:
            return f.read()
    
    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file.
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            True if deleted, False if file didn't exist or error occurred
        """
        try:
            os.remove(filepath)
            logger.debug(f"Deleted temporary file: {filepath}")
            return True
        except OSError as e:
            logger.warning(f"Failed to delete file {filepath}: {e}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
            
        Returns:
            Number of files deleted
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0
        
        for filepath in self.temp_dir.iterdir():
            if filepath.is_file():
                file_age = current_time - filepath.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        filepath.unlink()
                        deleted_count += 1
                        logger.debug(f"Cleaned up old temporary file: {filepath}")
                    except OSError as e:
                        logger.warning(f"Failed to delete file {filepath} during cleanup: {e}")
                        pass  # File might be in use, skip it
                        
        logger.info(f"Cleaned up {deleted_count} temporary files")
        return deleted_count


# Global instance
file_service = FileService()