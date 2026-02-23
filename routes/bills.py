from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..utils.jwt_handler import verify_token
from ..models import User, Tagihan, Tarif, Residence
from datetime import datetime

router = APIRouter(prefix="/tagihan", tags=["Tagihan"])

@router.get("/{pelanggan_id}/{year}")
def get_bills(pelanggan_id: str,year: int,current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pelanggan = db.query(Residence).filter(Residence.pelanggan_id == pelanggan_id).first()
    if not pelanggan:
        raise HTTPException(status_code=404, detail="Pelanggan not found")

    current_datetime = datetime.now()

    for i in range(current_datetime.month):
        tagihan = db.query(Tagihan).filter(Tagihan.residence_id == pelanggan.id).filter(Tagihan.bulan == i+1).filter(Tagihan.tahun == year).first()
        if not tagihan:
            tarif = db.query(Tarif).order_by(Tarif.berlaku.desc()).first()
            tagihan = Tagihan(
                residence_id=pelanggan.id,
                pelanggan_id=pelanggan_id,
                bulan=i+1,
                tahun=year,
                jumlah=tarif.nominal if tarif else 5000,
                status="Belum Bayar",
            )
            db.add(tagihan)
            db.commit()
            db.refresh(tagihan)


    return (
        db.query(Tagihan).filter(Tagihan.residence_id == pelanggan.id).filter(Tagihan.tahun == year).all()
    )