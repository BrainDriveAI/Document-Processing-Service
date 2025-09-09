from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen=True)
class AuthenticatedUser:
    """Represents an authenticated user/client"""
    id: str
    name: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create_api_key_user(cls, api_key_hash: str) -> "AuthenticatedUser":
        """Create user from API key"""
        return cls(
            id=f"api_key_{api_key_hash[:8]}",
            name="API Key User",
            permissions={"upload_documents": True}
        )
    
    @classmethod
    def create_jwt_user(cls, user_id: str, claims: Dict[str, Any]) -> "AuthenticatedUser":
        """Create user from JWT claims"""
        return cls(
            id=user_id,
            name=claims.get("name"),
            permissions=claims.get("permissions", {"upload_documents": True})
        )
