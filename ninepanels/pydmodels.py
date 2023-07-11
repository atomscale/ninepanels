from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class AccessToken(BaseModel):
    access_token: str

class UserBase(BaseModel):
    email: EmailStr = Field(examples=['james@bond.com'])

class UserCreate(UserBase):
    plain_password: str

class User(UserBase):
    id: int
    name: str
    hashed_password: str
    panels: list | None = None


class EntryCreate(BaseModel):
    is_complete: bool = Field(examples=[True])
    panel_id: int

class Entry(EntryCreate):
    model_config = {"from_attributes": True}

    id: int
    timestamp: datetime

class Panel(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    user_id: int

