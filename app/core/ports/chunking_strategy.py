from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..domain.entities.document_chunk import DocumentChunk
from ..domain.value_objects.chunk_metadata import ChunkMetadata


class ChunkingStrategy(ABC):
    """Port for chunking strategies"""
    
    @abstractmethod
    async def create_chunks(
        self,
        document_id: str,
        text: str,
        document_metadata: Dict[str, Any],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[DocumentChunk]:
        """
        Create chunks from text using specific strategy.
        
        Args:
            document_id: ID of the source document
            text: Text content to chunk
            document_metadata: Metadata from document processing
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of DocumentChunk entities
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return name of the chunking strategy"""
        pass
    
    @abstractmethod
    def get_optimal_chunk_size(self, text: str, target_size: int) -> int:
        """
        Calculate optimal chunk size based on content.
        
        Args:
            text: Text content
            target_size: Target chunk size
            
        Returns:
            Optimal chunk size
        """
        pass
    