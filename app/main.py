import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import business_cards
from app.config import API_V1_PREFIX, UPLOAD_DIR
from app.db.session import Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle Google Cloud credentials
try:
    # If GOOGLE_CREDENTIALS_JSON env var exists (Render deployment)
    if os.environ.get("GOOGLE_CREDENTIALS_JSON"):
        logger.info("Found credentials in GOOGLE_CREDENTIALS_JSON environment variable")
        credentials_path = "./google-credentials.json"

        # Write credentials to file
        with open(credentials_path, "w") as f:
            f.write(os.environ.get("GOOGLE_CREDENTIALS_JSON"))

        # Set environment variable to point to file
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        logger.info(f"Credentials written to {credentials_path}")

    # Check if credentials file exists at the path in GOOGLE_APPLICATION_CREDENTIALS
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(creds_path):
            logger.info(f"Using credentials from {creds_path}")
        else:
            logger.error(f"Credentials file not found at {creds_path}")
            raise FileNotFoundError(f"Credentials file not found at {creds_path}")

    # Check for credentials file in current directory (local development)
    elif os.path.exists("./google-credentials.json"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./google-credentials.json"
        logger.info("Using credentials from ./google-credentials.json")

    # No credentials found
    else:
        logger.error("No Google Cloud credentials found")
        raise FileNotFoundError("No Google Cloud credentials found")

except Exception as e:
    logger.error(f"Error setting up Google Cloud credentials: {str(e)}")
    # Continue execution to allow the app to start and show proper error messages

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
    # Check if Google credentials are working
    creds_status = "available" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "missing"

    if creds_status == "available":
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if os.path.exists(creds_path):
            creds_status = "valid"
        else:
            creds_status = f"file not found at {creds_path}"

    return {
        "status": "healthy",
        "google_credentials": creds_status,
        "environment": "production" if not os.environ.get("DEBUG") else "development"
    }
