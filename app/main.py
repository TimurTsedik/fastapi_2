from fastapi import FastAPI
from . import models
from .database import engine

from .users import router as users_router
from .ads import router as ads_router

app = FastAPI()
app.include_router(users_router, tags=["users"])
app.include_router(ads_router, tags=["ads"])

models.Base.metadata.create_all(bind=engine)


