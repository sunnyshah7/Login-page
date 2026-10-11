from fastapi import FastAPI

from app.core.config import settings
from app.db.database import engine
from app.db.base import Base

settings.validate_security_settings()

app = FastAPI(title="Chatflow API")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Chatflow API is running"}
