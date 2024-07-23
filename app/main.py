from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, schemas, utils
from .database import engine, SessionLocal
from .models import UserGroup
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = utils.decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.group != UserGroup.admin and current_user.group != UserGroup.user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


@app.post("/login", response_model=schemas.TokenResponse)
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


@app.post("/user", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, group=user.group)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.patch("/user/{user_id}", response_model=schemas.UserResponse)
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


@app.delete("/user/{user_id}")
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


@app.post("/advertisement", response_model=schemas.Advertisement)
def create_advertisement(ad: schemas.AdvertisementCreate, current_user: models.User = Depends(get_current_active_user),
                         db: Session = Depends(get_db)):
    db_ad = models.Advertisement(**ad.dict(), owner_id=current_user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@app.patch("/advertisement/{ad_id}", response_model=schemas.Advertisement)
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


@app.delete("/advertisement/{ad_id}")
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


@app.get("/advertisement/{ad_id}", response_model=schemas.Advertisement)
def read_advertisement(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Advertisement).filter(models.Advertisement.id == ad_id).first()
    if ad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")
    return ad


@app.get("/advertisement", response_model=list[schemas.Advertisement])
def search_advertisements(title: str | None = None, description: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Advertisement)
    if title:
        query = query.filter(models.Advertisement.title.ilike(f"%{title}%"))
    if description:
        query = query.filter(models.Advertisement.description.ilike(f"%{description}%"))
    return query.all()
