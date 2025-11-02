from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core import security
from app.db import models, database, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    """Dependency to get a DB session."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """Dependency to get the current authenticated user."""
    token_data = security.decode_access_token(token)
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_user_optional(
    db: Session = Depends(get_db), token: str | None = Depends(oauth2_scheme)
) -> models.User | None:
    """Optional dependency to get user if token is provided, but doesn't fail."""
    if token is None:
        return None
    try:
        token_data = security.decode_access_token(token)
        user = db.query(models.User).filter(models.User.email == token_data.email).first()
        return user
    except HTTPException:
        return None