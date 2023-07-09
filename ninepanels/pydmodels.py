from pydantic import BaseModel, Field

class EntryCreate(BaseModel):
    is_complete: bool = Field(examples=[True])
    panel_id: int

class Entry(EntryCreate):
    model_config = {"from_attributes": True}

    id: int
    timestamp: str

