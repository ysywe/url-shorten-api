from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import URLModel

def get_url_from_db(db: Session, short_code: str) -> URLModel:
    return db.scalar(select(URLModel).where(URLModel.short_code == short_code))

def save_url_to_db(db: Session, url: str, short_code: str) -> URLModel:
    new_url = URLModel(url=url, short_code=short_code)

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url

def update_url_from_db(db: Session, short_code: str, new_url: str) -> URLModel:
    url = get_url_from_db(db, short_code)

    if not url:
        return None

    url.url = new_url
    db.commit()
    db.refresh(url)

    return url

def del_url_from_db(db: Session, short_code: str) -> URLModel | None:
    url = get_url_from_db(db, short_code)

    if not url:
        return None

    db.delete(url)
    db.commit()

    return url

def update_url_access_count(db, url: URLModel) -> None:
    url.access_count += 1
    db.commit()