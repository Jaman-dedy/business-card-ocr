import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class BusinessCard(Base):
    __tablename__ = "business_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_path = Column(String, nullable=False)
    full_text = Column(Text, nullable=True)  # Raw OCR text
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contact_info = relationship("ContactInfo", back_populates="business_card", uselist=False, cascade="all, delete-orphan")

class ContactInfo(Base):
    __tablename__ = "contact_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_card_id = Column(UUID(as_uuid=True), ForeignKey("business_cards.id"), nullable=False)

    # Person info
    name = Column(String, nullable=True)
    job_title = Column(String, nullable=True)

    # Company info
    company = Column(String, nullable=True)

    # Contact details
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Address
    address = Column(Text, nullable=True)

    # Social media
    linkedin = Column(String, nullable=True)
    twitter = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business_card = relationship("BusinessCard", back_populates="contact_info")
