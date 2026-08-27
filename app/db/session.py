from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Configure SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Session factory for generating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
