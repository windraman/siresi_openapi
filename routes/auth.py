from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt
from .. import models, schemas
from ..database import get_db
from ..utils.jwt_handler import create_access_token
from ..config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.nik == request.nik).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.password:
        raise HTTPException(status_code=400, detail="User has no password set")

    hashed = user.password.encode("utf-8")
    if hashed.startswith(b"$2y$"):
        hashed = hashed.replace(b"$2y$", b"$2b$")

    if not bcrypt.checkpw(request.password.encode("utf-8"), hashed):
        raise HTTPException(status_code=401, detail="Invalid NIK or password")

    # ✅ Create JWT token
    access_token = create_access_token(data={"sub": str(user.nik), "user_id": user.id})
    priv = db.query(models.CmsPrivilege).filter(models.CmsPrivilege.id == user.id_cms_privileges).first()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nik": user.nik,
            "name": user.display_name or user.name,
            "role_id": user.id_cms_privileges,
            "role": priv.name if priv else None,
        }
    }
