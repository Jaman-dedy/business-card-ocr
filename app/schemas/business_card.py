from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl, Field

class ContactInfoBase(BaseModel):
    name: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None

class ContactInfoCreate(ContactInfoBase):
    pass

class ContactInfoUpdate(ContactInfoBase):
    pass

class ContactInfoInDB(ContactInfoBase):
    id: UUID
    business_card_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BusinessCardBase(BaseModel):
    pass

class BusinessCardCreate(BusinessCardBase):
    pass

class BusinessCardUpdate(BusinessCardBase):
    processed: Optional[bool] = None

class BusinessCardInDB(BusinessCardBase):
    id: UUID
    image_path: str
    full_text: Optional[str] = None
    processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class BusinessCardWithContactInfo(BusinessCardInDB):
    contact_info: Optional[ContactInfoInDB] = None

class BusinessCardResponse(BaseModel):
    id: UUID
    image_path: str
    processed: bool
    contact_info: Optional[ContactInfoBase] = None
    created_at: datetime

    class Config:
        orm_mode = True

class BusinessCardListResponse(BaseModel):
    total: int
    items: List[BusinessCardResponse]
