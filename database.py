from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Example: MySQL database configuration
DATABASE_URL = "mysql+pymysql://root:INV%40n4n4cu@localhost:3306/siapkakang"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency (used in routes)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
