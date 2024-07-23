from pydantic import BaseModel
from enum import Enum

class UserGroup(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    group: UserGroup

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: str | None = None
    group: UserGroup | None = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class AdvertisementBase(BaseModel):
    title: str
    description: str
    price: float
    author: str

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    author: str | None = None

class Advertisement(AdvertisementBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    expiry: float
