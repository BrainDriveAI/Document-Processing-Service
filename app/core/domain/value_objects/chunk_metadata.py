from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class ChunkMetadata:
    # Content characteristics
    language: Optional[str] = None
    char_count: int = 0
    token_count: int = 0
    word_count: int = 0
    
    # Document structure
    section_title: Optional[str] = None
    section_level: int = 0
    page_number: Optional[int] = None
    paragraph_index: Optional[int] = None
    
    # Layout information
    bbox: Optional[List[float]] = None  # [x1, y1, x2, y2]
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    text_color: Optional[str] = None
    
    # Semantic information
    content_type: Optional[str] = None  # paragraph, header, table, list, etc.
    topics: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Processing metadata
    chunking_strategy: Optional[str] = None
    chunk_method: Optional[str] = None
    overlap_with_previous: bool = False
    overlap_with_next: bool = False
    
    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def add_custom_field(self, key: str, value: Any) -> None:
        """Add custom metadata field"""
        self.custom_fields[key] = value
    
    def get_custom_field(self, key: str, default: Any = None) -> Any:
        """Get custom metadata field"""
        return self.custom_fields.get(key, default)
    
    def update_content_stats(self, content: str) -> None:
        """Update content statistics"""
        self.char_count = len(content)
        self.word_count = len(content.split())
    
    def add_entity(self, entity_type: str, entity_text: str, 
                   start_char: int, end_char: int) -> None:
        """Add named entity"""
        self.entities.append({
            "type": entity_type,
            "text": entity_text,
            "start": start_char,
            "end": end_char
        })
    
    def add_topic(self, topic: str) -> None:
        """Add topic to chunk"""
        if topic not in self.topics:
            self.topics.append(topic)