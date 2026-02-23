from fastapi import FastAPI
from .routes.api_v1 import api_v1_router
from .database import engine
from . import models
from .docs import custom_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🌴 BorneoAPI",
    version="1.0.0",
    description="""
BorneoAPI is a RESTful backend service for **waste retribution management**, 
built using **FastAPI** and **MySQL**.

### 🔑 Authentication
- Login using NIK (`/api/v1/auth/login`)
- Get JWT token for secured endpoints

### 👤 User Management
- `/api/v1/users/me` – Get profile info
- `/api/v1/users` – Manage user records

### 🗄️ Database
Connected to existing **Laravel `cms_users`** table.
    """,
    contact={
        "name": "BorneoAPI Developer Team",
        "url": "https://borneoapi.dev",
        "email": "support@borneoapi.dev",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # for testing only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(api_v1_router)

@app.get("/")
def root():
    return {"message": "BorneoAPI is running 🚀"}

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return custom_swagger_ui_html()

