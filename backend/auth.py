"""
auth.py — Everything related to passwords and login tokens.

This file handles two things:
  1. Passwords — hashing them before storing, and checking them at login.
  2. JWT Tokens — creating them after login, and reading them on each request.

WHY DO WE HASH PASSWORDS?
  If our database ever gets hacked, we don't want attackers to see real passwords.
  A hash is a one-way scramble. "hello123" → "$2b$12$Xk8...". You can't reverse it.
  We verify by hashing the input again and comparing the hash — never the plain text.

WHY JWT TOKENS?
  After you log in, we can't ask for your password on every request.
  Instead, we give you a "token" — like a wristband at an event.
  You show the wristband (token) on every request and we trust you without re-checking your ID.
  Tokens expire (default: 7 days), so even if stolen, they eventually become useless.
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
import models

# -----------------------------------------------------------------
# SECRET KEY — used to sign and verify JWT tokens.
# In production, put this in an environment variable, NOT in code!
# If someone gets this key, they can forge login tokens.
# -----------------------------------------------------------------
SECRET_KEY = "flipearn-super-secret-key-change-this-in-production"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_DAYS = 7

# -----------------------------------------------------------------
# Password context — tells passlib to use bcrypt for hashing.
# bcrypt is intentionally slow, making brute-force attacks hard.
# -----------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------------------------------------------
# HTTPBearer scheme — FastAPI reads the "Authorization: Bearer <token>"
# header automatically. In Swagger UI this shows a simple "Value" box
# where you just paste your token — no client_id or client_secret needed.
# -----------------------------------------------------------------
bearer_scheme = HTTPBearer()


# ===================== PASSWORD FUNCTIONS ========================

def hash_password(plain_password: str) -> str:
    """Turn a plain text password into a secure hash."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches a stored hash. Returns True/False."""
    return pwd_context.verify(plain_password, hashed_password)


# ===================== TOKEN FUNCTIONS ==========================

def create_access_token(data: dict) -> str:
    """
    Create a JWT token that encodes user info (like user_id and role).
    The token is signed with our SECRET_KEY so we know it wasn't tampered with.
    """
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire})              # token will stop working after this time
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode a JWT token and return its payload.
    Raises an error if the token is invalid or expired.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ===================== DEPENDENCY FUNCTIONS =====================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    FastAPI dependency — runs before any route that needs a logged-in user.

    Flow:
      1. Extract the JWT token from the "Authorization" header.
      2. Decode it to get the user_id.
      3. Look up the user in the database.
      4. Return the user object so the route can use it.

    Usage in a route:
      @router.get("/me")
      def my_profile(current_user = Depends(get_current_user)):
          return current_user
    """
    payload = decode_token(credentials.credentials)
    user_id: int = int(payload.get("sub"))

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User account no longer exists.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been suspended.")

    return user


def get_current_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    FastAPI dependency — same as get_current_user, but also checks for admin role.
    Use this on routes that only admins should access (e.g. approve listings).
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to do this. Admin access required."
        )
    return current_user
