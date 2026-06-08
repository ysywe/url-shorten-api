import schemas
import models
import secrets
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

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
async def create_Post(payload: schemas.URLCreate, db: DBSession) -> schemas.URLResponse:
    random_token = secrets.token_urlsafe(4)
    short_code = random_token.replace("-", "").replace("_", "")[:6]

    new_url = models.URLModel(**payload.model_dump(), short_code=short_code)

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url