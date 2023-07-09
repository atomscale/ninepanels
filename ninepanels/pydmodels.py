from pydantic import BaseModel, Field
from datetime import datetime

class EntryCreate(BaseModel):
    is_complete: bool = Field(examples=[True])
    panel_id: int

class Entry(EntryCreate):
    model_config = {"from_attributes": True}

    id: int
    timestamp: datetime

