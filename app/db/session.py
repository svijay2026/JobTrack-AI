from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

db_url = settings.database_url
engine_kwargs = {"echo": settings.DEBUG}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
    })

# Configure SQLAlchemy engine
engine = create_engine(db_url, **engine_kwargs)

# Session factory for generating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
