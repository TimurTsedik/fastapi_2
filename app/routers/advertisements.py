from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models, database

router = APIRouter()

@router.post("/", response_model=schemas.Advertisement)
def create_advertisement(advertisement: schemas.AdvertisementCreate, db: Session = Depends(database.get_db)):
    return crud.create_advertisement(db=db, advertisement=advertisement)

@router.get("/{advertisement_id}", response_model=schemas.Advertisement)
def get_advertisement(advertisement_id: int, db: Session = Depends(database.get_db)):
    db_advertisement = crud.get_advertisement(db=db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@router.patch("/{advertisement_id}", response_model=schemas.Advertisement)
def update_advertisement(advertisement_id: int, advertisement: schemas.AdvertisementUpdate, db: Session = Depends(database.get_db)):
    db_advertisement = crud.update_advertisement(db=db, advertisement_id=advertisement_id, advertisement=advertisement)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@router.delete("/{advertisement_id}", response_model=schemas.Advertisement)
def delete_advertisement(advertisement_id: int, db: Session = Depends(database.get_db)):
    db_advertisement = crud.delete_advertisement(db=db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@router.get("/", response_model=List[schemas.Advertisement])
def search_advertisements(title: str = None, author: str = None, db: Session = Depends(database.get_db)):
    return crud.search_advertisements(db=db, title=title, author=author)
