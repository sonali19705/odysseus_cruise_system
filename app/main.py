from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes.quotes import router as quote_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Cruise Booking System",
    description="Odysseus Practical Assessment",
    version="1.0.0"
)


app.include_router(quote_router)


@app.get("/")
def root():
    return {
        "message": "Cruise Booking System API",
        "status": "running"
    }