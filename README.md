# BrainDrive Document AI - Project Structure

## Overview
Standalone document processing API service following Clean Architecture principles. Processes documents and returns structured chunks with metadata.

## Project Structure

```
braindrive-document-ai/
├── README.md
├── LICENSE
├── pyproject.toml
├── poetry.lock
├── .env.example
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── start.sh
├── project_structure.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_document_processor.py
│   │   ├── test_chunking_strategies.py
│   │   └── test_use_cases.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   └── test_document_processing.py
│   └── fixtures/
│       ├── sample.pdf
│       ├── sample.docx
│       └── sample.txt
├── docs/
│   ├── api.md
│   ├── architecture.md
│   └── deployment.md
├── scripts/
│   ├── setup.sh
│   └── health_check.sh
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document.py
│   │   │   │   ├── document_chunk.py
│   │   │   │   └── processing_result.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document_type.py
│   │   │   │   ├── chunk_metadata.py
│   │   │   │   └── processing_status.py
│   │   │   └── exceptions.py
│   │   ├── ports/
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py
│   │   │   ├── chunking_strategy.py
│   │   │   ├── token_service.py
│   │   │   └── storage_service.py
│   │   └── use_cases/
│   │       ├── __init__.py
│   │       ├── process_document.py
│   │       ├── get_processing_status.py
│   │       └── validate_document.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── document_processing/
│   │   │   ├── __init__.py
│   │   │   ├── spacy_layout_processor.py
│   │   │   └── text_extractor.py
│   │   ├── chunking/
│   │   │   ├── __init__.py
│   │   │   ├── hierarchical_chunking.py
│   │   │   ├── semantic_chunking.py
│   │   │   ├── token_based_chunking.py
│   │   │   └── adaptive_chunking.py
│   │   ├── token_service/
│   │   │   ├── __init__.py
│   │   │   └── tiktoken_service.py
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── local_storage.py
│   │       └── temp_storage.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── document_processing.py
│   │   │   └── status.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── document_request.py
│   │       ├── document_response.py
│   │       └── processing_response.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   ├── file_handler.py
│   │   └── validation.py
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       ├── text_utils.py
│       └── validation_utils.py
├── data/
│   ├── temp/
│   └── uploads/
└── logs/
    ├── app.log
    └── error.log
```

## Key Features

### 1. Clean Architecture Compliance
- **Domain Layer**: Pure business logic without external dependencies
- **Ports**: Interfaces defining contracts
- **Adapters**: Implementations of external services
- **Use Cases**: Application-specific business rules

### 2. Document Processing Capabilities
- **Multi-format Support**: PDF, DOCX, DOC, TXT
- **Advanced Chunking**: Hierarchical, semantic, token-based, adaptive
- **Metadata Extraction**: Rich metadata from document structure
- **spaCy Layout Integration**: Sophisticated document understanding

### 3. API Design
- **RESTful Endpoints**: Clean, intuitive API design
- **Async Processing**: Handle large documents efficiently
- **Status Tracking**: Monitor processing progress
- **Error Handling**: Comprehensive error reporting

### 4. Extensibility
- **Plugin Architecture**: Easy to add new processors
- **Strategy Pattern**: Swappable chunking strategies
- **Configuration-driven**: Flexible processing parameters

## Core Components

### Document Processor
```python
class DocumentProcessor(ABC):
    @abstractmethod
    async def process_document(self, document: Document) -> ProcessingResult:
        """Process document and return structured chunks"""
        pass
```

### Chunking Strategy
```python
class ChunkingStrategy(ABC):
    @abstractmethod
    async def create_chunks(self, text: str, metadata: dict) -> List[DocumentChunk]:
        """Create chunks from text with strategy-specific logic"""
        pass
```

### Processing Result
```python
class ProcessingResult:
    document_id: str
    chunks: List[DocumentChunk]
    metadata: dict
    processing_time: float
    status: ProcessingStatus
```

## API Endpoints

### POST /api/v1/process
Process a document and return structured chunks

### GET /api/v1/status/{task_id}
Get processing status for async operations

### POST /api/v1/validate
Validate document before processing

### GET /api/v1/health
Health check endpoint

## Configuration Options

- **Chunking Strategy**: hierarchical, semantic, token-based, adaptive
- **Chunk Size**: Configurable token/character limits
- **Overlap**: Configurable overlap between chunks
- **Metadata Extraction**: Configurable metadata fields
- **Processing Mode**: Sync vs async processing

## Docker Support
- **Multi-stage Build**: Optimized container size
- **Health Checks**: Container health monitoring
- **Environment Variables**: Flexible configuration
- **Volume Mounts**: Persistent storage options

## Testing Strategy
- **Unit Tests**: Test individual components
- **Integration Tests**: Test API endpoints
- **Performance Tests**: Benchmark processing speed
- **Document Tests**: Test with various document types

## Monitoring & Observability
- **Structured Logging**: JSON-formatted logs
- **Metrics Collection**: Processing metrics
- **Error Tracking**: Comprehensive error reporting
- **Performance Monitoring**: Response time tracking

## Deployment Options
- **Docker Compose**: Local development
- **Kubernetes**: Production deployment
- **Cloud Functions**: Serverless deployment
- **Standalone**: Direct installation

This structure provides a solid foundation for a standalone document processing API that can be easily integrated with your main chat application while maintaining clean architecture principles and extensibility.
