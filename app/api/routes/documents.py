import shutil
import logging
import traceback
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ...config import settings
from ...core.use_cases.process_document import ProcessDocumentUseCase
from ...core.domain.entities.document import Document as DomainDocument
from ...core.domain.entities.user import AuthenticatedUser
from ...core.domain.value_objects.document_type import DocumentType
from ...core.domain.exceptions import InvalidDocumentTypeError
from ...api.deps import (
    get_document_processing_use_case,
    authenticate_user
)

router = APIRouter()

# Set up logger for this module
logger = logging.getLogger(__name__)

def determine_document_type(filename: str) -> DocumentType:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "pdf":
        return DocumentType.PDF
    elif ext == "docx":
        return DocumentType.DOCX
    elif ext == "doc":
        return DocumentType.DOC
    else:
        raise InvalidDocumentTypeError(f"Unsupported file extension: {ext}")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_use_case: ProcessDocumentUseCase = Depends(get_document_processing_use_case),
    current_user: Optional[AuthenticatedUser] = Depends(authenticate_user)
):
    # Log authenticated user (if auth is enabled)
    if current_user:
        logger.info(f"Document upload by authenticated user: {current_user.id}")

    saved_path = None
    
    try:
        # 2. Determine type
        try:
            doc_type = determine_document_type(file.filename)
        except InvalidDocumentTypeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        uploads_base = Path(settings.UPLOADS_DIR)
        collection_dir = uploads_base
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        import uuid
        new_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix.lower()
        saved_filename = f"{new_id}{ext}"
        saved_path = collection_dir / saved_filename
        
        try:
            # Write file
            with open(saved_path, "wb") as out_file:
                shutil.copyfileobj(file.file, out_file)
            logger.info(f"File saved to: {saved_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        finally:
            file.file.close()
        
        # 4. Create DomainDocument entity
        file_stat = saved_path.stat()
        domain_doc = DomainDocument.create(
            filename=saved_filename,
            original_filename=file.filename,
            file_path=str(saved_path),
            file_size=file_stat.st_size,
            document_type=doc_type,
            metadata={}
        )
        logger.info(f"Created domain document: {domain_doc.id}")
        
        # Process the document
        result = await document_use_case.document_processor.process_document(domain_doc)
        
        # Clean up the uploaded file after successful processing
        if saved_path and saved_path.exists():
            try:
                saved_path.unlink()
                logger.info(f"Successfully deleted uploaded file: {saved_path}")
            except Exception as e:
                logger.warning(f"Failed to delete uploaded file {saved_path}: {e}")
        
        return result
        
    except Exception as e:
        # If processing fails, still try to clean up the file
        if saved_path and saved_path.exists():
            try:
                saved_path.unlink()
                logger.info(f"Cleaned up uploaded file after processing error: {saved_path}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup file {saved_path} after error: {cleanup_error}")
        
        # Re-raise the original exception
        raise
