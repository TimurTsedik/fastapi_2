from pydantic import BaseModel, Field

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

    class Config:
        from_attributes = True
