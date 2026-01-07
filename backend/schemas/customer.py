# schemas/customer.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: Optional[str]
    created_at: datetime