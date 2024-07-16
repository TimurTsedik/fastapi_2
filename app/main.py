from fastapi import FastAPI
from .database import engine, Base
from .routers import advertisements

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(advertisements.router, prefix="/advertisements", tags=["advertisements"])
