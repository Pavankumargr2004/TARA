"""
OAuth2 & Role-Based Access Control (RBAC) Module for Enterprise Deployment.
Provides JWT authentication, password hashing, and role permission guards.
"""
import hmac
import hashlib
import base64
import json
import time
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import User

# Standard Roles
ROLES = {
    "SYSTEM_ARCHITECT": "System Architect",
    "CYBERSECURITY_ENGINEER": "Cybersecurity Engineer",
    "LEAD_AUDITOR": "Lead Security Auditor",
    "GUEST": "Guest Viewer"
}

SECRET_KEY = "AUTOSEC_ISO21434_SUPER_SECRET_PRODUCTION_KEY_2026"
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 86400  # 24 Hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hash password using PBKDF2 HMAC SHA-256 for zero-dependency security."""
    salt = b"autosec_salt_2026"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)


def create_access_token(data: dict, expires_in: int = TOKEN_EXPIRE_SECONDS) -> str:
    """Create a signed JWT token without external dependencies."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in
    
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        encoded_header, encoded_payload, encoded_signature = parts
        
        # Verify signature
        signature_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_sig = base64.urlsafe_b64encode(
            hmac.new(SECRET_KEY.encode(), signature_input, hashlib.sha256).digest()
        ).decode().rstrip("=")
        
        if not hmac.compare_digest(encoded_signature, expected_sig):
            return None
        
        # Decode payload
        rem = len(encoded_payload) % 4
        if rem > 0:
            encoded_payload += "=" * (4 - rem)
        
        payload_bytes = base64.urlsafe_b64decode(encoded_payload.encode())
        payload = json.loads(payload_bytes.decode())
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None


def init_default_users(db: Session):
    """Seed pre-configured default users for instant enterprise testing."""
    default_users = [
        {"username": "admin", "email": "admin@autosec.tara", "password": "Admin@123", "role": ROLES["SYSTEM_ARCHITECT"]},
        {"username": "engineer", "email": "engineer@autosec.tara", "password": "Eng@123", "role": ROLES["CYBERSECURITY_ENGINEER"]},
        {"username": "auditor", "email": "auditor@autosec.tara", "password": "Auditor@123", "role": ROLES["LEAD_AUDITOR"]},
        {"username": "guest", "email": "guest@autosec.tara", "password": "Guest@123", "role": ROLES["GUEST"]},
    ]
    
    for u in default_users:
        existing = db.query(User).filter(User.username == u["username"]).first()
        if not existing:
            new_user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                is_active=1
            )
            db.add(new_user)
    db.commit()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency: Extract and validate user from OAuth2 bearer token."""
    if not token:
        # Fallback default engineer for unauthenticated dev requests
        user = db.query(User).filter(User.username == "engineer").first()
        if not user:
            init_default_users(db)
            user = db.query(User).filter(User.username == "engineer").first()
        return user

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


class RoleChecker:
    """Dependency Guard: Enforces Role-Based Access Control (RBAC)."""
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' lacks permission for this action. Allowed: {self.allowed_roles}"
            )
        return user
