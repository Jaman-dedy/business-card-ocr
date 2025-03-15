import os
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from app.core.ocr import BusinessCardOCR
from app.db.models import BusinessCard, ContactInfo
from app.db.session import get_db
from app.schemas.business_card import BusinessCardResponse, BusinessCardListResponse

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()
ocr_engine = BusinessCardOCR()

def validate_file_extension(filename: str) -> bool:
    """Validate file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/", response_model=BusinessCardResponse)
async def upload_business_card(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a business card image.
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create business card record
    business_card = BusinessCard(
        image_path=file_path,
        processed=False
    )
    db.add(business_card)
    db.commit()
    db.refresh(business_card)

    # Process asynchronously
    # In a production environment, you'd want to use a background task or queue
    # For simplicity, we'll process synchronously here
    try:
        # Process image with OCR
        full_text, contact_info = ocr_engine.process_image(file_path)

        # Update business card with OCR results
        business_card.full_text = full_text
        business_card.processed = True

        # Create contact info
        contact = ContactInfo(
            business_card_id=business_card.id,
            name=contact_info.get("name"),
            job_title=contact_info.get("job_title"),
            company=contact_info.get("company"),
            email=contact_info.get("email"),
            phone=contact_info.get("phone"),
            mobile=contact_info.get("mobile"),
            website=contact_info.get("website"),
            address=contact_info.get("address"),
            linkedin=contact_info.get("linkedin"),
            twitter=contact_info.get("twitter")
        )
        db.add(contact)
        db.commit()
        db.refresh(business_card)
    except Exception as e:
        # In case of error, keep the record but mark as unprocessed
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error processing business card: {str(e)}"}
        )

    return business_card

@router.get("/{business_card_id}", response_model=BusinessCardResponse)
def get_business_card(
    business_card_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific business card by ID.
    """
    business_card = db.query(BusinessCard).filter(BusinessCard.id == business_card_id).first()
    if not business_card:
        raise HTTPException(status_code=404, detail="Business card not found")

    return business_card

@router.get("/", response_model=BusinessCardListResponse)
def list_business_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all business cards with pagination.
    """
    total = db.query(BusinessCard).count()
    business_cards = db.query(BusinessCard).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": business_cards
    }

@router.delete("/{business_card_id}", status_code=204)
def delete_business_card(
    business_card_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a business card.
    """
    business_card = db.query(BusinessCard).filter(BusinessCard.id == business_card_id).first()
    if not business_card:
        raise HTTPException(status_code=404, detail="Business card not found")

    # Delete image file
    if os.path.exists(business_card.image_path):
        os.remove(business_card.image_path)

    # Delete from database (contact info will be deleted via cascade)
    db.delete(business_card)
    db.commit()

    return None
