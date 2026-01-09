from pydantic import BaseModel
from typing import Literal, Optional

class TicketCreate(BaseModel):
    customer_id: int
    title: str
    description: Optional[str] = None
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    assigned_to: Optional[int] = None
