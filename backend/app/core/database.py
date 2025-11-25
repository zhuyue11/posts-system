from typing import Generator, Union
from app.core.config import settings

if settings.DB_TYPE == "postgresql":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session

    # Create database engine
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL query logging during development
    )

    # Create session factory
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    def get_db() -> Generator[Session, None, None]:
        """
        Database session dependency for FastAPI routes.
        Yields a database session and ensures it's closed after use.

        Usage:
            @app.get("/items")
            def get_items(db: Session = Depends(get_db)):
                return db.query(Item).all()
        """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

elif settings.DB_TYPE == "firestore":
    from app.core.firestore_client import get_firestore_client
    from google.cloud import firestore

    def get_db() -> firestore.Client:
        """
        Firestore client dependency for FastAPI routes.
        Returns the Firestore client singleton.

        Usage:
            @app.get("/items")
            def get_items(db: firestore.Client = Depends(get_db)):
                return db.collection('items').stream()
        """
        return get_firestore_client()

else:
    raise ValueError(f"Invalid DB_TYPE: {settings.DB_TYPE}. Must be 'postgresql' or 'firestore'.")
