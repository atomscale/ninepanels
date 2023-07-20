from pydantic import BaseModel, Field, EmailStr
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
    title: str
    user_id: int
    entries: list[Entry]

class PanelUpdate(BaseModel):
    """ request validation for the udpate operation """
    title: str


class UserBase(BaseModel):
    email: EmailStr = Field(examples=['james@bond.com'])
    name: str | None = None

class UserCreate(UserBase):
    plain_password: str

class User(UserBase):
    model_config = {"from_attributes": True}

    id: int

class UserInDB(User):
    panels: list[Panel]
    hashed_password: str








