from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session,relationship
from .. import models, schemas
from ..database import get_db
from ..utils.jwt_handler import verify_token
from ..models import User, MultiPrivs, CmsPrivilege, Warga, Villages, Districts, Regencies, Provinces, Tagihan, Tarif
from sqlalchemy import exists, or_, func
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])

# @router.post("/", response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = models.User(**user.dict())
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# @router.get("/{user_id}")
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()  
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

@router.get("/profile")
def get_profile(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 🧩 Get privileges via join
    privileges = (
        db.query(CmsPrivilege.name)
        .join(MultiPrivs, CmsPrivilege.id == MultiPrivs.cms_privileges_id)
        .filter(MultiPrivs.cms_users_id == user.id)
        .all()
    )

    privileges = [
        {"id": p.privilege.id, "name": p.privilege.name}
        for p in user.privileges
        if p.privilege is not None
    ]

    return {
        "id": user.id,
        "nik": user.nik,
        "name": user.display_name or user.name,
        "email": user.email,
        "role_id": user.id_cms_privileges,
        "role": user.privilege.name,
        "photo": user.photo,
        "status": user.status,   
        "privileges": privileges
    }

@router.get("/by-nik/{nik}") #add verify_token
def get_user_by_nik(nik: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.nik == nik).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    warga = (
        db.query(Warga)
        .filter(Warga.nik == user.nik)
        .first()
    )

    return {
        "id": user.id,
        "nik": user.nik,
        "name": user.display_name or user.name,
        "alamat": warga.alamat2,
        "rt": warga.rt,
        "rw": warga.rw,
        "status": user.status,
    }

@router.get("/")
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    search: str = "",
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    # Base Query with LEFT JOIN
    query = (
        db.query(
            User.id,
            User.nik,
            User.display_name,
            User.name.label("user_name"),
            User.email,
            User.no_telp,
            User.status,
            # Warga.alamat2,
            # Warga.rt,
            # Warga.rw
        )
        # .outerjoin(Warga, Warga.nik == User.nik)
    )

    # 🔍 Apply search if provided
    if search:
        s = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(User.name).like(s),
                func.lower(User.display_name).like(s),
                User.nik.like(f"%{search}%")
            )
        )

    # Count total items
    total_items = query.count()
    total_pages = (total_items + limit - 1) // limit

    # Fetch data
    rows = (
        query.order_by(User.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for row in rows:
        warga = (
            db.query(Warga)
            .filter(Warga.nik == row.nik)
            .first()
        )
        items.append({
            "id": row.id,
            "nik": row.nik,
            "name": row.display_name or row.user_name,
            "email": row.email,
            "no_telp": row.no_telp,
            "alamat": warga.alamat2,
            "rt": warga.rt,
            "rw": warga.rw,
            "status": row.status,
        })

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "data": items
    }

@router.get("/{user_id}/tagihan")
def get_warga_tagihan(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_datetime = datetime.now()

    for i in range(current_datetime.month):
        tagihan = db.query(Tagihan).filter(Tagihan.cms_users_id == user.id).filter(Tagihan.bulan == i+1).filter(Tagihan.tahun == 2025).first()
        if not tagihan:
            tarif = db.query(Tarif).order_by(Tarif.berlaku.desc()).first()
            tagihan = Tagihan(
                cms_users_id=user.id,
                bulan=i+1,
                tahun=2025,
                jumlah=tarif.nominal if tarif else 5000,
                status="Belum Bayar",
            )
            db.add(tagihan)
            db.commit()
            db.refresh(tagihan)


    return (
        db.query(Tagihan).filter(Tagihan.cms_users_id == user.id).filter(Tagihan.tahun == 2025).all()
    )


