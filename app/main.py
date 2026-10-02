from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)


@app.get("/")
def root():
    return {"message": "AI Knowledge & Action Platform API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}