from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime


class AccessToken(BaseModel):
    access_token: str


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
    created_at: datetime | None = None # dev None, will be non-nullable
    title: str
    description: str | None = None
    position: int | None = None # dev None, will be non-nullable
    user_id: int
    entries: list[Entry]

class PanelResponse(Panel):
    is_complete: bool


class PanelUpdate(BaseModel):
    """request validation for the update operation"""

    title: str = None
    description: str = None

class UserBase(BaseModel):
    email: EmailStr = Field(examples=["james@bond.com"])
    name: str | None = None


class UserCreate(UserBase):
    plain_password: str


class User(UserBase):
    model_config = {"from_attributes": True}

    id: int


class UserInDB(User):
    panels: list[Panel]
    hashed_password: str
