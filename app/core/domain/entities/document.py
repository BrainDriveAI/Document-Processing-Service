from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, UTC
from uuid import uuid4
from ..value_objects.document_type import DocumentType
from ..value_objects.processing_status import ProcessingStatus


@dataclass
class Document:
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    filename: str = ""
    original_filename: str = ""
    file_path: str = ""
    file_size: int = 0
    document_type: DocumentType = DocumentType.UNKNOWN
    content_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        filename: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        document_type: DocumentType,
        content_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Document":
        return cls(
            filename=filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            created_at=datetime.now(UTC),
            document_type=document_type,
            content_hash=content_hash,
            metadata=metadata or {}
        )
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update document metadata"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    