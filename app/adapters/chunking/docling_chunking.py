from typing import List, Dict, Any
import asyncio
from app.core.ports.chunking_strategy import ChunkingStrategy
from app.core.domain.entities.document_chunk import DocumentChunk
from app.core.domain.value_objects.chunk_metadata import ChunkMetadata
from app.core.domain.exceptions import ChunkingError

try:
    from docling.chunking import HierarchicalChunker
except ImportError:
    raise ImportError(
        "Docling is not installed. Please install it with: pip install docling"
    )


class DoclingHierarchicalChunking(ChunkingStrategy):
    """Docling hierarchical chunking strategy"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.chunker = HierarchicalChunker()
        
    async def create_chunks(
        self, 
        text: str, 
        metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Create chunks using Docling's hierarchical chunker
        
        Args:
            text: The text to chunk
            metadata: Document metadata
            
        Returns:
            List[DocumentChunk]: List of created chunks
        """
        try:
            document_id = metadata.get("document_id", "unknown")
            
            # Use Docling's chunker
            chunks_result = await asyncio.to_thread(
                self.chunker.chunk,
                text
            )
            
            document_chunks = []
            for i, chunk_text in enumerate(chunks_result):
                # Create chunk metadata
                chunk_metadata = ChunkMetadata.create_basic(
                    start_char=i * len(chunk_text),  # Simplified - Docling may provide better positions
                    end_char=(i + 1) * len(chunk_text),
                    page_number=None  # Would need to be extracted from Docling structure
                )
                
                # Create document chunk
                doc_chunk = DocumentChunk.create(
                    document_id=document_id,
                    text=chunk_text,
                    metadata=chunk_metadata,
                    sequence_number=i
                )
                
                document_chunks.append(doc_chunk)
            
            return document_chunks
            
        except Exception as e:
            raise ChunkingError(f"Docling chunking failed: {str(e)}") from e
    
    def get_strategy_name(self) -> str:
        return "docling_hierarchical"
