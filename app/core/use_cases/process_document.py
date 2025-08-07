import traceback
from typing import List, Optional
from app.core.domain.entities.document import Document
from app.core.domain.entities.document_chunk import DocumentChunk
from app.core.domain.entities.processing_result import ProcessingResult
from app.core.domain.value_objects.processing_status import ProcessingStatus
from app.core.ports.document_processor import DocumentProcessor
from app.core.ports.chunking_strategy import ChunkingStrategy
from app.core.ports.storage_service import StorageService
from app.core.domain.exceptions import DocumentProcessingError
import asyncio
import time
import uuid


class ProcessDocumentUseCase:
    def __init__(
        self,
        document_processor: DocumentProcessor
    ):
        self.document_processor = document_processor

    async def execute(
        self, 
        document: Document
    ) -> ProcessingResult:
        """
        Process a document and optionally return chunks
        
        Args:
            document: The document to process
            
        Returns:
            ProcessingResult containing the processed document or chunks
        """
        start_time = time.time()
        
        try:
            # Step 1: Process the document to extract content and metadata

            # Extract text and create basic chunks
            self.logger.info(f"Extracting text and creating chunks for document {document.id}")
            try:
                doc_chunks, complete_text = await self.document_processor.process_document(document)
                self.logger.info(f"Created {len(doc_chunks)} initial chunks from document {document.id}")
            except Exception as e:
                self.logger.error(f"Failed to process document for {document.id}: {str(e)}")
                self.logger.error(f"Document processor error traceback: {traceback.format_exc()}")
                raise DocumentProcessingError(f"Document processing failed: {str(e)}")

            if not doc_chunks:
                error_msg = "No chunks created from document"
                self.logger.error(f"{error_msg} for document {document.id}")
                raise DocumentProcessingError(error_msg)
            
            # Step 4: Create processing result
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                document_id=document.id,
                chunks=doc_chunks,
                complete_text=complete_text,
                metadata={},
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Create error result
            error_result = ProcessingResult(
                document_id=document.id,
                chunks=[],
                complete_text=None,
                metadata={"error": str(e)},
                processing_time=processing_time,
                status=ProcessingStatus.FAILED
            )
            
            raise DocumentProcessingError(
                f"Failed to process document {document.id}: {str(e)}"
            ) from e
        