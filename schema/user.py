from typing import Optional
from pydantic import BaseModel


class BookingUser(BaseModel):
    uid: str
    name: str
    password: str
    email: Optional[str]
    mac: str