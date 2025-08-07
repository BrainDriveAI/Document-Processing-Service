from app.core.domain.entities.document import Document
from app.core.domain.value_objects.document_type import DocumentType
from app.core.domain.exceptions import DocumentValidationError
from typing import List
import mimetypes
import os


class ValidateDocumentUseCase:
    def __init__(self, max_file_size: int = 50 * 1024 * 1024):  # 50MB default
        self.max_file_size = max_file_size
        self.supported_types = [
            DocumentType.PDF,
            DocumentType.DOCX,
            DocumentType.DOC,
            DocumentType.TXT
        ]
        
    async def execute(self, document: Document) -> bool:
        """
        Validate a document before processing
        
        Args:
            document: The document to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            DocumentValidationError: If validation fails
        """
        errors = []
        
        # Check file size
        if document.size > self.max_file_size:
            errors.append(f"File size {document.size} exceeds maximum {self.max_file_size}")
        
        # Check file type
        if document.document_type not in self.supported_types:
            errors.append(f"Document type {document.document_type} not supported")
        
        # Check if file exists and is readable
        if document.file_path and not os.path.exists(document.file_path):
            errors.append(f"File not found: {document.file_path}")
        
        # Check if file is not empty
        if document.size == 0:
            errors.append("Document is empty")
        
        if errors:
            raise DocumentValidationError("; ".join(errors))
        
        return True
