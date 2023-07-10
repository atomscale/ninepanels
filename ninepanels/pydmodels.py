from pydantic import BaseModel, Field
from datetime import datetime

class EntryCreate(BaseModel):
    is_complete: bool = Field(examples=[True])
    panel_id: int
    user_id: int | None = None # dev only remove one auth depdncy in place

class Entry(EntryCreate):
    model_config = {"from_attributes": True}

    id: int
    timestamp: datetime

class Panel(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    user_id: int

