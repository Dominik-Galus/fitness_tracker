import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore[attr-defined]

load_dotenv()

SQLALCHEMY_DATABASE_URL: str | None = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    msg = "There is no database url"
    raise ValueError(msg)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
