import secrets
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db, create_tables
from app.schemas import (
    URLCreate, 
    URLUpdate, 
    URLResponse, 
    URLDetailsResponse
)
from app.repositories.url_repo import (
    get_url_from_db, 
    save_url_to_db, 
    update_url_from_db,
    del_url_from_db,
    update_url_access_count
)

db_session = Annotated[Session, Depends(get_db)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def create_url(payload: URLCreate, db: db_session) -> URLResponse:
    random_token = secrets.token_urlsafe(4)
    short_code = random_token.replace("-", "").replace("_", "")[:6]

    new_url = save_url_to_db(db, **payload.model_dump(), short_code=short_code)

    return URLResponse.model_validate(new_url)

@app.get("/shorten/{short_code}")
def get_url(short_code: str, db: db_session) -> URLResponse:
    url = get_url_from_db(db, short_code)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    return URLResponse.model_validate(url)

@app.put("/shorten/{short_code}", status_code=status.HTTP_200_OK)
def update_url(short_code: str, payload: URLUpdate, db: db_session) -> URLResponse:
    url = update_url_from_db(db, short_code, payload.url)
    if not url: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")

    return URLResponse.model_validate(url)

@app.delete("/shorten/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(short_code: str, db: db_session) -> Response:
    url = del_url_from_db(db, short_code)

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/shorten/{short_code}/stats")
def get_url_stats(short_code: str, db: db_session) -> URLDetailsResponse:
    url = get_url_from_db(db, short_code)

    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    return URLDetailsResponse.model_validate(url)

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: db_session):
    selected_url = get_url_from_db(db, short_code)

    if not selected_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"URL with {short_code} not found")
    
    update_url_access_count(db, selected_url)
    return RedirectResponse(url=selected_url.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)