from datetime import timedelta, datetime

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from app import schemas, models, utils
from app.database import get_db
from app.models import UserGroup
from app.utils import get_current_active_user


router = APIRouter()

@router.post("/login", response_model=schemas.TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(hours=48)
    access_token = utils.create_access_token(user.id, expires_delta=access_token_expires)
    token_expiry = datetime.timestamp(datetime.utcnow() + access_token_expires)

    token_entry = models.Token(user_id=user.id, token=access_token, expiry=token_expiry)
    db.add(token_entry)
    db.commit()

    return {"token": access_token, "expiry": token_expiry}


@router.post("/user", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = utils.hash_password(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, group=user.group)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/user/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, current_user: models.User = Depends(get_current_active_user),
                db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.group != UserGroup.admin and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    if user.password:
        db_user.hashed_password = utils.hash_password(user.password)
    if user.group and current_user.group == UserGroup.admin:
        db_user.group = user.group

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_user: models.User = Depends(get_current_active_user),
                db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.group != UserGroup.admin and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
