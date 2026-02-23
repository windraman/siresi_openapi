import os
import random
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Warga
import bcrypt

router = APIRouter(prefix="/register", tags=["Register"])

@router.get("/{telp}/{nik}/{name}")
def registrasi(telp: str, nik: str, name: str, db: Session = Depends(get_db)):
    telp_exist = db.query(User).filter(User.no_telp == telp).first()
    if not telp_exist:
        nik_exist = db.query(Warga).filter(Warga.nik == nik).first()
        if nik_exist:
            user_exist = db.query(User).filter(User.nik == nik).first()
            if not user_exist:
                new_password = str(random.randint(100000, 999999))
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode()
                new_user = User(
                    name=name,
                    display_name=name,
                    nik=nik,
                    no_telp=telp,
                    id_cms_privileges=2,
                    password=hashed,
                    status="Active"
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                return {"api_status": 1,"message": "Pendaftaran Berhasil, \nNik : " + nik + "\nPassword : " + new_password , "user_id": new_user.id}
            else:
                return {"api_status": 0, "message": "NIK already registered"}
        else:
            new_warga = Warga(
                nama_lgkp=name,
                nik=nik,
                telp=telp
            )
            db.add(new_warga)
            db.commit()
            db.refresh(new_warga)

            new_password = str(random.randint(100000, 999999))
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode()
            new_user = User(
                name=name,
                display_name=name,
                nik=nik,
                no_telp=telp,
                id_cms_privileges=2,
                password=hashed,
                status="Active"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return {"api_status": 1,"message": "Pendaftaran Berhasil, \nNik : " + nik + "\nPassword : " + new_password , "user_id": new_user.id}
    else:
        return {"api_status": 0, "message": "Nomor Telepon Sudah Pernah Digunakan."}
    
@router.get("/reset/{telp}/{nik}")
def reset(telp: str, nik: str, db: Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.no_telp == telp).filter(User.nik == nik).first()
    if user_exist:
        new_password = str(random.randint(100000, 999999))
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode()
        user_exist.password = hashed
        db.commit()
        return {"api_status": 1,"message": "Reset Password Berhasil, \nNik : " + nik + "\nPassword Baru : " + new_password }
    else:
        return {"api_status": 0, "message": "Data tidak valid !! Gunakan nomor telepon yang digunakan dalam pendaftaran dan Pastikan NIK sudah benar"}
