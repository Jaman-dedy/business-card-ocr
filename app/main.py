import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import business_cards
from app.config import API_V1_PREFIX, UPLOAD_DIR
from app.db.session import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Business Card OCR API",
    description="API for processing business cards using OCR",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(
    business_cards.router,
    prefix=f"{API_V1_PREFIX}/business-cards",
    tags=["business-cards"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the Business Card OCR API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
