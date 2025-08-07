from typing import Optional
from app.core.domain.entities.processing_result import ProcessingResult
from app.core.ports.storage_service import StorageService
from app.core.domain.exceptions import ProcessingStatusNotFoundError


class GetProcessingStatusUseCase:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service
    
    async def execute(self, document_id: str) -> Optional[ProcessingResult]:
        """
        Get processing status for a document
        
        Args:
            document_id: The ID of the document
            
        Returns:
            ProcessingResult if found, None otherwise
            
        Raises:
            ProcessingStatusNotFoundError: If status not found
        """
        try:
            result = await self.storage_service.get_processing_result(document_id)
            if result is None:
                raise ProcessingStatusNotFoundError(f"Processing status not found for document {document_id}")
            return result
        except Exception as e:
            raise ProcessingStatusNotFoundError(f"Error retrieving status for document {document_id}: {str(e)}")
