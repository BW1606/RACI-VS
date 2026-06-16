import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

if getattr(sys, "frozen", False):
    # Running as a PyInstaller bundle — store the DB in %APPDATA%\RACI-VS\
    # so it survives app updates and is always writable (Program Files is not).
    _db_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "RACI-VS")
    os.makedirs(_db_dir, exist_ok=True)
else:
    _db_dir = os.path.dirname(os.path.abspath(__file__))

DATABASE_URL = f"sqlite:///{os.path.join(_db_dir, 'raci_vs.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
