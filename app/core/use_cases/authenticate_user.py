import logging
from typing import Optional
from ..ports.auth_service import AuthService
from ..domain.entities.user import AuthenticatedUser
from ..domain.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class AuthenticateUserUseCase:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def authenticate_with_api_key(self, api_key: str) -> AuthenticatedUser:
        """Authenticate user with API key"""
        if not api_key:
            raise AuthenticationError("API key is required")
        
        user = await self.auth_service.verify_api_key(api_key)
        if not user:
            logger.warning("Failed API key authentication attempt")
            raise AuthenticationError("Invalid API key")
        
        logger.info(f"Successful API key authentication for user: {user.id}")
        return user
    
    async def authenticate_with_jwt(self, token: str) -> AuthenticatedUser:
        """Authenticate user with JWT token"""
        if not token:
            raise AuthenticationError("JWT token is required")
        
        user = await self.auth_service.verify_jwt_token(token)
        if not user:
            logger.warning("Failed JWT authentication attempt")
            raise AuthenticationError("Invalid or expired JWT token")
        
        logger.info(f"Successful JWT authentication for user: {user.id}")
        return user
    
    async def authenticate_request(
        self, 
        api_key: Optional[str] = None, 
        bearer_token: Optional[str] = None
    ) -> Optional[AuthenticatedUser]:
        """
        Authenticate a request using available credentials.
        Returns None if no credentials provided, raises AuthenticationError if invalid.
        """
        # Try API key first
        if api_key:
            return await self.authenticate_with_api_key(api_key)
        
        # Try JWT token
        if bearer_token:
            return await self.authenticate_with_jwt(bearer_token)
        
        # No credentials provided
        return None
