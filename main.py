import schemas
import models
import secrets
from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
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
async def create_url(payload: schemas.URLCreate, db: DBSession) -> schemas.URLResponse:
    random_token = secrets.token_urlsafe(4)
    short_code = random_token.replace("-", "").replace("_", "")[:6]

    new_url = models.URLModel(**payload.model_dump(), short_code=short_code)

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url

@app.get("/shorten/{short_code}", status_code=status.HTTP_200_OK)
async def get_url(short_code: str, db: DBSession) -> schemas.URLResponse:
    url = db.scalar(select(models.URLModel).where(models.URLModel.short_code == short_code))

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    return url

@app.put("/shorten/{short_code}", status_code=status.HTTP_200_OK)
async def update_url(short_code: str, payload: schemas.URLUpdate, db: DBSession) -> schemas.URLResponse:
    url = db.scalar(select(models.URLModel).where(models.URLModel.short_code == short_code))

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")

    url.url = payload.url

    db.commit()
    db.refresh(url)

    return url

@app.delete("/shorten/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(short_code: str, db: DBSession):
    url = db.scalar(select(models.URLModel).where(models.URLModel.short_code == short_code))

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    db.delete(url)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/shorten/{short_code}/stats", status_code=status.HTTP_200_OK)
async def get_url_stats(short_code: str, db: DBSession) -> schemas.URLDetailsResponse:
    url = db.scalar(select(models.URLModel).where(models.URLModel.short_code == short_code))

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    return url

@app.get("/{short_code}", status_code=status.HTTP_200_OK)
async def redirect_to_url(short_code: str, db: DBSession):
    selected_url = db.scalar(select(models.URLModel).where(models.URLModel.short_code == short_code))

    if not selected_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    selected_url.access_count += 1
    db.commit()

    return RedirectResponse(url=selected_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)