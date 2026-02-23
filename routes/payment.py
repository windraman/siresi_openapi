import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Payment, User, Tagihan, Residence
from ..utils.jwt_handler import verify_token
from datetime import datetime,timedelta

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.get("/{year}")
def history(year: int,current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    history = []

    pelanggans = db.query(Residence).filter(Residence.cms_users_id == user.id).all()
    if not pelanggans:
        raise HTTPException(status_code=404, detail="Pelanggan not found")

    for pelanggan in pelanggans:
        tagihans = (db.query(Tagihan)
                    .filter(Tagihan.pelanggan_id == pelanggan.pelanggan_id)
                    .filter(Tagihan.tahun == year)
                    .all()
                    )

        
        
        for tagihan in tagihans:
            payments = (db.query(Payment)
                        .filter(Payment.tagihan_id == tagihan.id)
                        .all()
                        )
            if(payments):
                for payment in payments:
                    history.append({
                        "pelanggan_id": pelanggan.pelanggan_id,
                        "tagihan_id": tagihan.id,
                        "bulan": tagihan.bulan,
                        "tahun": tagihan.tahun,
                        "jumlah_tagihan": tagihan.jumlah,
                        "status_tagihan": tagihan.status,
                        "payment_id": payment.id,
                        "amounts": payment.amounts,
                        "metode": payment.metode,
                        "payment_code": payment.payment_code,
                        "status_payment": payment.status,
                        "created_at": payment.created_at,
                        "expired_at": payment.expired_at
                    })

    
    return history

@router.get("/qr/{pelanggan_id}/{year}/{month}")
def get_qr_payment(pelanggan_id: str, year: int,month: int,current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tagihan = (db.query(Tagihan)
                .filter(Tagihan.pelanggan_id == pelanggan_id)
                .filter(Tagihan.tahun == year)
                .filter(Tagihan.bulan == month)
                .first()
                )
    
    # request QR payment record
    payment_code = "QR123456789" # This should be generated or retrieved from a payment gateway
    current_time = datetime.now()
    new_qr = Payment(
                tagihan_id=tagihan.id,
                cms_users_id=current_user["user_id"],
                pelanggan_id = pelanggan_id,
                amounts=5000,
                metode="QRIS",
                status="Pending",
                payment_code=payment_code,
                created_at=current_time,
                expired_at=current_time + timedelta(seconds=30)
            )
    
    db.add(new_qr)
    db.commit()
    db.refresh(new_qr)
    
    return {"api_status": 1, "message": "QRIS Created", "qris" : new_qr.payment_code } 