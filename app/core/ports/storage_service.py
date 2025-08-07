from abc import ABC, abstractmethod
from typing import Optional
import io


class StorageService(ABC):
    """Port for storage operations"""
    
    @abstractmethod
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """
        Save file and return storage path.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Storage path/identifier
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        Retrieve file content.
        
        Args:
            file_path: Storage path/identifier
            
        Returns:
            File content as bytes or None if not found
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_path: Storage path/identifier
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get file metadata.
        
        Args:
            file_path: Storage path/identifier
            
        Returns:
            File metadata dictionary or None if not found
        """
        pass
    