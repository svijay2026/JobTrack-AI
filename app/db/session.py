import os
import ssl
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

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
    # If connecting to Aiven or external MySQL requiring SSL, configure TLS context
    if "aivencloud" in db_url or "ssl" in db_url.lower():
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        engine_kwargs["connect_args"] = {"ssl": ctx}

# Configure SQLAlchemy engine with resilient connection check
try:
    engine = create_engine(db_url, **engine_kwargs)
    with engine.connect() as conn:
        pass
except Exception as err:
    logger.warning(f"Could not connect to primary database ({err}). Falling back to local persistent SQLite.")
    os.makedirs("uploads", exist_ok=True)
    engine = create_engine("sqlite:///./uploads/jobtrack_ai.db", connect_args={"check_same_thread": False})

# Session factory for generating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
