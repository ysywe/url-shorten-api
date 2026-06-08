import schemas
import models
from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]
