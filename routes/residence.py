from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session, joinedload
from .. import models, schemas
from ..database import get_db
from ..utils.jwt_handler import verify_token
from ..models import Residence, User, Villages, PelangganUsers
from datetime import datetime
from ..schemas import PairResidenceRequest

router = APIRouter(prefix="/residence", tags=["Residence"])

@router.get("/")
def get_residences(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pelanggan_users = db.query(PelangganUsers).filter(PelangganUsers.cms_users_id == user.id).all()
    if not pelanggan_users:
        raise HTTPException(status_code=404, detail="No residences found")

    residences = []
    for pu in pelanggan_users:
        residence = (db.query(
                            Residence
                            )
                        .options(joinedload(Residence.village))
                        .filter(Residence.id == pu.pelanggan_id)
                        .first()
                    )
        if residence:
            residence.paired_id = pu.id
            residences.append(residence)


    return (
        residences
    )

@router.get("/check/{pelanggan_id}")
def get_residence(pelanggan_id:str, current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    residence = (db.query(
                        Residence
                        )
                    .filter(Residence.pelanggan_id == pelanggan_id)
                    .first()
                )
    if not residence:
        raise HTTPException(status_code=404, detail="No residence found")

    return (
        residence
    )

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

@router.post("/pair/", status_code=http_status.HTTP_201_CREATED)
async def pair_residence(
    payload: PairResidenceRequest,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pelanggan_id = payload.pelanggan_id

    paired = (
        db.query(PelangganUsers)
        .filter(PelangganUsers.cms_users_id == user.id)
        .filter(PelangganUsers.pelanggan_id == pelanggan_id)
        .first()
    )

    if paired:
        raise HTTPException(
            status_code=400,
            detail="Residence already paired"
        )

    pair = PelangganUsers(
        cms_users_id=user.id,
        pelanggan_id=pelanggan_id,
    )

    db.add(pair)
    db.commit()
    db.refresh(pair)

    return {
        "success": True,
        "message": "Berhasil memasangkan pelanggan",
        "paired_id": pair.id
    }

@router.delete("/unpair/{paired_id}", status_code=http_status.HTTP_200_OK)
def unpair_residence(
    paired_id: int,
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    # 🔐 Load paired residence from DB
    pair = (
        db.query(PelangganUsers)
        .filter(PelangganUsers.id == paired_id)
        .filter(PelangganUsers.cms_users_id == current_user["user_id"])
        .first()
    )

    if not pair:
        raise HTTPException(
            status_code=404,
            detail="Data pasangan pelanggan tidak ditemukan"
        )

    db.delete(pair)
    db.commit()

    return {
        "success": True,
        "message": "Berhasil menghapus pasangan pelanggan"
    }
    
