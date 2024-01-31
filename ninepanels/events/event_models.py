import uuid

from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr
from pydantic import field_serializer
from typing import NewType

from .. import exceptions

MethodPath = NewType("MethodPath", str)


class BaseEvent(BaseModel):
    """Parent event for all events. Do not instantiate this directly.
    Event workers and handlers expected a subclass of this BaseEvent.

    Consumers call model_dump() on the payload, so all keys will always be available.

    Can be referenced for type hints when the exact subclass instance is unknown until runtime.

    """

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: str(datetime.utcnow()))


class BaseExceptionEvent(BaseModel):
    """Base exception building on BaseModel that adds specific expetions eent requirements

    Attrs:
        exc_msg: str, exception message from raised exception
        exc_type: str

        user_id: int, id of user, optional

    """

    exc_msg: str
    exc_type: str

    user_id: int | None = None


class RouteTimingCreated(BaseEvent):
    """A `RouteTimer` has completed a measurement in `RouteTimingMiddleware`

    `name`: str = "route_timing_created"

    Attrs:
        `request_id`: str
        `method_path`: str
        `method`: str
        `path`: str
        `start_ts`: datetime
        `stop_ts`: datetime
        `diff_ms`: float | int = Field(ge=0)

    Exclude on `model_dump()`:
        - `name`

    """

    name: str = "route_timing_created"
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

    `name`: str = "route_timings_persisted"

    Attrs:
        `method_path`: MethodPath

    Exclude on `model_dump()`:
        - `name`

    """

    name: str = "route_timings_persisted"
    method_path: MethodPath


class NewUserCreated(BaseEvent):
    """A new user has signed up and been created in the database.

    `name`: str = "new_user_created"

    Attrs:
        `email`: str, new user's email
        `name`: str, new user's name

    Exclude on `model_dump()`:
        - `name`

    """

    name: str = "new_user_created"
    email: EmailStr
    user_name: str


class PasswordResetRequested(BaseEvent):
    """A visitor has passed authentication as an existing user
     and requested a password reset url be sent to their email.

    `name`: str = "password_reset_requested"

    Attrs:
        `email`: str, the user's email
        `name`: str, the user's name
        `url`: str, the password reset link

    Exclude on `model_dump()`:
        - `name`

    """

    name: str = "password_reset_requested"
    email: EmailStr
    user_name: str
    url: str


class UserLoggedIn(BaseEvent):
    """An existing user has logged in.

    `name`: str = "user_logged_in"

    Attrs:
        `user_id`: int, user's id
        `name`: str, user's name

    Exclude on `model_dump()`:
        - `name`

    """

    # TODO this can capture user_agent, ip address etc as needed for analysis
    name: str = "user_logged_in"
    user_id: int
    user_name: str


class UserActivity(BaseEvent):
    """A user has completed some action on the app.

    General purpose by intention, to be peppered in path operation funcs as needed.

    Utilises BaseEvent created_at attr as the activity timestamp.

    `name`: str = "user_activity"

    Attrs:
        `user_id`: int, user's id

    Exclude on `model_dump()`:
        - `name`

    """

    name: str = "user_activity"
    user_id: int


class ExceptionRaisedInfo(BaseExceptionEvent):


    name: str = "exc_raised_info"
    exc_msg: str | None = None
    exc_type: str | None = None
    user_id: int | None = ModuleNotFoundError



class ExceptionRaisedWarn(BaseExceptionEvent):
    name: str = "exc_raised_warn"
    exc_msg: str | None = None
    exc_type: str | None = None
    user_id: int | None = ModuleNotFoundError



class ExceptionRaisedError(BaseExceptionEvent):
    """An exception has been raised in the application for which the
    INFO level is appropriate.

    Utilise BaseExceptionEvent.

    Attrs:
        exc_msg: str, the exception message captured in the except block
        exc_type: exceptions.NinePanelsBaseException, the type of exception, get with `type(e)`
        user_id: int, optional id of user if available

    """
    name: str = "exc_raised_error"
    exc_msg: str | None = None
    exc_type: str | None = None
    user_id: int | None = ModuleNotFoundError
