from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
from uuid import uuid4
from ..value_objects.chunk_metadata import ChunkMetadata


@dataclass
class DocumentChunk:
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    content: str = ""
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    token_count: int = 0
    metadata: ChunkMetadata = field(default_factory=ChunkMetadata)
    
    @classmethod
    def create(
        cls,
        document_id: str,
        content: str,
        chunk_index: int,
        # start_char: int = 0,
        # end_char: int = 0,
        # token_count: int = 0,
        metadata: Optional[ChunkMetadata] = None
    ) -> "DocumentChunk":
        return cls(
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            created_at=datetime.now(UTC),
            # start_char=start_char,
            # end_char=end_char,
            # token_count=token_count,
            metadata=metadata or ChunkMetadata()
        )
    
    def update_content(self, content: str) -> None:
        """Update chunk content"""
        self.content = content
        self.end_char = self.start_char + len(content)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add custom metadata"""
        self.metadata.add_custom_field(key, value)
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return getattr(self.metadata, key, 
                      self.metadata.custom_fields.get(key, default))
    