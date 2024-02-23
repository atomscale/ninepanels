import uuid

from typing import Any

from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from pydantic import model_validator

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
    # entries: list[Entry] # depr in new response model

class DayCreate(BaseModel):
    panel_date: datetime
    day_of_week: int
    day_date_num: int
    last_updated: datetime
    is_complete: bool
    is_pad: bool
    panel_id: int


class Day(DayCreate):
    model_config = {"from_attributes": True}
    id: int


class Graph(BaseModel):
    days: list[Day]
    stats: dict
    week_column: list

class PanelResponse(Panel):
    # is_complete: bool # depr in new response model, use panel.graph[0].isComplete in client instead
    graph: Graph

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
    is_admin: bool | None = None
    last_login: datetime | None = None
    last_activity: datetime | None = None


class UserInDB(User):
    panels: list[Panel]
    hashed_password: str

class LogMessage(BaseModel):
    timestamp: str = Field(default_factory=lambda: str(datetime.utcnow()))
    level: str = Field(default='info')
    detail: str
    context_msg: str | None = None
    context_data: dict | None = None # TODO this will need to change if it is to be persisted? or leverage postgres json?

class WrappedResponse(BaseModel):
    data: dict | list | bool | None = None
    status_code: int
    is_error: bool
    error_message: str | None = None
    meta: dict | list | None = None

# class Event(BaseModel):
#     """ DEPRECATED """
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     created_at: str = Field(default_factory=lambda: str(datetime.utcnow()))
#     type: str
#     payload: Any | None = None
#     payload_type: Any | None = None
#     payload_desc: str | None = None