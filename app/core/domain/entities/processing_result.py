from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, UTC
from .document_chunk import DocumentChunk
from ..value_objects.processing_status import ProcessingStatus


@dataclass
class ProcessingResult:
    task_id: str
    document_id: str
    status: ProcessingStatus
    complete_text: str
    chunks: List[DocumentChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now(UTC))
    completed_at: Optional[datetime] = None
    
    @classmethod
    def create_processing(
        cls,
        task_id: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ProcessingResult":
        return cls(
            task_id=task_id,
            document_id=document_id,
            status=ProcessingStatus.PROCESSING,
            metadata=metadata or {}
        )
    
    def mark_completed(
        self,
        chunks: List[DocumentChunk],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Mark processing as completed"""
        self.status = ProcessingStatus.COMPLETED
        self.chunks = chunks
        self.processing_time = processing_time
        self.completed_at = datetime.now(UTC)
        if metadata:
            self.metadata.update(metadata)
    
    def mark_failed(self, error_message: str) -> None:
        """Mark processing as failed"""
        self.status = ProcessingStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(UTC)
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        return len(self.chunks)
    
    def get_total_content_length(self) -> int:
        """Get total content length across all chunks"""
        return sum(len(chunk.content) for chunk in self.chunks)
    