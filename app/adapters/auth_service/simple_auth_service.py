import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from ...core.ports.auth_service import AuthService
from ...core.domain.entities.user import AuthenticatedUser

logger = logging.getLogger(__name__)

class SimpleAuthService(AuthService):
    def __init__(self, api_key: Optional[str], jwt_secret: Optional[str], jwt_algorithm: str = "HS256"):
        self.api_key = api_key
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
    
    async def verify_api_key(self, provided_key: str) -> Optional[AuthenticatedUser]:
        """Verify API key using secure comparison"""
        if not self.api_key or not provided_key:
            return None
        
        # Use secure comparison to prevent timing attacks
        if not hmac.compare_digest(self.api_key, provided_key):
            logger.warning(f"Invalid API key attempt")
            return None
        
        # Create a hash for user ID (don't log the actual key)
        key_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return AuthenticatedUser.create_api_key_user(key_hash)
    
    async def verify_jwt_token(self, token: str) -> Optional[AuthenticatedUser]:
        """Verify JWT token"""
        if not self.jwt_secret or not token:
            return None
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            return AuthenticatedUser.create_jwt_user(user_id, payload)
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
