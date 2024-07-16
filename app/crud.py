from sqlalchemy.orm import Session
from . import models, schemas

def create_advertisement(db: Session, advertisement: schemas.AdvertisementCreate):
    db_advertisement = models.Advertisement(**advertisement.dict())
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

def get_advertisement(db: Session, advertisement_id: int):
    return db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()

def update_advertisement(db: Session, advertisement_id: int, advertisement: schemas.AdvertisementUpdate):
    db_advertisement = get_advertisement(db, advertisement_id)
    if not db_advertisement:
        return None
    for key, value in advertisement.dict(exclude_unset=True).items():
        setattr(db_advertisement, key, value)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

def delete_advertisement(db: Session, advertisement_id: int):
    db_advertisement = get_advertisement(db, advertisement_id)
    if db_advertisement:
        db.delete(db_advertisement)
        db.commit()
    return db_advertisement

def search_advertisements(db: Session, title: str = None, author: str = None):
    query = db.query(models.Advertisement)
    if title:
        query = query.filter(models.Advertisement.title.contains(title))
    if author:
        query = query.filter(models.Advertisement.author.contains(author))
    return query.all()
