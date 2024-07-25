from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from app import schemas, models
from app.database import get_db
from app.models import UserGroup
from app.utils import get_current_active_user


router = APIRouter()

@router.post("/advertisement", response_model=schemas.Advertisement)
def create_advertisement(ad: schemas.AdvertisementCreate, current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    db_ad = models.Advertisement(**ad.dict(), owner_id=current_user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@router.patch("/advertisement/{ad_id}", response_model=schemas.Advertisement)
def update_advertisement(ad_id: int, ad: schemas.AdvertisementUpdate,
                         current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_ad = db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()
    if db_ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")

    if current_user.group != UserGroup.admin and db_ad.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    for var, value in vars(ad).items():
        setattr(db_ad, var, value) if value else None

    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@router.delete("/advertisement/{ad_id}")
def delete_advertisement(ad_id: int, current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    db_ad = db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()
    if db_ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")

    if current_user.group != UserGroup.admin and db_ad.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db.delete(db_ad)
    db.commit()
    return {"message": "Advertisement deleted successfully"}


@router.get("/advertisement/{ad_id}", response_model=schemas.Advertisement)
def read_advertisement(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()
    if ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")
    return ad


@router.get("/advertisement", response_model=list[schemas.Advertisement])
def search_advertisements(title: str | None = None, description: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Advertisement)
    if title:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        query = query.filter(models.Advertisement.description.ilike(f"%{description}%"))
    return query.all()
