import string
import nanoid
from typing import Optional
from pydantic import BaseModel, Field


class Note(BaseModel):
    uid: str = Field(default_factory=lambda: nanoid.generate(string.ascii_letters+string.digits, 64))
    uuid: str
    title: str
    content: Optional[str]
    type: str
    path: Optional[str]
    tag: str  
    created_at: int
    modified_at: int
    is_template: int
    is_trash: int
    is_deleted: int
