from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
    pool_size=20,
    max_overflow=10
)

SessionLocal = sessionmaker(
    engine,  
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    with SessionLocal() as session:
        yield session


