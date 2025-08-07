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

class OptimizedSpacyLayoutProcessor(DocumentProcessor):
    """Optimized spaCy Layout processor with faster PDF processing"""
    
    def __init__(
            self,
            token_service: TokenService,
            spacy_model: str = "en_core_web_sm",
            chunk_size: int = 1000,
            chunk_overlap: int = 200,
            min_chunk_size: int = 100,
            # PDF optimization parameters
            fast_pdf_mode: bool = True,
            ocr_enabled: bool = False,
            images_scale: float = 1.0,
            generate_page_images: bool = False,
            generate_table_images: bool = False,
            generate_picture_images: bool = False
    ):
        self.logger = logging.getLogger(__name__)
        self.token_service = token_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.fast_pdf_mode = fast_pdf_mode
        
        try:
            # Load spaCy model
            self.nlp = spacy.load(spacy_model)
            self.logger.info(f"Loaded spaCy model: {spacy_model}")
        except OSError:
            # Fallback to blank model if specific model not available
            self.nlp = spacy.blank("en")
            self.logger.warning(f"Could not load {spacy_model}, using blank English model")
        
        # Always initialize spaCy Layout as fallback
        self.layout = spaCyLayout(self.nlp)
        
        # Configure optimized PDF pipeline options
        if fast_pdf_mode:
            try:
                self.pdf_pipeline_options = PdfPipelineOptions(
                    # Disable OCR for faster processing (if your PDFs have extractable text)
                    ocr_enabled=ocr_enabled,
                    # Reduce image processing
                    images_scale=images_scale,
                    generate_page_images=generate_page_images,
                    generate_table_images=generate_table_images,
                    generate_picture_images=generate_picture_images,
                    # Optimize for speed
                    table_structure_options={
                        "do_cell_matching": False,  # Disable cell matching for speed
                        "do_table_structure": False  # Disable table structure detection
                    }
                )
                
                # Create optimized document converter
                self.document_converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: self.pdf_pipeline_options
                    }
                )
                
                # Use direct docling converter instead of spacy-layout for PDFs
                self.use_direct_docling = True
                self.logger.info("Initialized optimized docling converter for PDFs")
            except Exception as e:
                self.logger.warning(f"Failed to initialize optimized docling converter: {e}")
                self.logger.info("Falling back to standard spacy-layout processing")
                self.use_direct_docling = False
        else:
            self.use_direct_docling = False
            
        self.supported_types = ["pdf", "docx", "doc"]

    async def process_document(self, document: Document) -> Tuple[List[DocumentChunk], str]:
        """Process a document and return token-based chunks and complete text"""
        try:
            if document.document_type.value not in self.supported_types:
                raise InvalidDocumentTypeError(
                    f"Document type {document.document_type.value} not supported"
                )
            
            self.logger.info(f"Starting text extraction for document {document.id}")
            
            # Use optimized extraction for PDFs
            if document.document_type.value == "pdf" and self.use_direct_docling:
                complete_text = await self._extract_text_with_docling(document.file_path)
            else:
                complete_text = await self._extract_text_only(document.file_path)
            
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

    async def _extract_text_with_docling(self, file_path: str) -> str:
        """Fast text extraction using direct docling converter"""
        try:
            self.logger.info(f"Using optimized docling extraction for PDF: {file_path}")
            
            # Convert document using optimized pipeline
            conversion_result = self.document_converter.convert(file_path)
            
            # Extract text from the first (and likely only) document
            if conversion_result.document:
                complete_text = conversion_result.document.export_to_text()
                self.logger.debug(f"Docling extracted text length: {len(complete_text)}")
                return complete_text.strip()
            else:
                raise DocumentProcessingError("No document content found in conversion result")
                
        except Exception as e:
            self.logger.error(f"Failed to extract text with docling from {file_path}: {str(e)}")
            # Fallback to spacy-layout
            self.logger.info("Falling back to spacy-layout extraction")
            return await self._extract_text_only(file_path)

    async def _extract_text_only(self, file_path: str) -> str:
        """Extract only text content from document using spaCy Layout"""
        try:
            # Process document with spaCy Layout
            doc = self.layout(file_path)
            # Simply return the full text - no complex structure extraction
            complete_text = doc.text.strip()
            self.logger.debug(f"SpaCy Layout text length: {len(complete_text)}")
            return complete_text
            
        except Exception as e:
            self.logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Text extraction failed: {str(e)}")

    # Keep all your existing chunking methods unchanged
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
                        "processing_method": "optimized_token_chunking"
                    }
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to create chunks: {str(e)}")
            raise DocumentProcessingError(f"Chunk creation failed: {str(e)}")

    # Keep all your existing methods for chunking
    async def _recursive_token_split(self, text: str) -> List[str]:
        """Recursively split text based on token count"""
        try:
            # Check if text fits in one chunk
            token_count = self.token_service.count_tokens(text)
            if token_count <= self.chunk_size:
                return [text]
            
            # Text is too large, need to split
            chunks = []
            
            # Try splitting by paragraphs first
            paragraphs = text.split('\n\n')
            if len(paragraphs) > 1:
                current_chunk = ""
                current_tokens = 0
                
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    if not paragraph:
                        continue
                    
                    para_tokens = self.token_service.count_tokens(paragraph)
                    
                    # If single paragraph is too large, split it further
                    if para_tokens > self.chunk_size:
                        # Save current chunk if it has content
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                            current_tokens = 0
                        
                        # Recursively split the large paragraph
                        para_chunks = await self._split_large_paragraph(paragraph)
                        chunks.extend(para_chunks)
                    else:
                        # Check if adding this paragraph exceeds chunk size
                        if current_tokens + para_tokens > self.chunk_size and current_chunk:
                            # Save current chunk and start new one
                            chunks.append(current_chunk.strip())
                            current_chunk = paragraph
                            current_tokens = para_tokens
                        else:
                            # Add to current chunk
                            if current_chunk:
                                current_chunk += "\n\n" + paragraph
                                current_tokens += para_tokens
                            else:
                                current_chunk = paragraph
                                current_tokens = para_tokens
                
                # Add remaining chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
            else:
                # Single paragraph, split by sentences
                chunks = await self._split_large_paragraph(text)
            
            # Apply overlap if we have multiple chunks
            if len(chunks) > 1 and self.chunk_overlap > 0:
                chunks = await self._apply_overlap(chunks)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed in recursive token split: {str(e)}")
            # Fallback to simple character-based splitting
            return self._fallback_character_split(text)
    
    async def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph by sentences"""
        try:
            # Split by sentences using spaCy
            doc = self.nlp(paragraph)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            
            if not sentences:
                return [paragraph]
            
            chunks = []
            current_chunk = ""
            current_tokens = 0
            
            for sentence in sentences:
                sent_tokens = self.token_service.count_tokens(sentence)
                
                # If single sentence is too large, split by words
                if sent_tokens > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                        current_tokens = 0
                    
                    # Split sentence by words
                    word_chunks = await self._split_by_words(sentence)
                    chunks.extend(word_chunks)
                else:
                    if current_tokens + sent_tokens > self.chunk_size and current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = sentence
                        current_tokens = sent_tokens
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                            current_tokens += sent_tokens
                        else:
                            current_chunk = sentence
                            current_tokens = sent_tokens
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to split paragraph: {str(e)}")
            return [paragraph]
    
    async def _split_by_words(self, text: str) -> List[str]:
        """Split text by words when sentences are too large"""
        words = text.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            test_chunk = f"{current_chunk} {word}".strip()
            test_tokens = self.token_service.count_tokens(test_chunk)
            
            if test_tokens > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = word
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between chunks"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
                continue
            
            # Get overlap from previous chunk
            prev_chunk = chunks[i - 1]
            overlap_text = await self._get_overlap_text(prev_chunk, self.chunk_overlap)
            
            # Combine overlap with current chunk
            if overlap_text:
                overlapped_chunk = f"{overlap_text} {chunk}"
                overlapped_chunks.append(overlapped_chunk)
            else:
                overlapped_chunks.append(chunk)
        
        return overlapped_chunks
    
    async def _get_overlap_text(self, text: str, target_tokens: int) -> str:
        """Get the last N tokens worth of text for overlap"""
        try:
            # Split into words and work backwards
            words = text.split()
            overlap_words = []
            current_tokens = 0
            
            for word in reversed(words):
                test_text = " ".join([word] + overlap_words)
                test_tokens = self.token_service.count_tokens(test_text)
                
                if test_tokens > target_tokens:
                    break
                
                overlap_words.insert(0, word)
                current_tokens = test_tokens
            
            return " ".join(overlap_words)
            
        except Exception as e:
            self.logger.error(f"Failed to get overlap text: {str(e)}")
            return ""
    
    def _fallback_character_split(self, text: str) -> List[str]:
        """Fallback method for splitting text by characters"""
        chunk_size_chars = self.chunk_size * 4  # Rough estimate: 1 token ≈ 4 chars
        chunks = []
        
        for i in range(0, len(text), chunk_size_chars):
            chunk = text[i:i + chunk_size_chars]
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks

    def get_supported_types(self) -> List[str]:
        """Return list of supported document types"""
        return self.supported_types.copy()
