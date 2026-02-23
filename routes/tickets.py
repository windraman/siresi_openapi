import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Ticket, TicketProcess
from ..utils.jwt_handler import verify_token


router = APIRouter(prefix="/tickets", tags=["Tickets"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder of tickets.py
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "uploads", "tickets")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", status_code=http_status.HTTP_201_CREATED)
async def create_ticket(
    problem: str = Form(...),
    lat: float = Form(...),
    lon: float = Form(...),
    cms_privileges_id: int = Form(...),
    images: list[UploadFile] = File([]),
    current_user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    cms_users_id = current_user["user_id"]

    # 1️⃣ Create master ticket
    ticket = Ticket(
        cms_users_id=cms_users_id,
        cms_privileges_id=cms_privileges_id,
        problem=problem,
        lat=lat,
        lon=lon,
        status="Open"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # 2️⃣ Save uploaded images
    saved_filenames = []
    for img in images:
        filename = f"{ticket.id}_{img.filename.replace(' ', '_')}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(await img.read())

        saved_filenames.append(filename)

        # 3️⃣ Create initial ticket_process row
        process = TicketProcess(
            tickets_id=ticket.id,
            cms_users_id=cms_users_id,
            description=problem,
            image=",".join(saved_filenames),
            status="Open"
        )
        db.add(process)
        db.commit()

    return {
        "success": True,
        "message": "Laporan berhasil dibuat",
        "ticket_id": ticket.id,
        "images": saved_filenames
    }
