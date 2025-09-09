from fastapi import Request, HTTPException, Depends, Header
from typing import Optional

# Port interfaces
from ..core.ports.document_processor import DocumentProcessor
from ..core.ports.auth_service import AuthService
from ..core.domain.entities.user import AuthenticatedUser

# Use Cases
from ..core.use_cases.process_document import ProcessDocumentUseCase
from ..core.use_cases.authenticate_user import AuthenticateUserUseCase

# Errors
from ..core.domain.exceptions import AuthenticationError

# Config
from ..config import settings


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


def get_auth_service(request: Request) -> AuthService:
    auth_service = getattr(request.app.state, "auth_service", None)
    if auth_service is None:
        raise HTTPException(status_code=500, detail="AuthService not initialized")
    return auth_service

# Authentication use case dependency
def get_authenticate_user_use_case(
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(auth_service=auth_service)

# Authentication dependency using the use case
async def authenticate_user(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None),
    auth_use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case)
) -> Optional[AuthenticatedUser]:
    """
    Authenticate user using the authentication use case.
    Returns None if auth is disabled, raises HTTPException if auth fails.
    """
    # If auth is disabled, allow all requests
    if settings.disable_auth:
        return None
    
    try:
        # Extract bearer token if present
        bearer_token = None
        if authorization and authorization.startswith("Bearer "):
            bearer_token = authorization.split(" ", 1)[1]
        
        # Try to authenticate
        user = await auth_use_case.authenticate_request(
            api_key=x_api_key,
            bearer_token=bearer_token
        )
        
        if user is None:
            # No credentials provided
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Provide X-API-Key header or Authorization: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
