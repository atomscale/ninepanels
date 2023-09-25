from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime


class AccessToken(BaseModel):
    access_token: str


class EntryCreate(BaseModel):
    is_complete: bool = Field(examples=[True])


class Entry(EntryCreate):
    model_config = {"from_attributes": True}
    id: int
    panel_id: int
    timestamp: datetime


class Panel(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    created_at: datetime | None = None  # dev None, will be non-nullable
    title: str
    description: str | None = None
    position: int | None = None  # dev None, will be non-nullable
    user_id: int
    entries: list[Entry]


class PanelResponse(Panel):
    is_complete: bool


class PanelUpdate(BaseModel):
    """request validation for the update operation"""

    title: str = None
    description: str = None

class HTTPError(BaseModel):
    """error repsonse model for docs"""
    detail: str

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

class LogMessage(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(default='info')
    detail: str
    context_msg: str | None = None
    context_data: dict | None = None

class WrappedResponse(BaseModel):
    data: dict | list | None = None
    status_code: int
    is_error: bool
    error_message: str | None = None
    meta: dict | list | None = None