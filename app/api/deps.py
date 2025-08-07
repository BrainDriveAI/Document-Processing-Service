from fastapi import Request, HTTPException, Depends

# Port interfaces
from ..core.ports.document_processor import DocumentProcessor

# Use Cases
from ..core.use_cases.process_document import ProcessDocumentUseCase


# Dependency
def get_document_processor(request: Request) -> DocumentProcessor:
    dp = getattr(request.app.state, "document_processor", None)
    if dp is None:
        raise HTTPException(status_code=500, detail="DocumentProcessor not initialized")
    return dp


# Dependency provider for DocumentProcessingUseCase
def get_document_processing_use_case(
        document_processor: DocumentProcessor = Depends(get_document_processor),
) -> ProcessDocumentUseCase:
    return ProcessDocumentUseCase(
        document_processor=document_processor,
    )
