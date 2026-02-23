from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text, Double, Float
from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    __tablename__ = "cms_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    display_name = Column(String(100))
    email = Column(String(100), unique=True)
    nik = Column(String(100), unique=True)
    no_telp = Column(String(100), unique=True)
    password = Column(String(100))
    photo = Column(String(100))
    id_cms_privileges = Column(Integer, ForeignKey("cms_privileges.id"))
    privilege = relationship("CmsPrivilege") 
    status = Column(String(15))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    privileges = relationship(
        "MultiPrivs",
        backref="user",
        cascade="all, delete-orphan",
        lazy="joined"
    )

class MultiPrivs(Base):
    __tablename__ = "multi_privs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cms_users_id = Column(Integer, ForeignKey("cms_users.id"))
    cms_privileges_id = Column(Integer, ForeignKey("cms_privileges.id"))

    users = relationship("User")
    privilege = relationship("CmsPrivilege")  # 👈 directly link to CmsPrivilege

class CmsPrivilege(Base):
    __tablename__ = "cms_privileges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))

class Warga(Base):
    __tablename__ = "warga_bjb"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nik = Column(String(100))
    nama_lgkp = Column(String(100))
    alamat2 = Column(Text)
    telp = Column(String(15))
    rt = Column(String(10))
    rw = Column(String(10))
    nama_kel = Column(String(100), ForeignKey("villages.id"))
    nama_kec = Column(String(100), ForeignKey("distrists.id"))
    nama_kab = Column(String(100), ForeignKey("regencies.id"))
    nama_prop = Column(String(100), ForeignKey("provinces.id"))

class Residence(Base):
    __tablename__ = "pelanggan_restu_bumi"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cms_users_id = Column(Integer, ForeignKey("cms_users.id"), index=True)
    pelanggan_id = Column(String(13), nullable=False, unique=True)
    lat = Column(String(15))
    lon = Column(String(15))
    alamat = Column(String(512), nullable=True)
    rt = Column(String(8), nullable=True)
    rw = Column(String(8), nullable=True)
    village_id = Column(String(100), ForeignKey("villages.id"))
    village = relationship("Villages",back_populates="residence",lazy="joined")

    @property
    def kelurahan(self):
        return self.village.name if self.village else None

    district_id = Column(String(100), ForeignKey("districts.id"))
    regency_id = Column(String(100), ForeignKey("regencies.id"))
    province_id = Column(String(100), ForeignKey("provinces.id"))
    
    # user = relationship("User", back_populates="residences")
    # bills = relationship("Tagihan", back_populates="residence", lazy="joined")

class PelangganUsers(Base):
    __tablename__ = "pelanggan_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cms_users_id = Column(Integer, ForeignKey("cms_users.id"))
    pelanggan_id = Column(Integer, ForeignKey("pelanggan_restu_bumi.id"))

class Tagihan(Base):
    __tablename__ = "tagihan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    residence_id = Column(Integer, ForeignKey("pelanggan_restu_bumi.id"), index=True)
    pelanggan_id = Column(String(13))
    bulan = Column(Integer)
    tahun = Column(Integer)
    jumlah = Column(Double)
    status = Column(String(50))
    updated_at = Column(DateTime)
    # residence = relationship("Residence", back_populates="bills")

class Tarif(Base):
    __tablename__ = "tarif"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    nominal = Column(Double)
    berlaku = Column(DateTime)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    cms_users_id = Column(Integer, nullable=False)
    cms_privileges_id = Column(Integer, nullable=False)
    problem = Column(Text, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    status = Column(String(50), default="Open")

    processes = relationship("TicketProcess", back_populates="ticket")


class TicketProcess(Base):
    __tablename__ = "ticket_process"

    id = Column(Integer, primary_key=True, index=True)
    tickets_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    cms_users_id = Column(Integer, nullable=False)
    description = Column(Text)
    image = Column(Text)
    status = Column(String(50), default="Open")

    ticket = relationship("Ticket", back_populates="processes")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pelanggan_id = Column(String(13))
    tagihan_id = Column(Integer, ForeignKey("tagihan.id"))
    cms_users_id = Column(Integer, ForeignKey("cms_users.id"))
    amounts = Column(Double)
    created_at = Column(DateTime) 
    expired_at = Column(DateTime) 
    metode = Column(String(50))
    payment_code = Column(String(150))
    status = Column(String(50))

class Villages(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True)
    district_id = Column(Integer, ForeignKey("districts.id"))
    name = Column(String(100))

    residence = relationship("Residence", back_populates="village")

class Districts(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True)
    regency_id = Column(Integer, ForeignKey("regencies.id"))
    name = Column(String(100))

class Regencies(Base):
    __tablename__ = "regencies"

    id = Column(Integer, primary_key=True)
    province_id = Column(Integer, ForeignKey("provinces.id"))
    name = Column(String(100))

class Provinces(Base):
    __tablename__ = "provinces"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    