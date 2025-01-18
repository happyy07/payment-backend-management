from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str = Field(...,  pattern="^(completed|due_now|overdue|pending)$")
    payee_added_date_utc: datetime
    payee_due_date: datetime
    payee_address_line_1: str
    payee_address_line_2: Optional[str] = None
    payee_city: str
    payee_country: str = Field(..., pattern="^[A-Z]{2}$")
    payee_province_or_state: Optional[str] = None
    payee_postal_code: str
    payee_phone_number: str
    payee_email: EmailStr
    currency: str = Field(..., pattern="^[A-Z]{3}$")
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    tax_percent: Optional[float] = Field(None, ge=0)
    due_amount: float = Field(..., ge=0)
    total_due: Optional[float] = None
    evidence_file_id: Optional[str] = None

    @validator('payee_phone_number')
    def validate_phone(cls, v):
        if not re.match(r'^\+[1-9]\d{1,14}$', v):
            raise ValueError('Phone number must be in E.164 format')
        return v
