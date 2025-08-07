from enum import Enum
from pathlib import Path


class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_filename(cls, filename: str) -> "DocumentType":
        """Determine document type from filename"""
        ext = Path(filename).suffix.lower().lstrip(".")
        
        type_mapping = {
            "pdf": cls.PDF,
            "docx": cls.DOCX,
            "doc": cls.DOC,
            "txt": cls.TXT
        }
        
        return type_mapping.get(ext, cls.UNKNOWN)
    
    @classmethod
    def from_mime_type(cls, mime_type: str) -> "DocumentType":
        """Determine document type from MIME type"""
        mime_mapping = {
            "application/pdf": cls.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": cls.DOCX,
            "application/msword": cls.DOC,
            "text/plain": cls.TXT
        }
        
        return mime_mapping.get(mime_type, cls.UNKNOWN)
    
    def get_mime_type(self) -> str:
        """Get MIME type for document type"""
        mime_mapping = {
            self.PDF: "application/pdf",
            self.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            self.DOC: "application/msword",
            self.TXT: "text/plain"
        }
        return mime_mapping.get(self, "application/octet-stream")
    