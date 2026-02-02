"""
Database configuration and session management module.

This module handles SQLAlchemy engine initialization, session creation, and
provides database session management utilities. It loads the database URL
from environment variables and creates the database engine and session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from contextlib import contextmanager

import os

dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set.")


engine = create_engine(
    DATABASE_URL,
    echo=False,  # logs SQL queries
)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    """Context manager for database session management.

    Provides a safe way to obtain a database session that is automatically
    closed when done. Should be used with a 'with' statement.

    Yields:
        Session: A SQLAlchemy session object for database operations.

    Example:
        with get_db() as db:
            result = db.execute(select(Task))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    This class serves as the declarative base for all database models.
    All model classes should inherit from this Base class to be tracked
    by SQLAlchemy for database table creation and operations.
    """

    pass
