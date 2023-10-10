import uuid

from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from pydantic import field_serializer
from typing import NewType

MethodPath = NewType("MethodPath", str)


class BaseEvent(BaseModel):
    """Parent event for all events. Do not instantiate this directly.
    Event workers and handlers expected a subclass of this BaseEvent.

    Can be referenced for type hints when the exact subclass instance is unknown until runtime.

    """
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: str(datetime.utcnow()))


class RouteTimingCreated(BaseEvent):
    """A `RouteTimer` has completed a measurement in `RouteTimingMiddleware`

    # TODO once all event are using event_models, change `type` to `event_name`
    `type`: str = "route_timing_created"

    Attrs:
        `request_id`: str
        `method_path`: str
        `method`: str
        `path`: str
        `start_ts`: datetime
        `stop_ts`: datetime
        `diff_ms`: float | int = Field(ge=0)

    Exclude on `model_dump()`:
        - `type`

    """

    type: str = "route_timing_created"
    request_id: str
    method_path: MethodPath
    method: str
    path: str
    start_ts: datetime
    stop_ts: datetime
    diff_ms: float | int = Field(ge=0)


class RouteTimingsPersisted(BaseEvent):
    """A batch of route timing events for a `method_path`
    have been persisted to the db.

    `type`: str = "route_timings_persisted"

    Attrs:
        `method_path`: MethodPath

    Exclude on `model_dump()`:
        - `type`

    """

    type: str = "route_timings_persisted"
    method_path: MethodPath


class NewUserCreated(BaseEvent):
    """A new user has signed up and been created in the database.

    `type`: str = "new_user_created"

    Attrs:
        `email`: str, new user's email
        `name`: str, new user's name

    Exclude on `model_dump()`:
        - `type`

    """

    type: str = "new_user_created"
    email: EmailStr
    name: str


class PasswordResetRequested(BaseEvent):
    """A visitor has passed authentication as an existing user
     and requested a password reset url be sent to their email.

    `type`: str = "password_reset_requested"

    Attrs:
        `email`: str, the user's email
        `name`: str, the user's name
        `url`: str, the password reset link

    Exclude on `model_dump()`:
        - `type`

    """

    type: str = "password_reset_requested"
    email: EmailStr
    name: str
    url: str


class UserLoggedIn(BaseEvent):
    """An existing user has logged in.

    `type`: str = "user_logged_in"

    Attrs:
        `name`: str, user's name

    Exclude on `model_dump()`:
        - `type`

    """

    # TODO this can capture user_agent, ip address etc as needed for analysis
    type: str = "user_logged_in"
    user_id: int
    name: str
