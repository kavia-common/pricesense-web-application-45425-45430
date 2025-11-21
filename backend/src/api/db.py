import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Load environment variables from a .env file if present
load_dotenv()

# Database URL from environment with SQLite default suitable for local development
DATABASE_URL = os.getenv("BACKEND_DB_URL", "sqlite:///./pricesense.db")

# Create SQLAlchemy engine; for SQLite we must disable same-thread check for FastAPI usage
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations.

    Yields a SQLAlchemy Session that is closed after request handling.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
