import uuid

from datetime import datetime
from pydantic import BaseModel
from pydantic import Field

class Event(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RouteTimingCreated(Event):
    """ A RouteTimer has completed a measurement in RouteTimingMiddleware

    Exclude on `model_dump()`:
        - `type`

    """
    type: str = 'timing_created'
    request_id: str
    method_path: str
    method: str
    path: str
    start_ts: datetime
    stop_ts: datetime
    diff_ms: float | int = Field(ge=0)

class RouteTimingsPersisted(Event):
    """ A batch of route timing events have been persisted to the db.

    Exclude on `model_dump()`:
        - `type`

    """
    type: str = 'timings_persisted'

    # TODO will need to rethink stats calculation again to accomodate this buffer. right architecture. implement.