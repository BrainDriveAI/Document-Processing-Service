from abc import ABC, abstractmethod
from typing import Optional
from ..domain.entities.user import AuthenticatedUser

class AuthService(ABC):
    @abstractmethod
    async def verify_api_key(self, api_key: str) -> Optional[AuthenticatedUser]:
        """Verify API key and return authenticated user if valid"""
        pass
    
    @abstractmethod
    async def verify_jwt_token(self, token: str) -> Optional[AuthenticatedUser]:
        """Verify JWT token and return authenticated user if valid"""
        pass
