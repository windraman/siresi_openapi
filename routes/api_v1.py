from fastapi import APIRouter
from . import auth, users, bills, tickets, register, payment, residence

api_v1_router = APIRouter(prefix="/api/v1")

# Include all v1 routers here
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
api_v1_router.include_router(bills.router)
api_v1_router.include_router(tickets.router)
api_v1_router.include_router(register.router)
api_v1_router.include_router(payment.router)
api_v1_router.include_router(residence.router)


