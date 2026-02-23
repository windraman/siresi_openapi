from pydantic import BaseModel

class UserBase(BaseModel):
    name: str
    display_name: str
    nik: str
    password: str  
    id_cms_privileges: int = 2

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    nik: str
    password: str

class WargaBase(BaseModel):
    nik: str
    nama_lgkp: str
    telp: str

class WargaCreate(UserBase):
    pass

class WargaOut(UserBase):
    id: int

    class Config:
        orm_mode = True

class TicketBase(BaseModel):
    problem: str
    lat: float
    lon: float

class TicketCreate(TicketBase):
    pass

class TicketResponse(BaseModel):
    id: int
    cms_users_id: int
    cms_privileges_id: int
    problem: str
    lat: float
    lon: float
    status: str

    class Config:
        orm_mode = True

class VillageOut(BaseModel):
    id: str
    name: str
    district_id: str

class ResidenceOut(BaseModel):
    id: int
    pelanggan_id: str
    cms_users_id: int | None
    lat: str | None
    lon: str | None
    alamat: str | None
    rt: str | None
    rw: str | None
    village_id: str | None
    district_id: str | None
    regency_id: str | None
    province_id: str | None

    village: VillageOut | None

    kelurahan: str | None

    class Config:
        orm_mode = True

class PelangganUsers(BaseModel):
    id: int
    pelanggan_id: int
    cms_users_id: int 

class PairResidenceRequest(BaseModel):
    pelanggan_id: int