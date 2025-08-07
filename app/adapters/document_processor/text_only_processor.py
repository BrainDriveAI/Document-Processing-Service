import spacy
from spacy_layout import spaCyLayout
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
import logging
from typing import List, Dict, Any, Tuple, Optional
from ...core.ports.document_processor import DocumentProcessor
from ...core.domain.entities.document import Document
from ...core.domain.entities.document_chunk import DocumentChunk
from ...core.domain.exceptions import DocumentProcessingError, InvalidDocumentTypeError
from ...core.ports.token_service import TokenService

class TextOnlyProcessor(DocumentProcessor):
    """Ultra-fast text-only processor for PDFs"""
    
    def __init__(
            self,
            token_service: TokenService,
            spacy_model: str = "en_core_web_sm",
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            min_chunk_size: int = 100
    ):
        self.logger = logging.getLogger(__name__)
        self.token_service = token_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        try:
            # Load spaCy model
            self.nlp = spacy.load(spacy_model)
            self.logger.info(f"Loaded spaCy model: {spacy_model}")
        except OSError:
            # Fallback to blank model if specific model not available
            self.nlp = spacy.blank("en")
            self.logger.warning(f"Could not load {spacy_model}, using blank English model")
        
        # Configure minimal PDF pipeline - TEXT ONLY
        self.pdf_pipeline_options = PdfPipelineOptions(
            # Disable ALL visual processing
            ocr_enabled=False,
            images_scale=0.0,  # No image processing
            generate_page_images=False,
            generate_table_images=False,
            generate_picture_images=False,
            
            # Disable structure detection
            table_structure_options={
                "do_cell_matching": False,
                "do_table_structure": False
            },
            
            # Minimal layout detection
            layout_model_options={
                "do_table_structure": False,
                "do_figure_extraction": False
            }
        )
        
        # Create text-only document converter
        self.document_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: self.pdf_pipeline_options
            }
        )
        
        # Fallback spacy-layout for non-PDF files
        self.layout = spaCyLayout(self.nlp)
        self.supported_types = ["pdf", "docx", "doc"]

    async def process_document(self, document: Document) -> Tuple[List[DocumentChunk], str]:
        """Process a document and return token-based chunks and complete text"""
        try:
            if document.document_type.value not in self.supported_types:
                raise InvalidDocumentTypeError(
                    f"Document type {document.document_type.value} not supported"
                )
            
            self.logger.info(f"Starting fast text extraction for document {document.id}")
            
            # Use different extraction methods based on file type
            if document.document_type.value == "pdf":
                complete_text = await self._extract_pdf_text_only(document.file_path)
            else:
                complete_text = await self._extract_text_with_spacy_layout(document.file_path)
            
            if not complete_text or len(complete_text.strip()) == 0:
                raise DocumentProcessingError("No text content extracted from document")
            
            self.logger.info(f"Extracted {len(complete_text)} characters from document {document.id}")
            
            # Create token-based chunks
            doc_chunks = await self._create_token_chunks(
                document=document,
                text=complete_text
            )
            
            self.logger.info(f"Created {len(doc_chunks)} chunks for document {document.id}")
            return doc_chunks, complete_text
            
        except Exception as e:
            self.logger.error(f"Failed to process document {document.filename}: {str(e)}")
            raise DocumentProcessingError(f"Failed to process document {document.filename}: {str(e)}")

    async def _extract_pdf_text_only(self, file_path: str) -> str:
        """Ultra-fast PDF text extraction with minimal processing"""
        try:
            self.logger.info(f"Using text-only extraction for PDF: {file_path}")
            
            # Convert with minimal processing
            conversion_result = self.document_converter.convert(file_path)
            
            if conversion_result.document:
                # Get raw text without any formatting
                complete_text = conversion_result.document.export_to_text()
                self.logger.debug(f"Text-only extracted length: {len(complete_text)}")
                return complete_text.strip()
            else:
                raise DocumentProcessingError("No document content found")
                
        except Exception as e:
            self.logger.error(f"Text-only extraction failed for {file_path}: {str(e)}")
            raise DocumentProcessingError(f"PDF text extraction failed: {str(e)}")

    async def _extract_text_with_spacy_layout(self, file_path: str) -> str:
        """Extract text from non-PDF files using spaCy Layout"""
        try:
            doc = self.layout(file_path)
            complete_text = doc.text.strip()
            self.logger.debug(f"SpaCy Layout text length: {len(complete_text)}")
            return complete_text
            
        except Exception as e:
            self.logger.error(f"SpaCy Layout extraction failed for {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Text extraction failed: {str(e)}")

    async def _create_token_chunks(
            self,
            document: Document,
            text: str
    ) -> List[DocumentChunk]:
        """Create chunks based on token count using recursive approach"""
        try:
            chunks = []

            # Split text into chunks using recursive token-based splitting
            text_chunks = await self._recursive_token_split(text)

            for i, chunk_text in enumerate(text_chunks):
                if len(chunk_text.strip()) < self.min_chunk_size:
                    continue

                # Calculate token count for this chunk
                token_count = self.token_service.count_tokens(chunk_text)

                # Create chunk with basic metadata
                chunk = DocumentChunk.create(
                    document_id=document.id,
                    content=chunk_text.strip(),
                    chunk_index=i,
                    metadata={
                        "document_filename": document.original_filename,
                        "document_type": document.document_type.value,
                        "chunk_token_count": token_count,
                        "chunk_char_count": len(chunk_text),
                        "processing_method": "simple_token_chunking"
                    }
                )

                chunks.append(chunk)

            return chunks

        except Exception as e:
            self.logger.error(f"Failed to create chunks: {str(e)}")
            raise DocumentProcessingError(f"Chunk creation failed: {str(e)}")

    def get_supported_types(self) -> List[str]:
        return self.supported_types.copy()
