import uuid

from datetime import datetime
from pydantic import BaseModel
from pydantic import Field
from typing import NewType

MethodPath = NewType('MethodPath', str)

class Event(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RouteTimingCreated(Event):
    """ A RouteTimer has completed a measurement in RouteTimingMiddleware

    type: str = 'route_timing_created'

    Attrs:
        request_id: str
        method_path: str
        method: str
        path: str
        start_ts: datetime
        stop_ts: datetime
        diff_ms: float | int = Field(ge=0)

    Exclude on `model_dump()`:
        - `type`

    """
    type: str = 'route_timing_created'
    request_id: str
    method_path: MethodPath
    method: str
    path: str
    start_ts: datetime
    stop_ts: datetime
    diff_ms: float | int = Field(ge=0)

class RouteTimingsPersisted(Event):
    """ A batch of route timing events for a `method_path`
    have been persisted to the db.

    type: str = 'route_timings_persisted'

    Attrs:
        method_path: MethodPath

    Exclude on `model_dump()`:
        - `type`

    """
    type: str = 'route_timings_persisted'
    method_path: MethodPath
