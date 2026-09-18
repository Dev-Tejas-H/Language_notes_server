from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.database import engine, Base
from app.api.routes import auth, notes, translation

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create upload directories
os.makedirs(settings.AUDIO_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Language Notes — save translations, voice messages, grammar and synonym notes.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow React Native dev client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded audio files as static assets
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(notes.router, prefix=API_PREFIX)
app.include_router(translation.router, prefix=API_PREFIX)


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION}"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
