class DocumentProcessingError(Exception):
    """Base exception for document processing errors"""
    pass


class InvalidDocumentTypeError(DocumentProcessingError):
    """Raised when document type is not supported"""
    pass


class DocumentCorruptedError(DocumentProcessingError):
    """Raised when document is corrupted or unreadable"""
    pass


class FileSizeExceededError(DocumentProcessingError):
    """Raised when file size exceeds limits"""
    pass


class ProcessingTimeoutError(DocumentProcessingError):
    """Raised when processing times out"""
    pass


class ChunkingError(DocumentProcessingError):
    """Raised when chunking fails"""
    pass


class TokenServiceError(DocumentProcessingError):
    """Raised when token service fails"""
    pass


class StorageError(DocumentProcessingError):
    """Raised when storage operations fail"""
    pass

class ProcessingStatusNotFoundError(DocumentProcessingError):
    """Raised when processing status for a document is not found"""
    pass

class DocumentValidationError(DocumentProcessingError):
    """Raised when document validation fails"""
    pass

class TokenizationError(DocumentProcessingError):
    """Raised when tokenization fails"""
    pass
